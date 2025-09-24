#!/usr/bin/env python3
"""
SQS DNS Batch Worker for AWS Fargate

Processes DNS operations from SQS in batches for efficiency.
Handles Route53 operations and GitHub Actions triggers.
"""

import json
import logging
import os
import time
import boto3
import requests
import base64
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Any, List, Set
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class SQSDNSWorker:
    """
    SQS DNS Worker that processes DNS operations in batches.
    """
    
    def __init__(
        self,
        queue_url: str = None,
        region_name: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        github_token: str = None,
        repo: str = None,
        max_messages: int = 10,
        wait_time_seconds: int = 20,
        batch_timeout: int = 30
    ):
        """
        Initialize SQS DNS worker.
        
        Args:
            queue_url: SQS queue URL to consume from
            region_name: AWS region
            aws_access_key_id: AWS access key (optional, uses IAM role if not provided)
            aws_secret_access_key: AWS secret key (optional, uses IAM role if not provided)
            github_token: GitHub personal access token
            repo: GitHub repository (e.g., "AITeeToolkit/aws-fargate-cdk")
            max_messages: Maximum messages to receive per poll (1-10)
            wait_time_seconds: Long polling wait time (0-20 seconds)
            batch_timeout: Seconds to wait before processing incomplete batch
        """
        self.queue_url = queue_url or os.environ.get('SQS_DNS_OPERATIONS_QUEUE_URL')
        self.region_name = region_name or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        self.aws_access_key_id = aws_access_key_id or os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.github_token = github_token or os.environ.get('GH_TOKEN')
        self.repo = repo or os.environ.get('REPO', 'AITeeToolkit/aws-fargate-cdk')
        
        self.max_messages = min(max_messages, 10)  # SQS limit is 10
        self.wait_time_seconds = min(wait_time_seconds, 20)  # SQS limit is 20
        self.batch_timeout = batch_timeout
        
        if not self.queue_url:
            raise ValueError("SQS_DNS_QUEUE_URL must be configured")
        if not self.github_token:
            raise ValueError("GH_TOKEN must be configured")
        
        self.sqs_client = None
        self.route53_client = None
        self.running = False
        
        # Batch processing state
        self.pending_domains = set()
        self.last_batch_time = time.time()
        
        # Statistics
        self.stats = {
            'messages_processed': 0,
            'batches_processed': 0,
            'domains_processed': 0,
            'hosted_zones_created': 0,
            'github_triggers': 0,
            'start_time': None
        }
    
    def connect(self) -> bool:
        """
        Connect to AWS services.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create AWS clients
            session_kwargs = {'region_name': self.region_name}
            
            if self.aws_access_key_id and self.aws_secret_access_key:
                session_kwargs.update({
                    'aws_access_key_id': self.aws_access_key_id,
                    'aws_secret_access_key': self.aws_secret_access_key
                })
            
            self.sqs_client = boto3.client('sqs', **session_kwargs)
            self.route53_client = boto3.client('route53', **session_kwargs)
            
            logger.info(f"Connected to AWS services in region {self.region_name}")
            return True
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Configure IAM role or environment variables.")
            return False
            
        except Exception as e:
            logger.error(f"Failed to connect to AWS services: {e}")
            return False
    
    def receive_messages(self) -> List[Dict[str, Any]]:
        """
        Receive messages from SQS queue.
        
        Returns:
            list: List of messages received from SQS
        """
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=self.max_messages,
                WaitTimeSeconds=self.wait_time_seconds,
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            if messages:
                logger.debug(f"Received {len(messages)} messages from SQS")
            
            return messages
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Error receiving messages from SQS: {error_code} - {e}")
            return []
            
        except Exception as e:
            logger.error(f"Unexpected error receiving messages: {e}")
            return []
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process a single SQS message and add to batch.
        
        Args:
            message: SQS message dictionary
            
        Returns:
            bool: True if message processed successfully, False otherwise
        """
        try:
            # Extract message body
            body = message.get('Body', '{}')
            message_data = json.loads(body)
            
            # Extract message attributes for logging
            message_id = message.get('MessageId', 'unknown')
            
            domain_name = message_data.get('domain_name')
            active = message_data.get('active')
            operation_type = message_data.get('operation_type')
            
            if not domain_name or active not in ('Y', 'N'):
                logger.error(f"Invalid message data: {message_data}")
                return False
            
            logger.info(f"Processing DNS message {message_id}: {domain_name} (active={active})")
            
            # Add to pending batch
            self.pending_domains.add(domain_name)
            self.stats['messages_processed'] += 1
            
            # Delete message from queue (we've successfully added it to batch)
            self.delete_message(message.get('ReceiptHandle'))
            
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in SQS message: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Error processing SQS message: {e}")
            return False
    
    def delete_message(self, receipt_handle: str) -> bool:
        """
        Delete a message from the SQS queue.
        
        Args:
            receipt_handle: SQS message receipt handle
            
        Returns:
            bool: True if message deleted successfully, False otherwise
        """
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.debug("Message deleted from SQS queue")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Error deleting SQS message: {error_code} - {e}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error deleting message: {e}")
            return False
    
    def fetch_active_domains_from_db(self) -> List[str]:
        """
        Fetch active domains from database.
        This would need to be implemented based on your database connection.
        For now, we'll use the pending domains as a proxy.
        
        Returns:
            list: List of active domain names
        """
        # TODO: Implement actual database connection
        # For now, return the pending domains
        return list(self.pending_domains)
    
    def ensure_hosted_zones(self, domains: List[str]) -> List[str]:
        """
        Ensure hosted zones exist for all domains.
        
        Args:
            domains: List of domain names
            
        Returns:
            list: List of domains for which zones were created
        """
        created_zones = []
        
        for domain in domains:
            try:
                # Check if hosted zone exists
                response = self.route53_client.list_hosted_zones_by_name(DNSName=domain)
                hosted_zones = response.get("HostedZones", [])
                
                # Check if zone exists for this exact domain
                existing_zone = next((zone for zone in hosted_zones if zone["Name"] == f"{domain}."), None)
                
                if existing_zone:
                    logger.info(f"🔍 Hosted zone already exists for {domain}: {existing_zone['Id']}")
                    continue
                
                # Create hosted zone if it doesn't exist
                caller_reference = f"{domain}-{int(time.time())}"
                response = self.route53_client.create_hosted_zone(
                    Name=domain,
                    CallerReference=caller_reference,
                    HostedZoneConfig={
                        "Comment": f"Auto-created by SQS DNS worker for {domain}",
                        "PrivateZone": False
                    }
                )
                
                zone_id = response["HostedZone"]["Id"]
                created_zones.append(domain)
                self.stats['hosted_zones_created'] += 1
                logger.info(f"✅ Created hosted zone for {domain}: {zone_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to create hosted zone for {domain}: {e}")
        
        return created_zones
    
    def trigger_github_workflow(self, domains: List[str]) -> bool:
        """
        Trigger GitHub Actions workflow with domain list.
        
        Args:
            domains: List of active domains
            
        Returns:
            bool: True if triggered successfully
        """
        try:
            branch_name = "domain-updates"
            domains_content = json.dumps({"domains": domains}, indent=2)
            headers = {"Authorization": f"token {self.github_token}"}
            
            # Get latest commit SHA from main
            url = f"https://api.github.com/repos/{self.repo}/git/refs/heads/main"
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            main_sha = r.json()["object"]["sha"]
            
            # Ensure branch exists
            url = f"https://api.github.com/repos/{self.repo}/git/refs/heads/{branch_name}"
            r = requests.get(url, headers=headers)
            if r.status_code == 404:
                logger.info(f"🌱 Creating branch '{branch_name}' from main")
                url = f"https://api.github.com/repos/{self.repo}/git/refs"
                payload = {"ref": f"refs/heads/{branch_name}", "sha": main_sha}
                r = requests.post(url, headers=headers, json=payload)
                r.raise_for_status()
            
            # Get existing file SHA
            url = f"https://api.github.com/repos/{self.repo}/contents/domains.json"
            params = {"ref": branch_name}
            r = requests.get(url, headers=headers, params=params)
            file_sha = r.json()["sha"] if r.status_code == 200 else None
            
            # Update file
            content_b64 = base64.b64encode(domains_content.encode()).decode()
            payload = {
                "message": f"Update domains.json with {len(domains)} active domains (SQS batch)",
                "content": content_b64,
                "branch": branch_name
            }
            if file_sha:
                payload["sha"] = file_sha
            
            url = f"https://api.github.com/repos/{self.repo}/contents/domains.json"
            r = requests.put(url, headers=headers, json=payload)
            r.raise_for_status()
            
            self.stats['github_triggers'] += 1
            logger.info(f"✅ Triggered GitHub workflow with {len(domains)} domains")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to trigger GitHub workflow: {e}")
            return False
    
    def process_batch(self) -> bool:
        """
        Process the current batch of pending domains.
        
        Returns:
            bool: True if batch processed successfully
        """
        if not self.pending_domains:
            return True
        
        domains = list(self.pending_domains)
        logger.info(f"🔄 Processing batch of {len(domains)} domains: {domains}")
        
        try:
            # Step 1: Ensure hosted zones exist
            created_zones = self.ensure_hosted_zones(domains)
            if created_zones:
                logger.info(f"⏳ Waiting 15s for {len(created_zones)} hosted zone(s) to propagate...")
                time.sleep(15)
            
            # Step 2: Trigger GitHub workflow
            success = self.trigger_github_workflow(domains)
            
            if success:
                self.stats['batches_processed'] += 1
                self.stats['domains_processed'] += len(domains)
                logger.info(f"✅ Successfully processed batch of {len(domains)} domains")
                
                # Clear pending domains
                self.pending_domains.clear()
                self.last_batch_time = time.time()
                return True
            else:
                logger.error(f"❌ Failed to process batch of {len(domains)} domains")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing batch: {e}")
            return False
    
    def should_process_batch(self) -> bool:
        """
        Determine if we should process the current batch.
        
        Returns:
            bool: True if batch should be processed now
        """
        if not self.pending_domains:
            return False
        
        # Process if we have pending domains and timeout has elapsed
        time_since_last_batch = time.time() - self.last_batch_time
        return time_since_last_batch >= self.batch_timeout
    
    def run(self):
        """
        Start the SQS DNS worker main loop.
        """
        if not self.connect():
            logger.error("Failed to connect to AWS services. Exiting.")
            return
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        logger.info("🚀 SQS DNS Worker started. Processing DNS operations in batches...")
        
        try:
            while self.running:
                try:
                    # Receive messages from SQS
                    messages = self.receive_messages()
                    
                    # Process each message (add to batch)
                    for message in messages:
                        try:
                            self.process_message(message)
                        except Exception as e:
                            logger.error(f"Error processing individual message: {e}")
                            continue
                    
                    # Check if we should process the batch
                    if self.should_process_batch():
                        self.process_batch()
                
                except KeyboardInterrupt:
                    logger.info("Received interrupt signal. Processing final batch...")
                    if self.pending_domains:
                        self.process_batch()
                    break
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(5)  # Brief pause before retrying
                    continue
        
        finally:
            self.running = False
            logger.info("🛑 SQS DNS Worker stopped")
            self.print_stats()
    
    def stop(self):
        """Stop the worker."""
        self.running = False
        logger.info("Stop signal sent to SQS DNS worker")
    
    def print_stats(self):
        """Print worker statistics."""
        stats = self.get_stats()
        logger.info("=== SQS DNS Worker Statistics ===")
        logger.info(f"Messages processed: {stats['messages_processed']}")
        logger.info(f"Batches processed: {stats['batches_processed']}")
        logger.info(f"Domains processed: {stats['domains_processed']}")
        logger.info(f"Hosted zones created: {stats['hosted_zones_created']}")
        logger.info(f"GitHub triggers: {stats['github_triggers']}")
        if stats.get('uptime_seconds'):
            logger.info(f"Uptime: {stats['uptime_seconds']:.1f} seconds")
        logger.info("================================")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        stats = self.stats.copy()
        if stats['start_time']:
            stats['uptime_seconds'] = time.time() - stats['start_time']
        return stats


def main():
    """Main entry point for SQS DNS worker."""
    worker = SQSDNSWorker()
    
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        worker.stop()


if __name__ == "__main__":
    main()
