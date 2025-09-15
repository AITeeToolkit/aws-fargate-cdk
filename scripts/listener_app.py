import os, requests, psycopg2, select, json, logging, boto3

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
        trigger_github(domains)