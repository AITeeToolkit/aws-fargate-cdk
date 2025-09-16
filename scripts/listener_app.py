import os, requests, psycopg2, select, json, logging, boto3, time, base64


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
    # Commit directly to main branch
    domains_content = json.dumps({"domains": domains}, indent=2)
    
    # Get current domains.json file to get its SHA
    url = f"https://api.github.com/repos/{REPO}/contents/domains.json"
    headers = {"Authorization": f"token {GITHUB_PAT}"}
    r = requests.get(url, headers=headers)
    
    # Base64 encode the content
    content_b64 = base64.b64encode(domains_content.encode()).decode()
    
    if r.status_code == 200:
        file_sha = r.json()["sha"]
        # Update existing file
        payload = {
            "message": f"Update domains.json with {len(domains)} active domains",
            "content": content_b64,
            "sha": file_sha,
            "branch": "main"
        }
    else:
        # Create new file
        payload = {
            "message": f"Create domains.json with {len(domains)} active domains",
            "content": content_b64,
            "branch": "main"
        }
    
    r = requests.put(url, headers=headers, json=payload)
    r.raise_for_status()
    
    logging.info(f"✅ Committed domains.json to main branch with {len(domains)} domains.")

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
conn.commit()
logging.info("✅ Listening for domain updates...")

# Add periodic domain check
last_check = time.time()
CHECK_INTERVAL = 86400

while True:
    try:
        ready = select.select([conn], [], [], 60)
        if ready == ([], [], []):
            current_time = time.time()
            if current_time - last_check >= CHECK_INTERVAL:
                logging.info("🕐 Periodic domain check")
                domains = fetch_domains()
                if domains:
                    created_zones = ensure_hosted_zones(domains)
                    if created_zones:
                        logging.info(f"⏳ Waiting 15 seconds for hosted zones to propagate...")
                        time.sleep(15)
                        trigger_github(domains)
                last_check = current_time
        
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            logging.info(f"🔔 Domain change detected: {notify.payload}")
            domains = fetch_domains()
            
            created_zones = ensure_hosted_zones(domains)
            if created_zones:
                logging.info(f"⏳ Waiting 15 seconds for hosted zones to propagate...")
                time.sleep(15)
            
            trigger_github(domains)
            last_check = time.time()
            
    except Exception as e:
        logging.error(f"💥 Error in listener loop: {e}")
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
        conn.commit()
        logging.info("✅ Reconnected and listening for domain updates...")
        time.sleep(5)