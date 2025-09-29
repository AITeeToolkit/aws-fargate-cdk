#!/usr/bin/env python3
"""
SQS DNS Batch Worker for AWS Fargate

Processes DNS operations from SQS in batches for efficiency.
Handles Route53 operations and GitHub Actions triggers.
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
        self.region_name = region_name or os.environ.get(
            "AWS_DEFAULT_REGION", "us-east-1"
        )
        # Use IAM role for AWS authentication (no explicit credentials needed)
        self.aws_access_key_id = None
        self.aws_secret_access_key = None
        self.github_token = github_token or os.environ.get("GH_TOKEN")
        self.repo = repo or os.environ.get("REPO", "AITeeToolkit/aws-fargate-cdk")

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
            logger.error(
                "AWS credentials not found. Configure IAM role or environment variables."
            )
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
            body = message.get("Body", "{}")
            message_data = json.loads(body)

            # Extract message attributes for logging
            message_id = message.get("MessageId", "unknown")

            domain_name = message_data.get("domain_name")
            active = message_data.get("active")

            if not domain_name or active not in ("Y", "N"):
                logger.error(f"Invalid message data: {message_data}")
                return False

            logger.info(f"📨 Processing domain change: {domain_name} (active={active})")

            # Add to appropriate pending batch
            if active == "Y":
                self.pending_domains.add(domain_name)
                # Remove from deactivations if it was there
                self.pending_deactivations.discard(domain_name)
            elif active == "N":
                self.pending_deactivations.add(domain_name)
                # Remove from activations if it was there
                self.pending_domains.discard(domain_name)

            self.stats["messages_processed"] += 1

            # Delete message from queue (we've successfully added it to batch)
            self.delete_message(message.get("ReceiptHandle"))

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
                QueueUrl=self.queue_url, ReceiptHandle=receipt_handle
            )
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
            cur.execute(
                "SELECT DISTINCT full_url FROM purchased_domains WHERE active_domain = 'Y';"
            )
            result = [row[0] for row in cur.fetchall()]
            cur.close()
            logger.info(f"🌐 Fetched {len(result)} active domains from database")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to fetch active domains from database: {e}")
            return []

    def update_domain_activation(self, domain_name: str) -> bool:
        """
        Update domains table to mark domain as active with tenant information.

        Args:
            domain_name: Domain to activate

        Returns:
            bool: True if updated successfully
        """
        try:
            # Get tenant information
            tenant_id = get_tenant_for_domain(self.db_connection, domain_name)

            if not tenant_id:
                logger.warning(
                    f"⚠️ Domain {domain_name} activation requested but no tenant found in purchased_domains"
                )
                return False

            # Update domains table to mark as active
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

            logger.info(
                f"✅ Domain {domain_name} marked as active for tenant {tenant_id}"
            )
            return True

        except Exception as e:
            logger.error(
                f"❌ Failed to update domain activation for {domain_name}: {e}"
            )
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

            # Update domains table to mark as inactive
            with self.db_connection.cursor() as cur:
                cur.execute(
                    "UPDATE domains SET active_status = 'N' WHERE full_url = %s",
                    (domain_name,),
                )
                self.db_connection.commit()

            logger.info(f"✅ Domain {domain_name} marked as inactive in database")
            return True

        except Exception as e:
            logger.error(
                f"❌ Failed to update domain deactivation for {domain_name}: {e}"
            )
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
                zone = next(
                    (z for z in hosted_zones if z["Name"] == f"{domain}."), None
                )

                if not zone:
                    logger.warning(
                        f"⚠️ No hosted zone found for {domain}, nothing to delete"
                    )
                    continue

                zone_id = zone["Id"].split("/")[-1]  # Clean zone ID

                # Get all record sets
                record_sets = self.route53_client.list_resource_record_sets(
                    HostedZoneId=zone_id
                )

                changes = []
                for record in record_sets["ResourceRecordSets"]:
                    record_type = record["Type"]
                    record_name = record["Name"]

                    if record_type in ["A", "MX", "TXT", "CNAME"]:
                        logger.info(
                            f"🗑️ Scheduling deletion for {record_type} record {record_name}"
                        )
                        changes.append(
                            {"Action": "DELETE", "ResourceRecordSet": record}
                        )

                # Batch delete records (skip SOA/NS, they are required for the zone)
                if changes:
                    self.route53_client.change_resource_record_sets(
                        HostedZoneId=zone_id, ChangeBatch={"Changes": changes}
                    )
                    logger.info(
                        f"✅ Deleted {len(changes)} records from zone {zone_id} ({domain})"
                    )

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
            logger.info(f"Latest main SHA: {main_sha}")

            # Ensure domain-updates branch exists and is up to date with main
            try:
                # Check if branch exists
                url = f"https://api.github.com/repos/{self.repo}/git/refs/heads/{branch_name}"
                r = requests.get(url, headers=headers)

                if r.status_code == 404:
                    # Branch doesn't exist, create it from main
                    url = f"https://api.github.com/repos/{self.repo}/git/refs"
                    payload = {"ref": f"refs/heads/{branch_name}", "sha": main_sha}
                    r = requests.post(url, headers=headers, json=payload)
                    r.raise_for_status()
                    logger.info(f"✅ Created {branch_name} branch from latest main")
                else:
                    # Branch exists, update it to latest main
                    payload = {"sha": main_sha, "force": True}
                    r = requests.patch(url, headers=headers, json=payload)
                    r.raise_for_status()
                    logger.info(f"✅ Updated {branch_name} branch to latest main")
            except Exception as e:
                logger.warning(f"⚠️ Failed to update branch, continuing: {e}")

            # Now update domains.json on the updated branch
            # Get domains.json from the now-updated branch
            url = f"https://api.github.com/repos/{self.repo}/contents/domains.json"
            params = {"ref": branch_name}
            r = requests.get(url, headers=headers, params=params)
            file_sha = r.json().get("sha") if r.status_code == 200 else None

            # Update domains.json content
            content_b64 = base64.b64encode(domains_content.encode()).decode()
            payload = {
                "message": f"Update domains.json with {len(domains)} active domains",
                "content": content_b64,
                "branch": branch_name,
            }
            if file_sha:
                payload["sha"] = file_sha

            url = f"https://api.github.com/repos/{self.repo}/contents/domains.json"
            r = requests.put(url, headers=headers, json=payload)
            r.raise_for_status()

            self.stats["github_triggers"] += 1
            logger.info(f"✅ Triggered GitHub workflow with {len(domains)} domains")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to trigger GitHub workflow: {e}")
            return False

    def clear_cdk_context(self) -> bool:
        """
        Clear CDK context cache to force fresh hosted zone lookups.

        Returns:
            bool: True if context cleared successfully
        """
        try:
            headers = {"Authorization": f"token {self.github_token}"}

            # Get current cdk.context.json content from domain-updates branch
            url = f"https://api.github.com/repos/{self.repo}/contents/cdk.context.json"
            params = {"ref": "domain-updates"}
            r = requests.get(url, headers=headers, params=params)

            if r.status_code == 404:
                logger.info(
                    "📝 No cdk.context.json found on domain-updates branch, nothing to clear"
                )
                return True

            r.raise_for_status()
            file_info = r.json()

            # Create minimal context (keep availability zones, remove hosted zone cache)
            minimal_context = {
                "availability-zones:account=156041439702:region=us-east-1": [
                    "us-east-1a",
                    "us-east-1b",
                    "us-east-1c",
                    "us-east-1d",
                    "us-east-1e",
                    "us-east-1f",
                ]
            }

            # Update cdk.context.json with minimal context
            content_b64 = base64.b64encode(
                json.dumps(minimal_context, indent=2).encode()
            ).decode()

            payload = {
                "message": "Clear CDK context cache for fresh hosted zone lookups [skip ci]",
                "content": content_b64,
                "sha": file_info["sha"],
                "branch": "domain-updates",
            }

            # Retry logic for 409 conflicts
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    r = requests.put(url, headers=headers, json=payload)
                    r.raise_for_status()
                    logger.info(
                        "✅ Cleared CDK context cache for fresh hosted zone lookups"
                    )
                    return True

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 409 and attempt < max_retries - 1:
                        logger.warning(
                            f"⚠️ CDK context conflict (attempt {attempt + 1}/{max_retries}), retrying..."
                        )
                        # Get fresh SHA and retry
                        r_fresh = requests.get(url, headers=headers, params=params)
                        if r_fresh.status_code == 200:
                            payload["sha"] = r_fresh.json()["sha"]
                            continue
                    raise

            return False

        except Exception as e:
            logger.error(f"❌ Failed to clear CDK context: {e}")
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
            # Step 1: Handle domain deactivations atomically (database + hosted zones)
            if self.pending_deactivations:
                for domain in self.pending_deactivations:
                    # Update database first
                    db_success = self.update_domain_deactivation(domain)
                    if db_success:
                        # Only delete hosted zone if database update succeeded
                        deleted_zones = self.delete_hosted_zones([domain])
                        if deleted_zones:
                            logger.info(f"✅ Atomically deactivated domain: {domain}")
                        else:
                            logger.warning(
                                f"⚠️ Database updated but hosted zone deletion failed for: {domain}"
                            )
                    else:
                        logger.error(
                            f"❌ Failed to deactivate domain in database: {domain}"
                        )

            # Step 2: Handle domain activations atomically (database + hosted zones)
            if self.pending_domains:
                for domain in self.pending_domains:
                    # Update database first
                    db_success = self.update_domain_activation(domain)
                    if db_success:
                        # Only create hosted zone if database update succeeded
                        created_zones = self.ensure_hosted_zones([domain])
                        if created_zones:
                            logger.info(f"✅ Atomically activated domain: {domain}")
                        else:
                            logger.warning(
                                f"⚠️ Database updated but hosted zone creation failed for: {domain}"
                            )
                    else:
                        logger.error(
                            f"❌ Failed to activate domain in database: {domain}"
                        )

            # Step 3: Fetch ALL active domains from database (reflects current state)
            all_active_domains = self.fetch_active_domains_from_db()

            # Step 4: Clear CDK context cache and trigger GitHub workflow
            self.clear_cdk_context()
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
                logger.error(
                    f"❌ Failed to process batch of {len(all_active_domains)} domains"
                )
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

        logger.info(
            "🚀 SQS DNS Worker started. Processing DNS operations in batches..."
        )

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
