#!/usr/bin/env python3
"""
SQS DNS Batch Worker for AWS Fargate

Processes DNS operations from SQS in batches for efficiency.
Handles Route53 operations and GitHub Actions triggers.

Note: SSL certificates are retained on domain deactivation (RemovalPolicy.RETAIN)
to prevent CloudFormation export dependency issues. Orphaned certificates can be
manually cleaned up via AWS Console or automated cleanup Lambda.
"""

import base64
import json
import logging
import os
import time
from collections import defaultdict
from typing import Any, Dict, List, Set

import boto3
import psycopg2
import requests
from botocore.exceptions import ClientError, NoCredentialsError

# Import domain helper functions
from domain_helpers import get_tenant_for_domain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
        github_token: str = None,
        repo: str = None,
        environment: str = None,
        max_messages: int = 10,
        wait_time_seconds: int = 20,
        batch_timeout: int = 30,
    ):
        """
        Initialize SQS DNS worker.

        Args:
            queue_url: SQS queue URL for DNS operations
            region_name: AWS region (uses IAM role for authentication)
            github_token: GitHub personal access token
            repo: GitHub repository (e.g., "AITeeToolkit/aws-fargate-cdk")
            max_messages: Maximum messages to receive per poll (1-10)
            wait_time_seconds: Long polling wait time (0-20 seconds)
            batch_timeout: Seconds to wait before processing incomplete batch
        """
        self.queue_url = queue_url or os.environ.get("SQS_DNS_OPERATIONS_QUEUE_URL")
        self.region_name = region_name or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        # Use IAM role for AWS authentication (no explicit credentials needed)
        self.aws_access_key_id = None
        self.aws_secret_access_key = None
        self.github_token = github_token or os.environ.get("GH_TOKEN")
        self.repo = repo or os.environ.get("REPO", "AITeeToolkit/aws-fargate-cdk")
        self.environment = environment or os.environ.get("ENVIRONMENT", "dev")

        self.max_messages = min(max_messages, 10)  # SQS limit is 10
        self.wait_time_seconds = min(wait_time_seconds, 20)  # SQS limit is 20
        self.batch_timeout = batch_timeout

        if not self.queue_url:
            raise ValueError("SQS_DNS_OPERATIONS_QUEUE_URL must be configured")
        if not self.github_token:
            raise ValueError("GH_TOKEN must be configured")

        self.sqs_client = None
        self.route53_client = None
        self.db_connection = None
        self.running = False

        # Batch processing state
        self.pending_domains = set()
        self.pending_deactivations = set()
        self.domain_info_map = {}  # Store full domain info from SNS messages
        self.last_batch_time = time.time()

        # Statistics
        self.stats = {
            "messages_processed": 0,
            "batches_processed": 0,
            "domains_processed": 0,
            "hosted_zones_created": 0,
            "hosted_zones_deleted": 0,
            "github_triggers": 0,
            "start_time": None,
        }

    def connect(self) -> bool:
        """
        Connect to AWS services and database.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create AWS clients
            session_kwargs = {"region_name": self.region_name}

            if self.aws_access_key_id and self.aws_secret_access_key:
                session_kwargs.update(
                    {
                        "aws_access_key_id": self.aws_access_key_id,
                        "aws_secret_access_key": self.aws_secret_access_key,
                    }
                )

            self.sqs_client = boto3.client("sqs", **session_kwargs)
            self.route53_client = boto3.client("route53", **session_kwargs)

            logger.info(f"Connected to AWS services in region {self.region_name}")

            # Connect to database
            try:
                self.db_connection = psycopg2.connect(
                    host=os.environ["PGHOST"],
                    user=os.environ["PGUSER"],
                    password=os.environ["PGPASSWORD"],
                    dbname=os.environ["PGDATABASE"],
                    port=os.environ.get("PGPORT", "5432"),
                )
                logger.info("✅ Database connection established")
            except Exception as e:
                logger.error(f"❌ Failed to connect to database: {e}")
                return False

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
                MessageAttributeNames=["All"],
            )

            messages = response.get("Messages", [])
            if messages:
                logger.debug(f"Received {len(messages)} messages from SQS")

            return messages

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            logger.error(f"Error receiving messages from SQS: {error_code} - {e}")
            return []

            logger.error(f"Unexpected error receiving messages: {e}")
            return []

    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process a single SQS message containing SNS notification with domain data.

        Expected SNS message format:
        {
            "full_url": "example.com",
            "tenant_id": "uuid-here",
            "active_status": "Y",
            "hosted_zone_id": 123  // optional
        }

        Args:
            message: SQS message dict (containing SNS notification)

        Returns:
            bool: True if message should be deleted from queue, False to retry
        """
        try:
            # Parse SQS message body
            message_body = message.get("Body", "{}")
            message_data = json.loads(message_body)

            # SNS wraps the actual message in a 'Message' field
            if "Message" in message_data:
                domain_data = json.loads(message_data["Message"])
            else:
                # Fallback for direct SQS messages (backward compatibility)
                domain_data = message_data

            # Validate required fields
            required_fields = [
                "full_url",
                "tenant_id",
                "active_status",
                "hosted_zone_id",
            ]
            missing_fields = [f for f in required_fields if f not in domain_data]

            if missing_fields:
                logger.error(
                    f"❌ Invalid SNS message - missing required fields: {missing_fields}. "
                    f"Message: {domain_data}"
                )
                return False  # Delete invalid message, don't retry

            # Extract domain data
            domain_name = domain_data["full_url"]
            tenant_id = domain_data["tenant_id"]
            active = domain_data["active_status"]
            hosted_zone_id = domain_data["hosted_zone_id"]

            if active not in ("Y", "N"):
                logger.error(f"❌ Invalid active_status: {active}. Must be 'Y' or 'N'")
                return False  # Delete invalid message

            logger.info(
                f"📨 Processing domain change: {domain_name} "
                f"(active={active}, tenant={tenant_id})"
            )

            # Store domain data for batch processing
            domain_info = {
                "full_url": domain_name,
                "tenant_id": tenant_id,
                "active_status": active,
                "hosted_zone_id": hosted_zone_id,
            }

            # Add to appropriate pending batch
            if active == "Y":
                self.pending_domains.add(domain_name)
                # Store full domain info for processing
                if not hasattr(self, "domain_info_map"):
                    self.domain_info_map = {}
                self.domain_info_map[domain_name] = domain_info
                # Remove from deactivations if it was there
                self.pending_deactivations.discard(domain_name)
            elif active == "N":
                self.pending_deactivations.add(domain_name)
                # Remove from activations if it was there
                self.pending_domains.discard(domain_name)
                if hasattr(self, "domain_info_map"):
                    self.domain_info_map.pop(domain_name, None)

            self.stats["messages_processed"] += 1

            # Message processed successfully, can be deleted from queue
            return True

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse message JSON: {e}")
            return False  # Invalid JSON, don't retry

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return True  # Retry on unexpected errors

    def delete_message(self, receipt_handle: str) -> bool:
        """
        Delete a message from SQS queue.

        Args:
            receipt_handle: SQS message receipt handle

        Returns:
            bool: True if message deleted successfully, False otherwise
        """
        try:
            self.sqs_client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
            logger.debug("Message deleted from SQS queue")
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            logger.error(f"Error deleting SQS message: {error_code} - {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error deleting message: {e}")
            return False

    def fetch_active_domains_from_db(self) -> List[str]:
        """
        Fetch active domains from database.

        Returns:
            list: List of active domain names
        """
        try:
            cur = self.db_connection.cursor()
            cur.execute("SELECT DISTINCT full_url FROM domains WHERE active_status = 'Y';")
            result = [row[0] for row in cur.fetchall()]
            cur.close()
            logger.info(f"🌐 Fetched {len(result)} active domains from database")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to fetch active domains from database: {e}")
            return []

    def update_domain_activation(self, domain_name: str) -> bool:
        """
        Update domains table to mark domain as active with tenant information from SNS message.

        Args:
            domain_name: Domain to activate

        Returns:
            bool: True if updated successfully
        """
        try:
            # Get domain info from SNS message
            domain_info = self.domain_info_map.get(domain_name)

            if not domain_info:
                logger.error(f"❌ No domain info found for {domain_name} in SNS message data")
                return False

            tenant_id = domain_info["tenant_id"]
            hosted_zone_id = domain_info.get("hosted_zone_id")

            # Update domains table to mark as active (hosted_zone_id will be NULL initially)
            with self.db_connection.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO domains (full_url, tenant_id, active_status, activation_date)
                    VALUES (%s, %s, 'Y', CURRENT_DATE)
                    ON CONFLICT (full_url) DO UPDATE SET
                        tenant_id = EXCLUDED.tenant_id,
                        active_status = 'Y',
                        activation_date = CURRENT_DATE
                    """,
                    (domain_name, tenant_id),
                )
                self.db_connection.commit()

            logger.info(f"✅ Domain {domain_name} marked as active for tenant {tenant_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update domain activation for {domain_name}: {e}")
            self.db_connection.rollback()
            return False

    def update_domain_deactivation(self, domain_name: str) -> bool:
        """
        Update domains table to mark domain as inactive.

        Args:
            domain_name: Domain to deactivate

        Returns:
            bool: True if updated successfully
        """
        try:
            # Test connection and reconnect if needed
            try:
                with self.db_connection.cursor() as test_cur:
                    test_cur.execute("SELECT 1")
                    test_cur.fetchone()
            except Exception:
                logger.warning("⚠️ Database connection lost, reconnecting...")
                self.db_connection = psycopg2.connect(
                    host=os.environ["PGHOST"],
                    user=os.environ["PGUSER"],
                    password=os.environ["PGPASSWORD"],
                    dbname=os.environ["PGDATABASE"],
                    port=os.environ.get("PGPORT", "5432"),
                )
                logger.info("✅ Database connection restored")

            # Update domains table to mark as inactive with inactivation date
            with self.db_connection.cursor() as cur:
                cur.execute(
                    "UPDATE domains SET active_status = 'N', inactivation_date = CURRENT_DATE WHERE full_url = %s",
                    (domain_name,),
                )
                self.db_connection.commit()

            logger.info(f"✅ Domain {domain_name} marked as inactive in database")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update domain deactivation for {domain_name}: {e}")
            try:
                self.db_connection.rollback()
            except:
                pass  # Connection might be dead
            return False

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
                existing_zone = next(
                    (zone for zone in hosted_zones if zone["Name"] == f"{domain}."),
                    None,
                )

                if existing_zone:
                    logger.info(
                        f"🔍 Hosted zone already exists for {domain}: {existing_zone['Id']}"
                    )
                    continue

                # Create hosted zone if it doesn't exist
                caller_reference = f"{domain}-{int(time.time())}"
                response = self.route53_client.create_hosted_zone(
                    Name=domain,
                    CallerReference=caller_reference,
                    HostedZoneConfig={
                        "Comment": f"Auto-created by SQS DNS worker for {domain}",
                        "PrivateZone": False,
                    },
                )

                zone_id = response["HostedZone"]["Id"]
                created_zones.append(domain)
                self.stats["hosted_zones_created"] += 1
                logger.info(f"✅ Created hosted zone for {domain}: {zone_id}")

            except Exception as e:
                logger.error(f"❌ Failed to create hosted zone for {domain}: {e}")

        return created_zones

    def delete_hosted_zones(self, domains: List[str]) -> List[str]:
        """
        Delete hosted zones for deactivated domains.

        Args:
            domains: List of domain names to delete hosted zones for

        Returns:
            list: List of domains for which zones were deleted
        """
        deleted_zones = []

        for domain in domains:
            try:
                # Find the hosted zone
                response = self.route53_client.list_hosted_zones_by_name(DNSName=domain)
                hosted_zones = response.get("HostedZones", [])
                zone = next((z for z in hosted_zones if z["Name"] == f"{domain}."), None)

                if not zone:
                    logger.warning(f"⚠️ No hosted zone found for {domain}, nothing to delete")
                    continue

                zone_id = zone["Id"].split("/")[-1]  # Clean zone ID

                # Get all record sets
                record_sets = self.route53_client.list_resource_record_sets(HostedZoneId=zone_id)

                changes = []
                for record in record_sets["ResourceRecordSets"]:
                    record_type = record["Type"]
                    record_name = record["Name"]

                    if record_type in ["A", "MX", "TXT", "CNAME"]:
                        logger.info(f"🗑️ Scheduling deletion for {record_type} record {record_name}")
                        changes.append({"Action": "DELETE", "ResourceRecordSet": record})

                # Batch delete records (skip SOA/NS, they are required for the zone)
                if changes:
                    self.route53_client.change_resource_record_sets(
                        HostedZoneId=zone_id, ChangeBatch={"Changes": changes}
                    )
                    logger.info(f"✅ Deleted {len(changes)} records from zone {zone_id} ({domain})")

                # Delete the hosted zone itself
                # TODO: Temporarily disabled - keeping hosted zones but deleting records
                # self.route53_client.delete_hosted_zone(Id=zone_id)
                # deleted_zones.append(domain)
                # self.stats['hosted_zones_deleted'] += 1
                # logger.info(f"✅ Deleted hosted zone {zone_id} for {domain}")
                logger.info(
                    f"⚠️ Skipped hosted zone deletion for {domain} (zone_id: {zone_id}) - only deleted records"
                )

            except Exception as e:
                logger.error(f"❌ Failed to delete hosted zone for {domain}: {e}")

        return deleted_zones

    def trigger_github_workflow(self, domains: List[str]) -> bool:
        """
        Trigger GitHub workflow via repository dispatch API.
        Infrastructure will read active domains directly from database.

        Args:
            domains: List of active domains (for logging only)

        Returns:
            bool: True if triggered successfully
        """
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

            # Trigger workflow via repository dispatch
            url = f"https://api.github.com/repos/{self.repo}/dispatches"
            payload = {
                "event_type": "domain-update",
                "client_payload": {
                    "environment": self.environment,
                    "domain_count": len(domains),
                    "triggered_at": time.time(),
                    "skip_tests": True,  # Domain updates don't need tests
                },
            }

            r = requests.post(url, headers=headers, json=payload)
            r.raise_for_status()

            self.stats["github_triggers"] += 1
            logger.info(
                f"✅ Triggered GitHub workflow for {self.environment} environment with {len(domains)} domains"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to trigger GitHub workflow: {e}")
            return False

    def process_batch(self) -> bool:
        """
        Process the current batch of pending domains.
        Handles both activations and deactivations, then fetches ALL active domains.

        Returns:
            bool: True if batch processed successfully
        """
        if not self.pending_domains and not self.pending_deactivations:
            return True

        pending_activations = len(self.pending_domains)
        pending_deactivations = len(self.pending_deactivations)
        logger.info(
            f"🔄 Processing batch: {pending_activations} activations, {pending_deactivations} deactivations"
        )

        try:
            successful_operations = False

            # Step 1: Process deactivations first
            if self.pending_deactivations:
                for domain in self.pending_deactivations:
                    # Update database first
                    db_success = self.update_domain_deactivation(domain)
                    if db_success:
                        successful_operations = True
                        # Only delete hosted zone if database update succeeded
                        deleted_zones = self.delete_hosted_zones([domain])
                        if deleted_zones:
                            logger.info(f"✅ Atomically deactivated domain: {domain}")
                        else:
                            logger.warning(
                                f"⚠️ Database updated but hosted zone deletion failed for: {domain}"
                            )
                    else:
                        logger.error(f"❌ Failed to deactivate domain in database: {domain}")

            # Step 2: Process activations
            if self.pending_domains:
                for domain in self.pending_domains:
                    # Update database first
                    db_success = self.update_domain_activation(domain)
                    if db_success:
                        successful_operations = True
                        # Only create hosted zone if database update succeeded
                        created_zones = self.ensure_hosted_zones([domain])
                        if created_zones:
                            logger.info(f"✅ Atomically activated domain: {domain}")
                        else:
                            logger.warning(
                                f"⚠️ Database updated but hosted zone creation failed for: {domain}"
                            )
                    else:
                        logger.error(f"❌ Failed to activate domain in database: {domain}")

            # Step 3: Only trigger workflow if there were successful database operations
            if not successful_operations:
                logger.warning("⚠️ No successful operations in batch - skipping workflow trigger")
                # Clear pending domains even on failure to avoid retry loops
                self.pending_domains.clear()
                self.pending_deactivations.clear()
                return False

            # Step 4: Fetch ALL active domains from database (reflects current state)
            all_active_domains = self.fetch_active_domains_from_db()

            # Step 5: Trigger GitHub workflow
            # CDK will read active domains from database and automatically remove stacks
            # for deactivated domains (CloudFormation handles deletion)
            if self.trigger_github_workflow(all_active_domains):
                self.stats["batches_processed"] += 1
                self.stats["domains_processed"] += len(all_active_domains)
                logger.info(
                    f"✅ Successfully processed batch: {len(all_active_domains)} total active domains"
                )

                # Clear pending domains (batch complete)
                self.pending_domains.clear()
                self.pending_deactivations.clear()
                self.last_batch_time = time.time()
                return True
            else:
                logger.error(f"❌ Failed to process batch of {len(all_active_domains)} domains")
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
        if not self.pending_domains and not self.pending_deactivations:
            return False

        # Process if we have pending changes and timeout has elapsed
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
        self.stats["start_time"] = time.time()

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
        """Stop the worker and cleanup connections."""
        self.running = False
        logger.info("Stop signal sent to SQS DNS worker")

        # Close database connection
        if self.db_connection:
            try:
                self.db_connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")

    def print_stats(self):
        """Print worker statistics."""
        stats = self.get_stats()
        logger.info("=== SQS DNS Worker Statistics ===")
        logger.info(f"Messages processed: {stats['messages_processed']}")
        logger.info(f"Batches processed: {stats['batches_processed']}")
        logger.info(f"Domains processed: {stats['domains_processed']}")
        logger.info(f"Hosted zones created: {stats['hosted_zones_created']}")
        logger.info(f"Hosted zones deleted: {stats['hosted_zones_deleted']}")
        logger.info(f"GitHub triggers: {stats['github_triggers']}")
        if stats.get("uptime_seconds"):
            logger.info(f"Uptime: {stats['uptime_seconds']:.1f} seconds")
        logger.info("================================")

    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        stats = self.stats.copy()
        if stats["start_time"]:
            stats["uptime_seconds"] = time.time() - stats["start_time"]
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
