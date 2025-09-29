import json
import logging
import os
import select
import time

import psycopg2
from sqs_dns_publisher import publish_domain_change

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logging.info("🚀 Starting SQS-enabled listener service...")

try:
    # Get credentials from environment variables
    logging.info("📡 Connecting to database...")
    conn = psycopg2.connect(
        host=os.environ["PGHOST"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
        port=os.environ.get("PGPORT", "5432"),  # Default PostgreSQL port
    )
    logging.info("✅ Database connection established")
except Exception as e:
    logging.error(f"❌ Failed to connect to database: {e}")
    raise

logging.info("🔄 SQS Mode: DNS operations will be queued for batch processing")


# Fetch active domains from database (same as original listener_app.py)
def fetch_domains():
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT full_url FROM purchased_domains WHERE active_domain = 'Y';"
    )
    result = [row[0] for row in cur.fetchall()]
    cur.close()
    return result


def setup_listener():
    """Setup database listener connection"""
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    cur.execute("LISTEN domain_status_changed;")
    cur.close()
    logging.info("✅ Listening on domain_status_changed channel...")


def handle_domain_change(domain_name: str, active: str):
    """
    Handle domain status change by queuing to DNS worker for atomic processing.
    DNS worker will handle all database updates and Route53 operations together.

    Args:
        domain_name: Domain that changed
        active: 'Y' for activated, 'N' for deactivated
    """
    try:
        action = "activation" if active == "Y" else "deactivation"
        logging.info(f"🔄 Processing domain {action} for {domain_name}")

        # Queue the change for DNS worker to handle ALL operations atomically
        logging.info(f"🔄 Queuing {domain_name} for atomic DNS worker processing")
        sqs_success = publish_domain_change(domain_name, active)

        if sqs_success:
            logging.info(
                f"✅ Successfully queued {domain_name} {action} for DNS worker"
            )
            logging.info(
                f"🔄 DNS Worker will handle database updates, hosted zone operations, and infrastructure updates atomically"
            )
        else:
            logging.error(f"❌ Failed to queue {domain_name} change for DNS worker")

    except Exception as e:
        logging.error(f"❌ Error processing domain change for {domain_name}: {e}")


# Setup listener for database notifications
setup_listener()

# Main event loop
while True:
    ready = select.select([conn], [], [], 60)
    if not ready[0]:
        logging.debug("🔄 Keepalive check (no notifications)")
        continue

    try:
        conn.poll()

        while conn.notifies:
            notify = conn.notifies.pop(0)
            logging.info(f"🔔 Raw notification received: {notify.payload}")

            payload = json.loads(notify.payload)
            domain_name = payload.get("domain_name")
            active = payload.get("active")

            if not domain_name or active not in ("Y", "N"):
                logging.warning(f"⚠️ Invalid payload: {payload}")
                continue

            logging.info(f"📌 Domain update → {domain_name} (active={active})")

            # Handle domain change via SQS
            handle_domain_change(domain_name, active)

    except Exception as e:
        logging.error(f"❌ Error processing notification: {e}")
        time.sleep(5)
