#!/usr/bin/env python3
"""
Control Plane Application for AWS Fargate

Runs multiple specialized workers in parallel:
- Database Worker: Handles domain table operations
- Route53 Worker: Manages DNS zones and records
- GitHub Worker: Triggers deployment workflows
"""

import logging
import os
import signal
import sys
import time

import boto3
import psycopg2
from database_worker import DatabaseWorker
from github_worker import GitHubWorker
from psycopg2.extras import RealDictCursor
from route53_worker import Route53Worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Global workers for signal handling
workers = []
db_connection = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"🛑 Received signal {signum}, shutting down all workers...")
    for worker in workers:
        worker.stop()
    if db_connection:
        db_connection.close()
    sys.exit(0)


def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        region_name = os.environ.get("AWS_REGION", "us-east-1")
        environment = os.environ.get("ENVIRONMENT", "dev")

        ssm_client = boto3.client("ssm", region_name=region_name)

        db_host = ssm_client.get_parameter(Name=f"/storefront-{environment}/database/host")[
            "Parameter"
        ]["Value"]

        db_name = ssm_client.get_parameter(Name=f"/storefront-{environment}/database/name")[
            "Parameter"
        ]["Value"]

        db_user = ssm_client.get_parameter(Name=f"/storefront-{environment}/database/username")[
            "Parameter"
        ]["Value"]

        db_password = ssm_client.get_parameter(
            Name=f"/storefront-{environment}/database/password", WithDecryption=True
        )["Parameter"]["Value"]

        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            cursor_factory=RealDictCursor,
        )

        logger.info(f"✅ Connected to database: {db_host}/{db_name}")
        return connection

    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise


def main():
    """Main application entry point."""
    global workers, db_connection

    logger.info("🚀 Starting Control Plane Service (Modular Architecture)...")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Connect to database (shared by database and github workers)
        db_connection = connect_to_database()

        # Initialize all workers
        database_worker = DatabaseWorker(db_connection)
        route53_worker = Route53Worker()
        github_worker = GitHubWorker(db_connection)

        workers = [database_worker, route53_worker, github_worker]

        logger.info("✅ All workers initialized successfully")
        logger.info(f"📋 Active Workers:")
        logger.info(f"   - Database Worker (domain table operations)")
        logger.info(f"   - Route53 Worker (DNS zone management)")
        logger.info(f"   - GitHub Worker (workflow triggers)")

        # Start all worker threads
        for worker in workers:
            worker.start()
            logger.info(f"🔄 Started {worker.name}")

        # Keep main thread alive
        logger.info("✅ All workers running...")
        while True:
            time.sleep(60)
            # Check if all workers are still alive
            for worker in workers:
                if not worker.is_alive():
                    logger.error(f"❌ Worker {worker.name} died, restarting...")
                    worker.start()

    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error in Control Plane service: {e}")
        sys.exit(1)
    finally:
        logger.info("🧹 Cleaning up workers...")
        for worker in workers:
            worker.stop()
        for worker in workers:
            worker.join(timeout=5)
        if db_connection:
            db_connection.close()
        logger.info("👋 Control Plane service stopped")


if __name__ == "__main__":
    main()
