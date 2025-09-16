import os, requests, psycopg2, select, json, logging, boto3, time

secret_name = "storefront/dev/rds-credentials"   # whatever CDK created
region_name = "us-east-1"
client = boto3.client("secretsmanager", region_name=region_name)
response = client.get_secret_value(SecretId=secret_name)
creds = json.loads(response["SecretString"])

conn = psycopg2.connect(
    host=creds["host"],
    user=creds["username"],
    password=creds["password"],
    dbname=creds["dbname"],
    port=creds["port"]
)

# GitHub repo + PAT
ssm_client = boto3.client("ssm", region_name=region_name)
github_pat_response = ssm_client.get_parameter(
    Name="/storefront-dev/github/PAT",
    WithDecryption=True
)
GITHUB_PAT = github_pat_response["Parameter"]["Value"]
REPO = "AITeeToolkit/aws-fargate-cdk" # your infra repo
WORKFLOW = "application.yml"     # workflow filename

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
logging.info("Listening for domain updates...")

while True:
    if select.select([conn], [], [], 60) == ([], [], []):
        continue
    conn.poll()
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