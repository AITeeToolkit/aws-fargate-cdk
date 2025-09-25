#!/usr/bin/env python3
"""
DNS Worker Application for AWS Fargate

Runs the SQS DNS Worker to process DNS operations from SQS queue.
Handles batch processing of domain activations/deactivations.
"""

import os
import sys
import time
import signal
import logging
from sqs_dns_worker import SQSDNSWorker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Global worker instance for signal handling
worker = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"🛑 Received signal {signum}, shutting down DNS worker...")
    if worker:
        worker.stop()
    sys.exit(0)

def main():
    """Main application entry point."""
    global worker
    
    logger.info("🚀 Starting DNS Worker Service...")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize the DNS worker
        worker = SQSDNSWorker(
            max_messages=10,           # Process up to 10 messages per batch
            wait_time_seconds=20,      # Long efficient polling
            batch_timeout=30           # Process batch every 30 seconds
        )
        
        logger.info("✅ DNS Worker initialized successfully")
        logger.info(f"📋 Configuration:")
        logger.info(f"   - Queue URL: {worker.queue_url}")
        logger.info(f"   - Region: {worker.region_name}")
        logger.info(f"   - Repository: {worker.repo}")
        logger.info(f"   - Max Messages: {worker.max_messages}")
        logger.info(f"   - Wait Time: {worker.wait_time_seconds}s")
        logger.info(f"   - Batch Timeout: {worker.batch_timeout}s")
        
        # Start processing messages
        logger.info("🔄 Starting message processing loop...")
        worker.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error in DNS worker: {e}")
        sys.exit(1)
    finally:
        if worker:
            logger.info("🧹 Cleaning up DNS worker...")
            worker.stop()
        logger.info("👋 DNS Worker service stopped")

if __name__ == "__main__":
    main()
