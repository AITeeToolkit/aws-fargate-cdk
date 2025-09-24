import os, requests, psycopg2, select, json, logging, boto3, time, base64
from sqs_dns_publisher import publish_domain_change

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logging.info("🚀 Starting SQS-enabled listener service...")

try:
    # Get credentials from environment variables (provided by ECS secrets)
    logging.info("📡 Connecting to database...")
    conn = psycopg2.connect(
        host=os.environ["PGHOST"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
        port=os.environ.get("PGPORT", "5432")  # Default PostgreSQL port
    )
    logging.info("✅ Database connection established")
except Exception as e:
    logging.error(f"❌ Failed to connect to database: {e}")
    raise

# GitHub repo + PAT from environment (kept for fallback)
try:
    GITHUB_PAT = os.environ["GH_TOKEN"]
    logging.info("✅ GitHub token loaded")
except KeyError as e:
    logging.error(f"❌ Missing environment variable: {e}")
    raise

REPO = os.environ.get("REPO", "AITeeToolkit/aws-fargate-cdk")
WORKFLOW = "infrastructure.yml"     # workflow filename
region_name = "us-east-1"

logging.info(f"🔧 Configuration: REPO={REPO}, WORKFLOW={WORKFLOW}")
logging.info("🔄 SQS Mode: DNS operations will be queued for batch processing")


def setup_listener():
    """Setup database listener connection"""
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    cur.execute("LISTEN domain_status_changed;")
    cur.close()
    logging.info("✅ Listening on domain_status_changed channel...")


def handle_domain_change(domain_name: str, active: str):
    """
    Handle domain status change by publishing to SQS.
    
    Args:
        domain_name: Domain that changed
        active: 'Y' for activated, 'N' for deactivated
    """
    try:
        success = publish_domain_change(domain_name, active)
        
        if success:
            action = "activation" if active == "Y" else "deactivation"
            logging.info(f"✅ Successfully queued {domain_name} {action} for batch processing")
        else:
            logging.error(f"❌ Failed to queue {domain_name} change (active={active})")
            
    except Exception as e:
        logging.error(f"❌ Error handling domain change for {domain_name}: {e}")


# Setup listener
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
