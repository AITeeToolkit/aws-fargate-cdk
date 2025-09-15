#!/usr/bin/env python3

import os
import json
import boto3
import psycopg2
import subprocess
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_credentials():
    """Get RDS credentials from Secrets Manager"""
    secret_name = os.environ["DB_SECRET_NAME"]
    region = os.environ.get("AWS_REGION", "us-east-1")
    
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

def update_domains_from_db():
    """Query database and return list of active domains"""
    creds = get_db_credentials()
    
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
    
    conn.close()
    domains = [r[0] for r in rows]
    logging.info(f"Found {len(domains)} active domains")
    return domains

def commit_and_push_changes(domains):
    """Commit updated domains.json to GitHub repository"""
    repo = os.environ["REPO"]
    github_token = os.environ["GH_TOKEN"]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone repository
        clone_url = f"https://{github_token}@github.com/{repo}.git"
        subprocess.run([
            "git", "clone", clone_url, temp_dir
        ], check=True, capture_output=True)
        
        # Update domains.json
        domains_file = os.path.join(temp_dir, "domains.json")
        with open(domains_file, "w") as f:
            json.dump({"domains": domains}, f, indent=2)
        
        # Configure git
        subprocess.run([
            "git", "config", "user.email", "action@github.com"
        ], cwd=temp_dir, check=True)
        subprocess.run([
            "git", "config", "user.name", "Domain Updater"
        ], cwd=temp_dir, check=True)
        
        # Check if there are changes
        result = subprocess.run([
            "git", "diff", "--quiet", "domains.json"
        ], cwd=temp_dir, capture_output=True)
        
        if result.returncode != 0:  # Changes detected
            # Add, commit and push
            subprocess.run([
                "git", "add", "domains.json"
            ], cwd=temp_dir, check=True)
            subprocess.run([
                "git", "commit", "-m", "Auto-update domains from database"
            ], cwd=temp_dir, check=True)
            subprocess.run([
                "git", "push", "origin", "main"
            ], cwd=temp_dir, check=True)
            logging.info("✅ Updated and pushed domains.json")
            return True
        else:
            logging.info("No changes to domains.json")
            return False

def main():
    """Main function"""
    try:
        logging.info("🚀 Starting domain update task")
        
        # Get domains from database
        domains = update_domains_from_db()
        
        # Commit changes to GitHub
        changes_made = commit_and_push_changes(domains)
        
        if changes_made:
            logging.info("✅ Domain update completed successfully")
        else:
            logging.info("✅ No updates needed")
            
    except Exception as e:
        logging.error(f"❌ Domain update failed: {e}")
        raise

if __name__ == "__main__":
    main()
