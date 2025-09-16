import os, requests, psycopg2, select, json, logging, boto3, time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logging.info("🚀 Starting listener service...")

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

# GitHub repo + PAT from environment
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

def trigger_github(domains):
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/dispatches"
    headers = {"Authorization": f"token {GITHUB_PAT}"}
    payload = {
        "ref": "main",
        "inputs": {
            "domains": json.dumps(domains),
            "environment": "dev"  # or detect from event
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    logging.info(f"✅ Triggered GitHub workflow with {len(domains)} domains.")

def fetch_domains():
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT full_url FROM purchased_domains WHERE active_domain = 'Y';")
    return [row[0] for row in cur.fetchall()]

def ensure_hosted_zones(domains):
    """Check for hosted zones and create missing ones"""
    route53_client = boto3.client("route53", region_name=region_name)
    created_zones = []
    
    for domain in domains:
        try:
            # List hosted zones to check if domain zone exists
            response = route53_client.list_hosted_zones_by_name(DNSName=domain)
            hosted_zones = response.get("HostedZones", [])
            
            # Check if zone exists for this exact domain
            existing_zone = next((zone for zone in hosted_zones if zone["Name"] == f"{domain}."), None)
            
            if existing_zone:
                logging.info(f"🔍 Hosted zone already exists for {domain}: {existing_zone['Id']}")
                continue
            
            # Create hosted zone if it doesn't exist
            caller_reference = f"{domain}-{int(time.time())}"
            response = route53_client.create_hosted_zone(
                Name=domain,
                CallerReference=caller_reference,
                HostedZoneConfig={
                    "Comment": f"Auto-created by listener for {domain}",
                    "PrivateZone": False
                }
            )
            
            zone_id = response["HostedZone"]["Id"]
            created_zones.append(domain)
            logging.info(f"✅ Created hosted zone for {domain}: {zone_id}")
            
        except Exception as e:
            logging.error(f"❌ Failed to create hosted zone for {domain}: {e}")
    
    if created_zones:
        logging.info(f"🎯 Created {len(created_zones)} new hosted zones: {created_zones}")
    
    return created_zones

cur = conn.cursor()
cur.execute("LISTEN domain_updates;")
conn.commit()  # Commit the LISTEN command
logging.info("Listening for domain updates...")

# Test if LISTEN is working by checking pg_listening_channels
cur.execute("SELECT * FROM pg_listening_channels();")
channels = cur.fetchall()
logging.info(f"📻 Currently listening to channels: {channels}")

# Also test a simple query to verify connection
cur.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
db_info = cur.fetchone()
logging.info(f"🔗 Connected to: database={db_info[0]}, user={db_info[1]}, host={db_info[2]}, port={db_info[3]}")

# Add periodic domain check
last_check = time.time()
CHECK_INTERVAL = 86400

# Test self-notification after 5 seconds
test_notification_sent = False

while True:
    try:
        ready = select.select([conn], [], [], 10)  # Shorter timeout for more frequent checks
        if ready == ([], [], []):
            current_time = time.time()
            
            # Send test notification after 5 seconds
            if not test_notification_sent and current_time - last_check > 5:
                logging.info("🧪 Sending test notification from same connection...")
                cur.execute("SELECT pg_notify('domain_updates', '{\"test\": \"self_notification\"}');")
                conn.commit()
                test_notification_sent = True
                logging.info("✅ Test notification sent")
            
            if current_time - last_check >= CHECK_INTERVAL:
                logging.info("🕐 Periodic domain check (no notifications received)")
                domains = fetch_domains()
                if domains:
                    logging.info(f"📋 Found {len(domains)} active domains: {domains}")
                    # Ensure hosted zones exist before triggering workflows
                    created_zones = ensure_hosted_zones(domains)
                    if created_zones:
                        logging.info(f"⏳ Waiting 15 seconds for hosted zones to propagate...")
                        time.sleep(15)
                        trigger_github(domains)
                    else:
                        logging.info("ℹ️ All hosted zones already exist, no deployment needed")
                else:
                    logging.info("📋 No active domains found")
                last_check = current_time
            # Add periodic debug info
            if current_time % 30 < 10:  # Every 30 seconds
                logging.info("🔍 Still listening... (no timeout)")
        else:
            logging.info("📡 Database connection has data ready")
            
        # Always poll for notifications
        conn.poll()
        if conn.notifies:
            logging.info(f"📬 Found {len(conn.notifies)} notifications")
            while conn.notifies:
                notify = conn.notifies.pop(0)
                logging.info(f"🔔 Domain change detected: {notify.payload}")
                domains = fetch_domains()
                
                # Ensure hosted zones exist before triggering workflow
                created_zones = ensure_hosted_zones(domains)
                if created_zones:
                    logging.info(f"⏳ Waiting 15 seconds for hosted zones to propagate...")
                    time.sleep(15)
                
                trigger_github(domains)
                last_check = time.time()  # Reset periodic check timer
        else:
            # Test if we're still listening every 30 seconds
            current_time = time.time()
            if int(current_time) % 30 == 0:
                cur.execute("SELECT * FROM pg_listening_channels();")
                channels = cur.fetchall()
                logging.info(f"🔍 Debug: Still listening to: {channels}")
            
    except Exception as e:
        logging.error(f"💥 Error in listener loop: {e}")
        # Try to reconnect
        try:
            conn.close()
        except:
            pass
        
        logging.info("🔄 Reconnecting to database...")
        conn = psycopg2.connect(
            host=os.environ["PGHOST"],
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
            dbname=os.environ["PGDATABASE"],
            port=os.environ.get("PGPORT", "5432")
        )
        cur = conn.cursor()
        cur.execute("LISTEN domain_updates;")
        conn.commit()  # Commit the LISTEN command
        logging.info("✅ Reconnected and listening for domain updates...")
        time.sleep(5)