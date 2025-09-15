import os, requests, psycopg2, select, json, logging, boto3

GITHUB_TOKEN = os.environ["GH_TOKEN"]
REPO = "AITeeToolkit/aws-fargate-cdk"

secret_name = "storefront/dev/rds-credentials"   # whatever CDK created
region_name = "us-east-1"
client = boto3.client("secretsmanager", region_name=region_name)
response = client.get_secret_value(SecretId=secret_name)
creds = json.loads(response["SecretString"])

def trigger_github():
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/application.yml/dispatches"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"ref": "main"}
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    logging.info("✅ Triggered GitHub application.yml workflow")

# listen for DB events
conn = psycopg2.connect(
    host=creds["host"],
    user=creds["username"],
    password=creds["password"],
    dbname=creds["dbname"],
    port=creds["port"]
)

conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("LISTEN domain_updates;")

while True:
    if select.select([conn], [], [], 60) == ([], [], []):
        continue
    conn.poll()
    while conn.notifies:
        notify = conn.notifies.pop(0)
        payload = json.loads(notify.payload)
        logging.info(f"Domain change detected: {payload}")
        trigger_github()