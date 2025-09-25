import os, requests, psycopg2, select, json, logging, time, base64
from sqs_dns_publisher import publish_domain_change
from domain_helpers import ensure_hosted_zone_and_store, update_domain_with_tenant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
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


# Trigger GitHub workflow (same as original listener_app.py)
def trigger_github(domains):
    branch_name = "domain-updates"  # fixed branch for updates
    domains_content = json.dumps({"domains": domains}, indent=2)
    headers = {"Authorization": f"token {GITHUB_PAT}"}

    # 1. Get latest commit SHA from main
    url = f"https://api.github.com/repos/{REPO}/git/refs/heads/main"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    main_sha = r.json()["object"]["sha"]

    # 2. Ensure the branch exists (create if missing)
    url = f"https://api.github.com/repos/{REPO}/git/refs/heads/{branch_name}"
    r = requests.get(url, headers=headers)
    if r.status_code == 404:
        logging.info(f"🌱 Creating branch '{branch_name}' from main")
        url = f"https://api.github.com/repos/{REPO}/git/refs"
        payload = {"ref": f"refs/heads/{branch_name}", "sha": main_sha}
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()

    # 3. Get SHA of existing domains.json in this branch (if it exists)
    url = f"https://api.github.com/repos/{REPO}/contents/domains.json"
    params = {"ref": branch_name}
    r = requests.get(url, headers=headers, params=params)
    file_sha = r.json()["sha"] if r.status_code == 200 else None

    # 4. Base64 encode content
    content_b64 = base64.b64encode(domains_content.encode()).decode()

    # 5. Commit update (create if new, update if exists)
    payload = {
        "message": f"Update domains.json with {len(domains)} active domains",
        "content": content_b64,
        "branch": branch_name
    }
    if file_sha:
        payload["sha"] = file_sha  # update existing

    url = f"https://api.github.com/repos/{REPO}/contents/domains.json"
    r = requests.put(url, headers=headers, json=payload)
    r.raise_for_status()

    logging.info(f"✅ Committed domains.json with {len(domains)} domains to '{branch_name}'")


# Fetch active domains from database (same as original listener_app.py)
def fetch_domains():
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT full_url FROM purchased_domains WHERE active_domain = 'Y';")
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
    Handle domain status change with proper sequence:
    1. If domain activated ('Y'), ensure hosted zone exists
    2. Update domains table with tenant information
    3. Queue to SQS for batch processing
    
    Args:
        domain_name: Domain that changed
        active: 'Y' for activated, 'N' for deactivated
    """
    try:
        if active == "Y":
            logging.info(f"🔄 Processing domain activation for {domain_name}")
            
            # Step 1: Ensure hosted zone exists and get info
            logging.info(f"🔍 Step 1: Ensuring hosted zone exists for {domain_name}")
            hosted_zone_id, aws_hosted_zone_id = ensure_hosted_zone_and_store(conn, domain_name, region_name)
            
            if hosted_zone_id and aws_hosted_zone_id:
                # Step 2: Update domains table with tenant information
                logging.info(f"🔄 Step 2: Updating domains table with tenant info for {domain_name}")
                tenant_id = update_domain_with_tenant(conn, domain_name, hosted_zone_id, aws_hosted_zone_id)
                
                if tenant_id:
                    logging.info(f"✅ Domain {domain_name} successfully linked to tenant {tenant_id}")
                else:
                    logging.warning(f"⚠️ Domain {domain_name} activated but no tenant found in purchased_domains")
            else:
                logging.error(f"❌ Could not ensure hosted zone for {domain_name}")
        
        # Step 4: Queue the change for batch processing via SQS
        logging.info(f"🔄 Step 3: Queuing {domain_name} for batch processing")
        sqs_success = publish_domain_change(domain_name, active)
        
        if sqs_success:
            action = "activation" if active == "Y" else "deactivation"
            logging.info(f"✅ Successfully queued {domain_name} {action} for batch processing")
            logging.info(f"🔄 DNS Worker will handle infrastructure updates in next batch cycle")
        else:
            logging.error(f"❌ Failed to queue {domain_name} change for batch processing")
            
    except Exception as e:
        logging.error(f"❌ Error processing domain change for {domain_name}: {e}")


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
