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


# Trigger GitHub workflow
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


# Fetch active domains from database
def fetch_domains():
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT full_url FROM purchased_domains WHERE active_domain = 'Y';")
    result = [row[0] for row in cur.fetchall()]
    cur.close()
    return result


# Ensure hosted zones exist
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

def setup_listener():
    """Setup database listener connection"""
    conn.set_session(autocommit=True)  # <-- ensures LISTEN persists
    cur = conn.cursor()
    cur.execute("LISTEN domain_updates;")
    cur.close()
    logging.info("✅ Listening for domain updates...")

setup_listener()

while True:
    try:
        # Block until notification or timeout
        ready = select.select([conn], [], [], 60)
        if not ready[0]:
            logging.debug("🔄 Keepalive check (no notifications)")
            continue

        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            logging.info(f"🔔 Raw notification received: {notify.payload}")

            try:
                # Parse JSON payload
                payload = json.loads(notify.payload)
                domain_name = payload.get("domain_name")
                active = payload.get("active")

                if not domain_name or active not in ("Y", "N"):
                    logging.warning(f"⚠️ Invalid payload: {payload}")
                    continue

                logging.info(f"📌 Domain update → {domain_name} (active={active})")

                if active == "Y":
                    # Ensure hosted zone exists
                    created_zones = ensure_hosted_zones([domain_name])
                    if created_zones:
                        logging.info("⏳ Waiting 15s for hosted zone to propagate...")
                        time.sleep(15)
                else:
                    logging.info(f"🗑 Marked inactive → handle removal for {domain_name}")
                    # TODO: remove hosted zone / update domains.json cleanup here

                # Trigger GitHub workflow for this single domain change
                trigger_github([domain_name])
                logging.info("✅ Successfully processed domain update")

            except Exception as e:
                logging.error(f"❌ Error processing notification: {e}")
                continue

    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logging.error(f"💥 Database connection error: {e}")
        try:
            conn.close()
        except:
            pass
        logging.info("🔄 Reconnecting to database...")
        time.sleep(5)
        try:
            conn = psycopg2.connect(
                host=os.environ["PGHOST"],
                user=os.environ["PGUSER"],
                password=os.environ["PGPASSWORD"],
                dbname=os.environ["PGDATABASE"],
                port=os.environ.get("PGPORT", "5432")
            )
            setup_listener()
        except Exception as reconnect_error:
            logging.error(f"❌ Failed to reconnect: {reconnect_error}")
            time.sleep(10)

    except Exception as e:
        logging.error(f"💥 Unexpected error in listener loop: {e}")
        time.sleep(5)