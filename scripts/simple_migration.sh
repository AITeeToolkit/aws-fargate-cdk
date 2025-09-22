#!/bin/bash
set -e

echo "🚀 Elasticsearch to Public OpenSearch Migration"
echo "==============================================="

# Parse command line arguments
SKIP_BACKUP=false
EXISTING_BUCKET=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --use-bucket)
            EXISTING_BUCKET="$2"
            SKIP_BACKUP=true
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-backup           Skip K8s backup copy (use existing S3 data)"
            echo "  --use-bucket BUCKET     Use existing S3 bucket (implies --skip-backup)"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Configuration
NAMESPACE="elasticsearch"
POD_LABEL="app=elasticsearch-master"
BACKUP_PATH="/usr/share/elasticsearch/backup"
S3_PREFIX="elasticsearch-snapshots"
REPO_NAME="migration_repo"

# Set S3 bucket
if [ -n "$EXISTING_BUCKET" ]; then
    S3_BUCKET="$EXISTING_BUCKET"
    echo "📦 Using existing S3 bucket: $S3_BUCKET"
else
    S3_BUCKET="opensearch-migration-$(date +%s)"
    echo "📦 Creating new S3 bucket: $S3_BUCKET"
fi

# Function to get OpenSearch endpoint (will be public after deployment)
get_opensearch_endpoint() {
    # Try to get from SSM parameter first (new public domain)
    ENDPOINT=$(aws ssm get-parameter --name "/storefront-dev/opensearch/endpoint" --query 'Parameter.Value' --output text 2>/dev/null | sed 's|https://||' || echo "")
    
    if [ -z "$ENDPOINT" ]; then
        # Fallback: get from existing domain (will be replaced)
        echo "⚠️  Using existing domain endpoint (will be replaced with public domain)"
        ENDPOINT=$(aws opensearch describe-domain --domain-name opensearchdomai-reqboywrejg9 --query 'DomainStatus.Endpoints.vpc' --output text 2>/dev/null || echo "")
    fi
    
    echo "$ENDPOINT"
}

OPENSEARCH_ENDPOINT=$(get_opensearch_endpoint)

echo "📡 OpenSearch endpoint: $OPENSEARCH_ENDPOINT"
echo "🪣 S3 bucket: $S3_BUCKET"

if [ "$SKIP_BACKUP" = true ]; then
    echo "⏭️  Skipping K8s backup copy (using existing S3 data)"
    
    # Verify S3 bucket exists and has data
    if ! aws s3 ls s3://$S3_BUCKET/$S3_PREFIX/ >/dev/null 2>&1; then
        echo "❌ S3 bucket or prefix not found: s3://$S3_BUCKET/$S3_PREFIX/"
        echo "💡 Available buckets with 'opensearch' in name:"
        aws s3 ls | grep opensearch || echo "   No opensearch buckets found"
        exit 1
    fi
    
    echo "✅ Found existing S3 data:"
    aws s3 ls s3://$S3_BUCKET/$S3_PREFIX/ | head -5
    echo "   ... (showing first 5 files)"
    
    # Create temp directory for summary info
    TEMP_DIR=$(mktemp -d)
    
    # Get snapshot info from S3 for summary
    LATEST_SNAP=$(aws s3 ls s3://$S3_BUCKET/$S3_PREFIX/ | grep "snap-.*\.dat" | tail -1 | awk '{print $4}')
    
else
    # Step 1: Get Elasticsearch pod
    echo "🔍 Finding Elasticsearch pod..."
    POD_NAME=$(kubectl get pods -n $NAMESPACE -l $POD_LABEL -o jsonpath='{.items[0].metadata.name}')
    echo "✅ Using pod: $POD_NAME"

    # Step 2: Create local temp directory
    TEMP_DIR=$(mktemp -d)
    echo "📁 Temp directory: $TEMP_DIR"

    # Step 3: Find and copy latest snapshot with its indices
    echo "📥 Finding latest snapshot..."
    LATEST_SNAP=$(kubectl exec $POD_NAME -n $NAMESPACE -c elasticsearch -- find $BACKUP_PATH -name "snap-*.dat" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)
    LATEST_META=$(echo $LATEST_SNAP | sed 's/snap-/meta-/')

    if [ -z "$LATEST_SNAP" ]; then
        echo "❌ No snapshots found"
        exit 1
    fi

    SNAP_ID=$(basename $LATEST_SNAP .dat | sed 's/snap-//')
    echo "📥 Latest snapshot: $(basename $LATEST_SNAP)"
    echo "📥 Snapshot ID: $SNAP_ID"

    mkdir -p $TEMP_DIR/backup

    echo "📥 Copying snapshot metadata files..."
    # Copy the essential metadata files
    echo "  → Copying $(basename $LATEST_SNAP)..."
    kubectl cp $NAMESPACE/$POD_NAME:$LATEST_SNAP $TEMP_DIR/backup/$(basename $LATEST_SNAP) -c elasticsearch -v=2
    echo "  → Copying $(basename $LATEST_META)..."
    kubectl cp $NAMESPACE/$POD_NAME:$LATEST_META $TEMP_DIR/backup/$(basename $LATEST_META) -c elasticsearch -v=2

    # Copy the index-N file (repository metadata)
    echo "  → Finding and copying index file..."
    kubectl exec $POD_NAME -n $NAMESPACE -c elasticsearch -- find $BACKUP_PATH -name "index-*" -type f | head -1 | xargs -I {} kubectl cp $NAMESPACE/$POD_NAME:{} $TEMP_DIR/backup/$(basename {}) -c elasticsearch -v=2

    echo "📥 Reading snapshot metadata to find associated indices..."
    # Get the list of indices from the snapshot metadata
    INDICES=$(kubectl exec $POD_NAME -n $NAMESPACE -c elasticsearch -- cat $LATEST_META | grep -o '"[^"]*"' | grep -E '^"[A-Za-z0-9_-]+Index"' | tr -d '"' | sed 's/Index$//' || echo "")

    if [ -z "$INDICES" ]; then
        echo "⚠️ Could not parse indices from metadata, copying entire indices directory..."
        echo "  → This may take several minutes depending on data size..."
        kubectl cp $NAMESPACE/$POD_NAME:$BACKUP_PATH/indices $TEMP_DIR/backup/indices -c elasticsearch -v=2
    else
        echo "📥 Found indices in snapshot: $INDICES"
        echo "📥 Copying indices directory (this may take a while)..."
        echo "  → This may take several minutes depending on data size..."
        
        # Copy the entire indices directory for the snapshot
        kubectl cp $NAMESPACE/$POD_NAME:$BACKUP_PATH/indices $TEMP_DIR/backup/indices -c elasticsearch -v=2
    fi

    echo "📊 Checking copied data size..."
    du -sh $TEMP_DIR/backup/

    echo "✅ Latest snapshot with indices copied"

    if [ ! -d "$TEMP_DIR/backup" ]; then
        echo "❌ Failed to copy backup files"
        exit 1
    fi

    echo "✅ Backup files copied successfully"
    ls -la $TEMP_DIR/backup/

    # Step 4: Create S3 bucket and upload files
    echo "☁️ Creating S3 bucket and uploading files..."
    aws s3 mb s3://$S3_BUCKET --region us-east-1 || echo "Bucket may already exist"
    echo "  → Uploading to s3://$S3_BUCKET/$S3_PREFIX/ (progress will be shown)..."
    aws s3 sync $TEMP_DIR/backup/ s3://$S3_BUCKET/$S3_PREFIX/ --region us-east-1

    echo "✅ Files uploaded to S3"
fi

# Step 5: Configure OpenSearch repository (public domain)
echo "🔧 Configuring OpenSearch snapshot repository..."

if [ -z "$OPENSEARCH_ENDPOINT" ]; then
    echo "❌ No OpenSearch endpoint found. Deploy the public OpenSearch stack first:"
    echo "   cdk deploy OpenSearchStack-dev"
    exit 1
fi

# Create repository using AWS CLI with proper signing
python3 << EOF
import boto3
import json
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import time

print("🔧 Setting up repository on public OpenSearch domain...")

session = boto3.Session()
credentials = session.get_credentials()

# Get the OpenSearch service role ARN from CloudFormation outputs
import subprocess
try:
    role_arn = subprocess.check_output([
        "aws", "cloudformation", "describe-stacks", "--stack-name", "OpenSearchStack-dev",
        "--query", "Stacks[0].Outputs[?OutputKey=='OpenSearchServiceRoleArn'].OutputValue | [0]",
        "--output", "text"
    ], text=True).strip()
    print(f"🔑 Using OpenSearch service role: {role_arn}")
except:
    # Fallback: try to find the role by pattern
    try:
        role_arn = subprocess.check_output([
            "aws", "iam", "list-roles", "--query", 
            "Roles[?contains(RoleName, 'OpenSearchServiceRole')].Arn | [0]", 
            "--output", "text"
        ], text=True).strip()
        print(f"🔑 Found service role: {role_arn}")
    except:
        print("❌ Could not find OpenSearch service role")
        role_arn = None

repo_config = {
    "type": "s3",
    "settings": {
        "bucket": "$S3_BUCKET",
        "base_path": "$S3_PREFIX",
        "region": "us-east-1"
    }
}

if role_arn and role_arn != "None":
    repo_config["settings"]["role_arn"] = role_arn

url = "https://$OPENSEARCH_ENDPOINT/_snapshot/$REPO_NAME"
request = AWSRequest(method='PUT', url=url, data=json.dumps(repo_config))
request.headers['Content-Type'] = 'application/json'

SigV4Auth(credentials, 'es', 'us-east-1').add_auth(request)

try:
    response = requests.put(url, data=request.body, headers=dict(request.headers), timeout=30)
    if response.status_code in [200, 201]:
        print("✅ Repository configured successfully")
    else:
        print(f"⚠️ Repository setup response: {response.status_code} - {response.text}")
except Exception as e:
    print(f"⚠️ Could not configure repository automatically: {e}")
    print("📋 Manual setup required - see instructions below")

EOF

# Step 6: Migration Summary
echo "📋 Migration Summary:"
echo "===================="
if [ "$SKIP_BACKUP" = true ]; then
    echo "✅ Using existing S3 data: s3://$S3_BUCKET/$S3_PREFIX/"
    echo "✅ Latest snapshot: $(basename $LATEST_SNAP)"
else
    echo "✅ Snapshot copied from K8s: $(basename $LATEST_SNAP)"
    echo "✅ Data size: $(du -sh $TEMP_DIR/backup/ | cut -f1)"
    echo "✅ Files uploaded to S3: s3://$S3_BUCKET/$S3_PREFIX/"
fi
echo "✅ Repository config ready"
echo ""
# Step 6: Attempt automatic restore (public domain)
echo ""
echo "🚀 Attempting automatic snapshot restore..."

python3 << EOF
import boto3
import json
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import time

session = boto3.Session()
credentials = session.get_credentials()

# List snapshots
print("📋 Listing available snapshots...")
url = "https://$OPENSEARCH_ENDPOINT/_snapshot/$REPO_NAME/_all"
request = AWSRequest(method='GET', url=url)
SigV4Auth(credentials, 'es', 'us-east-1').add_auth(request)

try:
    response = requests.get(url, headers=dict(request.headers), timeout=30)
    if response.status_code == 200:
        snapshots = response.json().get('snapshots', [])
        print(f"✅ Found {len(snapshots)} snapshots")
        
        if snapshots:
            # Get the latest snapshot
            latest_snapshot = snapshots[-1]['snapshot']
            print(f"📸 Latest snapshot: {latest_snapshot}")
            
            # Restore the snapshot
            restore_config = {
                "indices": "*",
                "ignore_unavailable": True,
                "include_global_state": False,
                "rename_pattern": "(.+)",
                "rename_replacement": "migrated_\$1"
            }
            
            restore_url = f"https://$OPENSEARCH_ENDPOINT/_snapshot/$REPO_NAME/{latest_snapshot}/_restore"
            restore_request = AWSRequest(method='POST', url=restore_url, data=json.dumps(restore_config))
            restore_request.headers['Content-Type'] = 'application/json'
            SigV4Auth(credentials, 'es', 'us-east-1').add_auth(restore_request)
            
            restore_response = requests.post(restore_url, data=restore_request.body, headers=dict(restore_request.headers), timeout=30)
            
            if restore_response.status_code in [200, 202]:
                print("✅ Snapshot restore initiated successfully!")
                print("📊 Indices will be restored with 'migrated_' prefix")
            else:
                print(f"⚠️ Restore failed: {restore_response.status_code} - {restore_response.text}")
        else:
            print("❌ No snapshots found in repository")
    else:
        print(f"⚠️ Could not list snapshots: {response.status_code}")
        
except Exception as e:
    print(f"⚠️ Automatic restore failed: {e}")

EOF

echo ""
echo "🌐 OpenSearch Dashboards: https://$OPENSEARCH_ENDPOINT/_dashboards/"

# Step 7: Clean up
echo ""
echo "🧹 Cleaning up temporary files..."
rm -rf $TEMP_DIR

echo ""
echo "🎉 Migration completed successfully!"
