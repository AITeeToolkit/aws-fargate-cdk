import boto3, json, psycopg2
import sys
import os

secret_name = "storefront/dev/rds-credentials"   # whatever CDK created
region_name = "us-east-1"

print("🔍 DEBUG: Environment check")
print(f"AWS_ACCESS_KEY_ID: {'SET' if os.environ.get('AWS_ACCESS_KEY_ID') else 'NOT SET'}")
print(f"AWS_SECRET_ACCESS_KEY: {'SET' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'NOT SET'}")
print(f"AWS_SESSION_TOKEN: {'SET' if os.environ.get('AWS_SESSION_TOKEN') else 'NOT SET'}")
print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'NOT SET')}")
print(f"AWS_DEFAULT_REGION: {os.environ.get('AWS_DEFAULT_REGION', 'NOT SET')}")

try:
    print("🔍 Testing AWS STS identity...")
    sts_client = boto3.client("sts", region_name=region_name)
    identity = sts_client.get_caller_identity()
    print(f"✅ AWS Identity: {identity.get('Arn', 'Unknown')}")
    print(f"   Account: {identity.get('Account', 'Unknown')}")
    print(f"   User/Role: {identity.get('UserId', 'Unknown')}")
    
except Exception as e:
    print(f"❌ AWS STS check failed: {e}")
    sys.exit(1)

try:
    print("🔍 Fetching database credentials from Secrets Manager...")
    print(f"   Secret: {secret_name}")
    print(f"   Region: {region_name}")
    
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    print("✅ Successfully retrieved secret")
    
    creds = json.loads(response["SecretString"])
    print(f"🔍 Secret contains keys: {list(creds.keys())}")
    print(f"🔍 Connecting to database at {creds['host']}:{creds['port']}")
    print(f"   Database: {creds['dbname']}")
    print(f"   Username: {creds['username']}")
    
    conn = psycopg2.connect(
        host=creds["host"],
        user=creds["username"],
        password=creds["password"],
        dbname=creds["dbname"],
        port=creds["port"],
        connect_timeout=10
    )
    print("✅ Database connection successful")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print(f"   Exception type: {type(e).__name__}")
    import traceback
    print("   Full traceback:")
    traceback.print_exc()
    sys.exit(1)

with conn.cursor() as cur:
    cur.execute("SELECT full_url FROM purchased_domains WHERE active_domain = 'Y';")
    rows = cur.fetchall()

domains = [r[0] for r in rows]

with open("domains.json", "w") as f:
    json.dump({"domains": domains}, f, indent=2)

print(f"✅ Found {len(domains)} active domains")