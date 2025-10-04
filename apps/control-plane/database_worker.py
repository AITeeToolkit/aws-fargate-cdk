#!/usr/bin/env python3
"""
Database Worker - Handles domain table operations

Responsibilities:
- Add/update domains in domains table
- Delete domains from domains table
- Update activation status
"""

import json
import logging
import os
import time
from threading import Thread

import boto3
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class DatabaseWorker(Thread):
    """Worker thread to handle database operations for domain management"""

    def __init__(self, db_connection):
        """
        Initialize database worker

        Args:
            db_connection: Shared database connection
        """
        super().__init__(daemon=True, name="DatabaseWorker")

        self.region_name = os.environ.get("AWS_REGION", "us-east-1")
        self.environment = os.environ.get("ENVIRONMENT", "dev")
        self.db_connection = db_connection

        # Get queue URL from SSM
        ssm_client = boto3.client("ssm", region_name=self.region_name)
        self.queue_url = ssm_client.get_parameter(
            Name=f"/storefront-{self.environment}/sqs/database-operations-queue-url"
        )["Parameter"]["Value"]

        self.sqs_client = boto3.client("sqs", region_name=self.region_name)

        # Stats
        self.stats = {
            "messages_processed": 0,
            "domains_added": 0,
            "domains_updated": 0,
            "domains_deleted": 0,
            "errors": 0,
        }

        self.running = True
        logger.info("✅ Database worker initialized")

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
            tenant_id = body.get("tenant_id")
            active_status = body.get("active_status", "Y")

            if not full_url or not tenant_id:
                logger.error(f"❌ Invalid message: missing full_url or tenant_id")
                return False

            logger.info(
                f"📨 [DB] Processing domain: {full_url} (active={active_status}, tenant={tenant_id})"
            )

            if active_status == "Y":
                return self._activate_domain(full_url, tenant_id)
            else:
                return self._deactivate_domain(full_url)

        except Exception as e:
            logger.error(f"❌ [DB] Error processing message: {e}")
            self.stats["errors"] += 1
            return False

    def _activate_domain(self, domain: str, tenant_id: str) -> bool:
        """Add or update domain in domains table"""
        try:
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
                    (domain, tenant_id),
                )
                self.db_connection.commit()

            self.stats["domains_added"] += 1
            logger.info(f"✅ [DB] Activated domain: {domain} for tenant {tenant_id}")
            return True

        except Exception as e:
            logger.error(f"❌ [DB] Failed to activate domain {domain}: {e}")
            self.db_connection.rollback()
            return False

    def _deactivate_domain(self, domain: str) -> bool:
        """Mark domain as inactive in domains table"""
        try:
            with self.db_connection.cursor() as cur:
                cur.execute(
                    "UPDATE domains SET active_status = 'N' WHERE full_url = %s",
                    (domain,),
                )
                self.db_connection.commit()

            self.stats["domains_deleted"] += 1
            logger.info(f"✅ [DB] Deactivated domain: {domain}")
            return True

        except Exception as e:
            logger.error(f"❌ [DB] Failed to deactivate domain {domain}: {e}")
            self.db_connection.rollback()
            return False

    def run(self):
        """Main worker loop"""
        logger.info("🔄 [DB] Starting database worker thread...")

        while self.running:
            try:
                response = self.sqs_client.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,
                    VisibilityTimeout=120,
                )

                messages = response.get("Messages", [])

                if not messages:
                    continue

                logger.info(f"📬 [DB] Received {len(messages)} messages")

                for message in messages:
                    if self.process_message(message):
                        # Delete message from queue
                        self.sqs_client.delete_message(
                            QueueUrl=self.queue_url,
                            ReceiptHandle=message["ReceiptHandle"],
                        )
                        self.stats["messages_processed"] += 1
                    else:
                        logger.warning(f"⚠️ [DB] Message processing failed, will retry")

                # Log stats periodically
                if (
                    self.stats["messages_processed"] % 10 == 0
                    and self.stats["messages_processed"] > 0
                ):
                    logger.info(f"📊 [DB] Stats: {self.stats}")

            except Exception as e:
                logger.error(f"❌ [DB] Error in worker loop: {e}")
                time.sleep(5)

        logger.info("👋 [DB] Database worker stopped")

    def stop(self):
        """Stop the worker gracefully"""
        self.running = False
