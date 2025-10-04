#!/usr/bin/env python3
"""
Route53 Worker - Handles DNS operations

Responsibilities:
- Create/delete Route53 hosted zones
- Add/delete DNS records
- Manage nameservers
"""

import json
import logging
import os
import time
from threading import Thread

import boto3

logger = logging.getLogger(__name__)


class Route53Worker(Thread):
    """Worker thread to handle Route53 DNS operations"""

    def __init__(self):
        """Initialize Route53 worker"""
        super().__init__(daemon=True, name="Route53Worker")

        self.region_name = os.environ.get("AWS_REGION", "us-east-1")
        self.environment = os.environ.get("ENVIRONMENT", "dev")

        # Get queue URL from SSM
        ssm_client = boto3.client("ssm", region_name=self.region_name)
        self.queue_url = ssm_client.get_parameter(
            Name=f"/storefront-{self.environment}/sqs/route53-operations-queue-url"
        )["Parameter"]["Value"]

        self.sqs_client = boto3.client("sqs", region_name=self.region_name)
        self.route53_client = boto3.client("route53", region_name=self.region_name)

        # Stats
        self.stats = {
            "messages_processed": 0,
            "zones_created": 0,
            "zones_deleted": 0,
            "records_added": 0,
            "errors": 0,
        }

        self.running = True
        logger.info("✅ Route53 worker initialized")

    def process_message(self, message: dict) -> bool:
        """
        Process a single domain change message

        Args:
            message: SQS message containing domain change data

        Returns:
            bool: True if processed successfully
        """
        try:
            body = json.loads(message["Body"])

            full_url = body.get("full_url")
            active_status = body.get("active_status", "Y")

            if not full_url:
                logger.error(f"❌ [R53] Invalid message: missing full_url")
                return False

            logger.info(f"📨 [R53] Processing domain: {full_url} (active={active_status})")

            if active_status == "Y":
                return self._create_hosted_zone(full_url)
            else:
                return self._delete_hosted_zone(full_url)

        except Exception as e:
            logger.error(f"❌ [R53] Error processing message: {e}")
            self.stats["errors"] += 1
            return False

    def _create_hosted_zone(self, domain: str) -> bool:
        """Create Route53 hosted zone for domain"""
        try:
            # Check if zone already exists
            try:
                zones = self.route53_client.list_hosted_zones_by_name(DNSName=domain)
                for zone in zones.get("HostedZones", []):
                    if zone["Name"].rstrip(".") == domain:
                        logger.info(f"ℹ️ [R53] Hosted zone already exists for {domain}")
                        return True
            except Exception:
                pass

            # Create new hosted zone
            response = self.route53_client.create_hosted_zone(
                Name=domain,
                CallerReference=f"{domain}-{int(time.time())}",
                HostedZoneConfig={
                    "Comment": f"Managed by storefront-{self.environment}",
                    "PrivateZone": False,
                },
            )

            zone_id = response["HostedZone"]["Id"]
            nameservers = response["DelegationSet"]["NameServers"]

            self.stats["zones_created"] += 1
            logger.info(f"✅ [R53] Created hosted zone {zone_id} for {domain}")
            logger.info(f"📋 [R53] Nameservers: {', '.join(nameservers)}")

            # Add default records (A, CNAME, etc.)
            self._add_default_records(zone_id, domain)

            return True

        except Exception as e:
            logger.error(f"❌ [R53] Failed to create hosted zone for {domain}: {e}")
            return False

    def _add_default_records(self, zone_id: str, domain: str):
        """Add default DNS records to hosted zone"""
        try:
            # Get ALB DNS name from SSM (if exists)
            ssm_client = boto3.client("ssm", region_name=self.region_name)
            try:
                alb_dns = ssm_client.get_parameter(
                    Name=f"/storefront-{self.environment}/alb/{domain}/dns-name"
                )["Parameter"]["Value"]

                # Add A record pointing to ALB
                self.route53_client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch={
                        "Changes": [
                            {
                                "Action": "UPSERT",
                                "ResourceRecordSet": {
                                    "Name": domain,
                                    "Type": "A",
                                    "AliasTarget": {
                                        "HostedZoneId": "Z35SXDOTRQ7X7K",  # ALB hosted zone for us-east-1
                                        "DNSName": alb_dns,
                                        "EvaluateTargetHealth": False,
                                    },
                                },
                            }
                        ]
                    },
                )

                self.stats["records_added"] += 1
                logger.info(f"✅ [R53] Added A record for {domain} → {alb_dns}")

            except Exception:
                logger.info(f"ℹ️ [R53] No ALB found for {domain}, skipping A record")

        except Exception as e:
            logger.warning(f"⚠️ [R53] Failed to add default records: {e}")

    def _delete_hosted_zone(self, domain: str) -> bool:
        """Delete Route53 hosted zone and all records"""
        try:
            # Find hosted zone
            zones = self.route53_client.list_hosted_zones_by_name(DNSName=domain)
            zone_id = None

            for zone in zones.get("HostedZones", []):
                if zone["Name"].rstrip(".") == domain:
                    zone_id = zone["Id"]
                    break

            if not zone_id:
                logger.info(f"ℹ️ [R53] No hosted zone found for {domain}")
                return True

            # Delete all records except NS and SOA
            records = self.route53_client.list_resource_record_sets(HostedZoneId=zone_id)
            changes = []

            for record in records.get("ResourceRecordSets", []):
                if record["Type"] not in ["NS", "SOA"]:
                    changes.append({"Action": "DELETE", "ResourceRecordSet": record})

            if changes:
                self.route53_client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch={"Changes": changes},
                )
                logger.info(f"✅ [R53] Deleted {len(changes)} records from {domain}")

            # Note: Not deleting the hosted zone itself to preserve history
            # Uncomment below to actually delete the zone:
            # self.route53_client.delete_hosted_zone(Id=zone_id)
            # self.stats["zones_deleted"] += 1

            logger.info(f"⚠️ [R53] Skipped hosted zone deletion for {domain} (keeping zone)")
            return True

        except Exception as e:
            logger.error(f"❌ [R53] Failed to delete hosted zone for {domain}: {e}")
            return False

    def run(self):
        """Main worker loop"""
        logger.info("🔄 [R53] Starting Route53 worker thread...")

        while self.running:
            try:
                response = self.sqs_client.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,
                    VisibilityTimeout=300,  # 5 minutes for DNS operations
                )

                messages = response.get("Messages", [])

                if not messages:
                    continue

                logger.info(f"📬 [R53] Received {len(messages)} messages")

                for message in messages:
                    if self.process_message(message):
                        # Delete message from queue
                        self.sqs_client.delete_message(
                            QueueUrl=self.queue_url,
                            ReceiptHandle=message["ReceiptHandle"],
                        )
                        self.stats["messages_processed"] += 1
                    else:
                        logger.warning(f"⚠️ [R53] Message processing failed, will retry")

                # Log stats periodically
                if (
                    self.stats["messages_processed"] % 10 == 0
                    and self.stats["messages_processed"] > 0
                ):
                    logger.info(f"📊 [R53] Stats: {self.stats}")

            except Exception as e:
                logger.error(f"❌ [R53] Error in worker loop: {e}")
                time.sleep(5)

        logger.info("👋 [R53] Route53 worker stopped")

    def stop(self):
        """Stop the worker gracefully"""
        self.running = False
