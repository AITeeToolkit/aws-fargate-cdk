#!/usr/bin/env python3
"""
GitHub Worker - Handles GitHub workflow triggers

Responsibilities:
- Trigger GitHub Actions workflows
- Update domain tracking files
- Commit to domain-updates branch
"""

import base64
import json
import logging
import os
import time
from threading import Thread

import boto3
import psycopg2
import requests
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class GitHubWorker(Thread):
    """Worker thread to handle GitHub workflow triggers"""

    def __init__(self, db_connection):
        """
        Initialize GitHub worker

        Args:
            db_connection: Shared database connection
        """
        super().__init__(daemon=True, name="GitHubWorker")

        self.region_name = os.environ.get("AWS_REGION", "us-east-1")
        self.environment = os.environ.get("ENVIRONMENT", "dev")
        self.db_connection = db_connection

        # GitHub configuration
        self.github_token = os.environ["GH_TOKEN"]
        self.repo = os.environ.get("REPO", "AITeeToolkit/aws-fargate-cdk")

        # Get queue URL from SSM
        ssm_client = boto3.client("ssm", region_name=self.region_name)
        self.queue_url = ssm_client.get_parameter(
            Name=f"/storefront-{self.environment}/sqs/github-workflow-queue-url"
        )["Parameter"]["Value"]

        self.sqs_client = boto3.client("sqs", region_name=self.region_name)

        # Batching configuration
        self.batch_timeout = 30  # Wait 30 seconds to batch messages
        self.pending_triggers = set()
        self.last_trigger_time = time.time()

        # Stats
        self.stats = {
            "messages_processed": 0,
            "workflows_triggered": 0,
            "errors": 0,
        }

        self.running = True
        logger.info("✅ GitHub worker initialized")

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

            if not full_url:
                logger.error(f"❌ [GH] Invalid message: missing full_url")
                return False

            logger.info(f"📨 [GH] Queuing workflow trigger for: {full_url}")

            # Add to pending triggers (will be batched)
            self.pending_triggers.add(full_url)

            return True

        except Exception as e:
            logger.error(f"❌ [GH] Error processing message: {e}")
            self.stats["errors"] += 1
            return False

    def should_trigger_workflow(self) -> bool:
        """Check if we should trigger workflow now"""
        if not self.pending_triggers:
            return False

        time_since_last = time.time() - self.last_trigger_time
        return time_since_last >= self.batch_timeout

    def trigger_workflow(self) -> bool:
        """Trigger GitHub workflow via repository dispatch"""
        try:
            # Fetch ALL active domains from database (not just pending)
            with self.db_connection.cursor() as cur:
                cur.execute(
                    "SELECT full_url FROM domains WHERE active_status = 'Y' ORDER BY full_url"
                )
                rows = cur.fetchall()
                all_active_domains = [row["full_url"] for row in rows]

            if not all_active_domains:
                logger.info("ℹ️ [GH] No active domains, skipping workflow trigger")
                return True

            logger.info(f"🔄 [GH] Triggering workflow for {len(all_active_domains)} active domains")

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
                    "domain_count": len(all_active_domains),
                    "triggered_at": time.time(),
                    "skip_tests": True,
                },
            }

            r = requests.post(url, headers=headers, json=payload)
            r.raise_for_status()

            self.stats["workflows_triggered"] += 1
            self.last_trigger_time = time.time()
            self.pending_triggers.clear()

            logger.info(f"✅ [GH] Triggered workflow for {len(all_active_domains)} domains")
            return True

        except Exception as e:
            logger.error(f"❌ [GH] Failed to trigger workflow: {e}")
            return False

    def run(self):
        """Main worker loop"""
        logger.info("🔄 [GH] Starting GitHub worker thread...")

        while self.running:
            try:
                response = self.sqs_client.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,
                    VisibilityTimeout=180,
                )

                messages = response.get("Messages", [])

                if messages:
                    logger.info(f"📬 [GH] Received {len(messages)} messages")

                    for message in messages:
                        if self.process_message(message):
                            # Delete message from queue
                            self.sqs_client.delete_message(
                                QueueUrl=self.queue_url,
                                ReceiptHandle=message["ReceiptHandle"],
                            )
                            self.stats["messages_processed"] += 1
                        else:
                            logger.warning(f"⚠️ [GH] Message processing failed, will retry")

                # Check if we should trigger workflow (batching)
                if self.should_trigger_workflow():
                    self.trigger_workflow()

                # Log stats periodically
                if (
                    self.stats["messages_processed"] % 10 == 0
                    and self.stats["messages_processed"] > 0
                ):
                    logger.info(f"📊 [GH] Stats: {self.stats}")

            except Exception as e:
                logger.error(f"❌ [GH] Error in worker loop: {e}")
                time.sleep(5)

        logger.info("👋 [GH] GitHub worker stopped")

    def stop(self):
        """Stop the worker gracefully"""
        self.running = False
