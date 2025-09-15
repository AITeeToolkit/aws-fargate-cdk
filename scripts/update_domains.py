import boto3, json, psycopg2

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

with conn.cursor() as cur:
    cur.execute("SELECT full_url FROM purchased_domains WHERE active_domain = 'Y';")
    rows = cur.fetchall()

domains = [r[0] for r in rows]

with open("domains.json", "w") as f:
    json.dump({"domains": domains}, f, indent=2)

print(f"✅ Found {len(domains)} active domains")