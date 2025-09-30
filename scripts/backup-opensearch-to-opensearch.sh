#!/bin/bash

# OpenSearch to OpenSearch Backup Script
# This script creates a backup from one OpenSearch domain and restores it to another
# Supports both snapshot and direct reindex methods

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed or not in PATH"
        exit 1
    fi
    
    print_success "All dependencies are installed"
}

# Function to sign OpenSearch requests with AWS SigV4
sign_request() {
    local method=$1
    local endpoint=$2
    local path=$3
    local data=$4
    local region=${5:-us-east-1}
    
    if [ -n "$data" ]; then
        aws opensearch-serverless sign-request \
            --method "$method" \
            --endpoint "$endpoint" \
            --path "$path" \
            --region "$region" \
            --data "$data"
    else
        aws opensearch-serverless sign-request \
            --method "$method" \
            --endpoint "$endpoint" \
            --path "$path" \
            --region "$region"
    fi
}

# Function to make authenticated request to OpenSearch
opensearch_request() {
    local method=$1
    local endpoint=$2
    local path=$3
    local data=$4
    local region=${5:-us-east-1}
    
    local url="https://${endpoint}${path}"
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "$url" \
            -H "Content-Type: application/json" \
            --aws-sigv4 "aws:amz:${region}:es" \
            --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
            -d "$data"
    else
        curl -s -X "$method" "$url" \
            -H "Content-Type: application/json" \
            --aws-sigv4 "aws:amz:${region}:es" \
            --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"
    fi
}

# Function to list all indices
list_indices() {
    local endpoint=$1
    local region=${2:-us-east-1}
    
    print_status "Listing indices from $endpoint"
    
    opensearch_request "GET" "$endpoint" "/_cat/indices?format=json" "" "$region" | \
        jq -r '.[] | select(.index | startswith(".") | not) | .index'
}

# Function to create snapshot repository (S3-based)
create_snapshot_repository() {
    local endpoint=$1
    local repo_name=$2
    local s3_bucket=$3
    local region=${4:-us-east-1}
    
    print_status "Creating snapshot repository: $repo_name"
    
    local repo_config=$(cat <<EOF
{
  "type": "s3",
  "settings": {
    "bucket": "$s3_bucket",
    "region": "$region",
    "role_arn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/OpenSearchSnapshotRole"
  }
}
EOF
)
    
    opensearch_request "PUT" "$endpoint" "/_snapshot/$repo_name" "$repo_config" "$region"
}

# Function to create snapshot
create_snapshot() {
    local endpoint=$1
    local repo_name=$2
    local snapshot_name=$3
    local indices=$4
    local region=${5:-us-east-1}
    
    print_status "Creating snapshot: $snapshot_name"
    
    local snapshot_config=$(cat <<EOF
{
  "indices": "$indices",
  "ignore_unavailable": true,
  "include_global_state": false
}
EOF
)
    
    opensearch_request "PUT" "$endpoint" "/_snapshot/$repo_name/$snapshot_name" "$snapshot_config" "$region"
    
    # Wait for snapshot to complete
    print_status "Waiting for snapshot to complete..."
    while true; do
        local status=$(opensearch_request "GET" "$endpoint" "/_snapshot/$repo_name/$snapshot_name" "" "$region" | \
            jq -r '.snapshots[0].state')
        
        if [ "$status" = "SUCCESS" ]; then
            print_success "Snapshot completed successfully"
            break
        elif [ "$status" = "FAILED" ]; then
            print_error "Snapshot failed"
            exit 1
        fi
        
        sleep 5
    done
}

# Function to restore snapshot
restore_snapshot() {
    local endpoint=$1
    local repo_name=$2
    local snapshot_name=$3
    local indices=$4
    local region=${5:-us-east-1}
    
    print_status "Restoring snapshot: $snapshot_name"
    
    local restore_config=$(cat <<EOF
{
  "indices": "$indices",
  "ignore_unavailable": true,
  "include_global_state": false
}
EOF
)
    
    opensearch_request "POST" "$endpoint" "/_snapshot/$repo_name/$snapshot_name/_restore" "$restore_config" "$region"
    
    print_success "Restore initiated"
}

# Function to reindex from remote (direct copy)
reindex_from_remote() {
    local source_endpoint=$1
    local target_endpoint=$2
    local index=$3
    local region=${4:-us-east-1}
    
    print_status "Reindexing $index from $source_endpoint to $target_endpoint"
    
    local reindex_config=$(cat <<EOF
{
  "source": {
    "remote": {
      "host": "https://$source_endpoint"
    },
    "index": "$index"
  },
  "dest": {
    "index": "$index"
  }
}
EOF
)
    
    local response=$(opensearch_request "POST" "$target_endpoint" "/_reindex" "$reindex_config" "$region")
    
    local total=$(echo "$response" | jq -r '.total')
    local created=$(echo "$response" | jq -r '.created')
    
    print_success "Reindexed $created/$total documents for index: $index"
}

# Function to backup using scroll API and bulk insert
backup_with_scroll() {
    local source_endpoint=$1
    local target_endpoint=$2
    local index=$3
    local region=${4:-us-east-1}
    local batch_size=${5:-1000}
    
    print_status "Backing up index: $index using scroll API"
    
    # Initialize scroll
    local scroll_response=$(opensearch_request "GET" "$source_endpoint" "/$index/_search?scroll=5m" \
        "{\"size\": $batch_size, \"query\": {\"match_all\": {}}}" "$region")
    
    local scroll_id=$(echo "$scroll_response" | jq -r '._scroll_id')
    local total_hits=$(echo "$scroll_response" | jq -r '.hits.total.value')
    
    print_status "Total documents to backup: $total_hits"
    
    local processed=0
    
    while true; do
        local hits=$(echo "$scroll_response" | jq -r '.hits.hits | length')
        
        if [ "$hits" -eq 0 ]; then
            break
        fi
        
        # Prepare bulk insert
        local bulk_data=$(echo "$scroll_response" | jq -r '.hits.hits[] | 
            "{\"index\": {\"_index\": \"'$index'\", \"_id\": \"" + ._id + "\"}}\n" + (._source | tostring)')
        
        # Insert into target
        echo "$bulk_data" | opensearch_request "POST" "$target_endpoint" "/_bulk" "" "$region" > /dev/null
        
        processed=$((processed + hits))
        print_status "Processed: $processed/$total_hits documents"
        
        # Get next batch
        scroll_response=$(opensearch_request "POST" "$source_endpoint" "/_search/scroll" \
            "{\"scroll\": \"5m\", \"scroll_id\": \"$scroll_id\"}" "$region")
    done
    
    # Clear scroll
    opensearch_request "DELETE" "$source_endpoint" "/_search/scroll" \
        "{\"scroll_id\": \"$scroll_id\"}" "$region" > /dev/null
    
    print_success "Completed backup of index: $index ($processed documents)"
}

# Main script
main() {
    print_status "=== OpenSearch to OpenSearch Backup Script ==="
    
    # Parse command line arguments
    METHOD=${1:-scroll}  # scroll, reindex, or snapshot
    
    case $METHOD in
        scroll)
            print_status "Using scroll API method (direct copy)"
            
            SOURCE_ENDPOINT=${SOURCE_ENDPOINT:-""}
            TARGET_ENDPOINT=${TARGET_ENDPOINT:-""}
            INDICES=${INDICES:-"*"}
            AWS_REGION=${AWS_REGION:-"us-east-1"}
            BATCH_SIZE=${BATCH_SIZE:-1000}
            
            if [ -z "$SOURCE_ENDPOINT" ]; then
                print_error "SOURCE_ENDPOINT is required"
                exit 1
            fi
            
            if [ -z "$TARGET_ENDPOINT" ]; then
                print_error "TARGET_ENDPOINT is required"
                exit 1
            fi
            
            check_dependencies
            
            # Get list of indices to backup
            if [ "$INDICES" = "*" ]; then
                print_status "Getting list of all indices from source..."
                INDICES_LIST=$(list_indices "$SOURCE_ENDPOINT" "$AWS_REGION")
            else
                INDICES_LIST="$INDICES"
            fi
            
            # Backup each index
            for index in $INDICES_LIST; do
                backup_with_scroll "$SOURCE_ENDPOINT" "$TARGET_ENDPOINT" "$index" "$AWS_REGION" "$BATCH_SIZE"
            done
            ;;
            
        reindex)
            print_status "Using reindex from remote method"
            
            SOURCE_ENDPOINT=${SOURCE_ENDPOINT:-""}
            TARGET_ENDPOINT=${TARGET_ENDPOINT:-""}
            INDICES=${INDICES:-"*"}
            AWS_REGION=${AWS_REGION:-"us-east-1"}
            
            if [ -z "$SOURCE_ENDPOINT" ]; then
                print_error "SOURCE_ENDPOINT is required"
                exit 1
            fi
            
            if [ -z "$TARGET_ENDPOINT" ]; then
                print_error "TARGET_ENDPOINT is required"
                exit 1
            fi
            
            check_dependencies
            
            # Get list of indices
            if [ "$INDICES" = "*" ]; then
                print_status "Getting list of all indices from source..."
                INDICES_LIST=$(list_indices "$SOURCE_ENDPOINT" "$AWS_REGION")
            else
                INDICES_LIST="$INDICES"
            fi
            
            # Reindex each index
            for index in $INDICES_LIST; do
                reindex_from_remote "$SOURCE_ENDPOINT" "$TARGET_ENDPOINT" "$index" "$AWS_REGION"
            done
            ;;
            
        snapshot)
            print_status "Using S3 snapshot method"
            
            SOURCE_ENDPOINT=${SOURCE_ENDPOINT:-""}
            TARGET_ENDPOINT=${TARGET_ENDPOINT:-""}
            S3_BUCKET=${S3_BUCKET:-""}
            SNAPSHOT_REPO=${SNAPSHOT_REPO:-"backup-repo"}
            SNAPSHOT_NAME=${SNAPSHOT_NAME:-"backup-$(date +%Y%m%d-%H%M%S)"}
            INDICES=${INDICES:-"*"}
            AWS_REGION=${AWS_REGION:-"us-east-1"}
            AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-""}
            
            if [ -z "$SOURCE_ENDPOINT" ]; then
                print_error "SOURCE_ENDPOINT is required"
                exit 1
            fi
            
            if [ -z "$TARGET_ENDPOINT" ]; then
                print_error "TARGET_ENDPOINT is required"
                exit 1
            fi
            
            if [ -z "$S3_BUCKET" ]; then
                print_error "S3_BUCKET is required for snapshot method"
                exit 1
            fi
            
            if [ -z "$AWS_ACCOUNT_ID" ]; then
                print_error "AWS_ACCOUNT_ID is required for snapshot method"
                exit 1
            fi
            
            check_dependencies
            
            # Create snapshot repository on source
            create_snapshot_repository "$SOURCE_ENDPOINT" "$SNAPSHOT_REPO" "$S3_BUCKET" "$AWS_REGION"
            
            # Create snapshot
            create_snapshot "$SOURCE_ENDPOINT" "$SNAPSHOT_REPO" "$SNAPSHOT_NAME" "$INDICES" "$AWS_REGION"
            
            # Create snapshot repository on target
            create_snapshot_repository "$TARGET_ENDPOINT" "$SNAPSHOT_REPO" "$S3_BUCKET" "$AWS_REGION"
            
            # Restore snapshot
            restore_snapshot "$TARGET_ENDPOINT" "$SNAPSHOT_REPO" "$SNAPSHOT_NAME" "$INDICES" "$AWS_REGION"
            ;;
            
        *)
            print_error "Invalid method: $METHOD"
            echo "Usage: $0 [scroll|reindex|snapshot]"
            echo ""
            echo "scroll method (recommended for most cases):"
            echo "  SOURCE_ENDPOINT=source.us-east-1.es.amazonaws.com"
            echo "  TARGET_ENDPOINT=target.us-east-1.es.amazonaws.com"
            echo "  INDICES='index1,index2' or '*' for all"
            echo "  BATCH_SIZE=1000 (optional)"
            echo ""
            echo "reindex method (built-in OpenSearch reindex):"
            echo "  SOURCE_ENDPOINT=source.us-east-1.es.amazonaws.com"
            echo "  TARGET_ENDPOINT=target.us-east-1.es.amazonaws.com"
            echo "  INDICES='index1,index2' or '*' for all"
            echo ""
            echo "snapshot method (S3-based):"
            echo "  SOURCE_ENDPOINT=source.us-east-1.es.amazonaws.com"
            echo "  TARGET_ENDPOINT=target.us-east-1.es.amazonaws.com"
            echo "  S3_BUCKET=my-opensearch-snapshots"
            echo "  AWS_ACCOUNT_ID=123456789012"
            echo "  SNAPSHOT_REPO=backup-repo (optional)"
            echo "  SNAPSHOT_NAME=backup-20250930 (optional)"
            echo "  INDICES='*' (optional)"
            exit 1
            ;;
    esac
    
    print_success "=== Backup completed successfully ==="
}

# Run main function
main "$@"
