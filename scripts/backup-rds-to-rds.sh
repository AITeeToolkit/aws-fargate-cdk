#!/bin/bash

# RDS to RDS Backup Script
# This script creates a backup from one RDS instance and restores it to another
# Supports both pg_dump/restore and AWS snapshot methods

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
    
    if ! command -v psql &> /dev/null; then
        print_error "psql is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v pg_dump &> /dev/null; then
        print_error "pg_dump is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed or not in PATH"
        exit 1
    fi
    
    print_success "All dependencies are installed"
}

# Function to get RDS credentials from AWS Secrets Manager
get_rds_credentials() {
    local secret_arn=$1
    local region=${2:-us-east-1}
    
    aws secretsmanager get-secret-value \
        --secret-id "$secret_arn" \
        --region "$region" \
        --query SecretString \
        --output text
    
    if [ $? -ne 0 ]; then
        print_error "Failed to fetch credentials from Secrets Manager"
        exit 1
    fi
}

# Function to backup using pg_dump
backup_with_pg_dump() {
    local source_host=$1
    local source_port=$2
    local source_db=$3
    local source_user=$4
    local source_password=$5
    local backup_file=$6
    
    print_status "Starting backup from $source_host:$source_port/$source_db"
    print_status "Backup file: $backup_file"
    
    export PGPASSWORD="$source_password"
    
    pg_dump \
        --host="$source_host" \
        --port="$source_port" \
        --username="$source_user" \
        --dbname="$source_db" \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="$backup_file"
    
    if [ $? -eq 0 ]; then
        print_success "Backup completed successfully"
        local backup_size=$(du -h "$backup_file" | cut -f1)
        print_status "Backup size: $backup_size"
    else
        print_error "Backup failed"
        exit 1
    fi
    
    unset PGPASSWORD
}

# Function to restore using pg_restore
restore_with_pg_restore() {
    local target_host=$1
    local target_port=$2
    local target_db=$3
    local target_user=$4
    local target_password=$5
    local backup_file=$6
    local clean_first=${7:-false}
    
    print_status "Starting restore to $target_host:$target_port/$target_db"
    
    export PGPASSWORD="$target_password"
    
    # Check if database exists
    local db_exists=$(psql \
        --host="$target_host" \
        --port="$target_port" \
        --username="$target_user" \
        --dbname="postgres" \
        --tuples-only \
        --command="SELECT 1 FROM pg_database WHERE datname='$target_db';" | xargs)
    
    if [ "$db_exists" != "1" ]; then
        print_status "Database $target_db does not exist, creating..."
        psql \
            --host="$target_host" \
            --port="$target_port" \
            --username="$target_user" \
            --dbname="postgres" \
            --command="CREATE DATABASE \"$target_db\";"
        
        if [ $? -eq 0 ]; then
            print_success "Database created successfully"
        else
            print_error "Failed to create database"
            exit 1
        fi
    fi
    
    # Clean database if requested
    if [ "$clean_first" = true ]; then
        print_warning "Cleaning target database before restore..."
        pg_restore \
            --host="$target_host" \
            --port="$target_port" \
            --username="$target_user" \
            --dbname="$target_db" \
            --clean \
            --if-exists \
            --verbose \
            "$backup_file" 2>&1 | grep -v "ERROR"
    fi
    
    # Restore the backup
    pg_restore \
        --host="$target_host" \
        --port="$target_port" \
        --username="$target_user" \
        --dbname="$target_db" \
        --no-owner \
        --no-acl \
        --verbose \
        "$backup_file"
    
    if [ $? -eq 0 ]; then
        print_success "Restore completed successfully"
    else
        print_warning "Restore completed with some errors (this is normal for existing objects)"
    fi
    
    unset PGPASSWORD
}

# Function to create AWS RDS snapshot
create_rds_snapshot() {
    local db_instance_id=$1
    local snapshot_id=$2
    local region=${3:-us-east-1}
    
    print_status "Creating RDS snapshot: $snapshot_id"
    
    aws rds create-db-snapshot \
        --db-instance-identifier "$db_instance_id" \
        --db-snapshot-identifier "$snapshot_id" \
        --region "$region"
    
    if [ $? -eq 0 ]; then
        print_success "Snapshot creation initiated"
        print_status "Waiting for snapshot to complete..."
        
        aws rds wait db-snapshot-completed \
            --db-snapshot-identifier "$snapshot_id" \
            --region "$region"
        
        print_success "Snapshot completed: $snapshot_id"
    else
        print_error "Failed to create snapshot"
        exit 1
    fi
}

# Function to restore RDS from snapshot
restore_rds_from_snapshot() {
    local snapshot_id=$1
    local new_instance_id=$2
    local instance_class=$3
    local region=${4:-us-east-1}
    
    print_status "Restoring RDS instance from snapshot: $snapshot_id"
    print_status "New instance ID: $new_instance_id"
    
    aws rds restore-db-instance-from-db-snapshot \
        --db-instance-identifier "$new_instance_id" \
        --db-snapshot-identifier "$snapshot_id" \
        --db-instance-class "$instance_class" \
        --region "$region"
    
    if [ $? -eq 0 ]; then
        print_success "Restore initiated"
        print_status "Waiting for instance to become available..."
        
        aws rds wait db-instance-available \
            --db-instance-identifier "$new_instance_id" \
            --region "$region"
        
        print_success "Instance is now available: $new_instance_id"
    else
        print_error "Failed to restore from snapshot"
        exit 1
    fi
}

# Main script
main() {
    print_status "=== RDS to RDS Backup Script ==="
    
    # Parse command line arguments
    METHOD=${1:-pg_dump}  # pg_dump or snapshot
    
    case $METHOD in
        pg_dump)
            print_status "Using pg_dump method"
            
            # Source RDS configuration
            SOURCE_HOST=${SOURCE_HOST:-""}
            SOURCE_PORT=${SOURCE_PORT:-5432}
            SOURCE_DB=${SOURCE_DB:-"storefront"}
            SOURCE_USER=${SOURCE_USER:-"postgres"}
            SOURCE_PASSWORD=${SOURCE_PASSWORD:-""}
            SOURCE_SECRET_ARN=${SOURCE_SECRET_ARN:-""}
            
            # Target RDS configuration
            TARGET_HOST=${TARGET_HOST:-""}
            TARGET_PORT=${TARGET_PORT:-5432}
            TARGET_DB=${TARGET_DB:-"storefront"}
            TARGET_USER=${TARGET_USER:-"postgres"}
            TARGET_PASSWORD=${TARGET_PASSWORD:-""}
            TARGET_SECRET_ARN=${TARGET_SECRET_ARN:-""}
            
            # Backup file
            BACKUP_FILE=${BACKUP_FILE:-"/tmp/rds_backup_$(date +%Y%m%d_%H%M%S).dump"}
            CLEAN_FIRST=${CLEAN_FIRST:-false}
            
            # Get credentials from Secrets Manager if provided (do this BEFORE validation)
            if [ -n "$SOURCE_SECRET_ARN" ]; then
                print_status "Fetching source credentials from Secrets Manager"
                SOURCE_CREDS=$(get_rds_credentials "$SOURCE_SECRET_ARN")
                SOURCE_USER=$(echo "$SOURCE_CREDS" | jq -r .username)
                SOURCE_PASSWORD=$(echo "$SOURCE_CREDS" | jq -r .password)
                SOURCE_HOST=$(echo "$SOURCE_CREDS" | jq -r .host)
                SOURCE_PORT=$(echo "$SOURCE_CREDS" | jq -r .port)
            fi
            
            if [ -n "$TARGET_SECRET_ARN" ]; then
                print_status "Fetching target credentials from Secrets Manager"
                TARGET_CREDS=$(get_rds_credentials "$TARGET_SECRET_ARN")
                TARGET_USER=$(echo "$TARGET_CREDS" | jq -r .username)
                TARGET_PASSWORD=$(echo "$TARGET_CREDS" | jq -r .password)
                TARGET_HOST=$(echo "$TARGET_CREDS" | jq -r .host)
                TARGET_PORT=$(echo "$TARGET_CREDS" | jq -r .port)
            fi
            
            # Validate required parameters (after fetching from Secrets Manager)
            if [ -z "$SOURCE_HOST" ]; then
                print_error "SOURCE_HOST is required (set SOURCE_HOST or SOURCE_SECRET_ARN)"
                exit 1
            fi
            
            if [ -z "$TARGET_HOST" ]; then
                print_error "TARGET_HOST is required (set TARGET_HOST or TARGET_SECRET_ARN)"
                exit 1
            fi
            
            check_dependencies
            
            # Perform backup
            backup_with_pg_dump \
                "$SOURCE_HOST" \
                "$SOURCE_PORT" \
                "$SOURCE_DB" \
                "$SOURCE_USER" \
                "$SOURCE_PASSWORD" \
                "$BACKUP_FILE"
            
            # Perform restore
            restore_with_pg_restore \
                "$TARGET_HOST" \
                "$TARGET_PORT" \
                "$TARGET_DB" \
                "$TARGET_USER" \
                "$TARGET_PASSWORD" \
                "$BACKUP_FILE" \
                "$CLEAN_FIRST"
            
            # Cleanup
            print_status "Cleaning up backup file..."
            rm -f "$BACKUP_FILE"
            print_success "Backup file removed"
            ;;
            
        snapshot)
            print_status "Using AWS snapshot method"
            
            SOURCE_INSTANCE_ID=${SOURCE_INSTANCE_ID:-""}
            SNAPSHOT_ID=${SNAPSHOT_ID:-"backup-$(date +%Y%m%d-%H%M%S)"}
            TARGET_INSTANCE_ID=${TARGET_INSTANCE_ID:-""}
            INSTANCE_CLASS=${INSTANCE_CLASS:-"db.t3.micro"}
            AWS_REGION=${AWS_REGION:-"us-east-1"}
            
            if [ -z "$SOURCE_INSTANCE_ID" ]; then
                print_error "SOURCE_INSTANCE_ID is required"
                exit 1
            fi
            
            if [ -z "$TARGET_INSTANCE_ID" ]; then
                print_error "TARGET_INSTANCE_ID is required"
                exit 1
            fi
            
            check_dependencies
            
            # Create snapshot
            create_rds_snapshot "$SOURCE_INSTANCE_ID" "$SNAPSHOT_ID" "$AWS_REGION"
            
            # Restore from snapshot
            restore_rds_from_snapshot "$SNAPSHOT_ID" "$TARGET_INSTANCE_ID" "$INSTANCE_CLASS" "$AWS_REGION"
            ;;
            
        *)
            print_error "Invalid method: $METHOD"
            echo "Usage: $0 [pg_dump|snapshot]"
            echo ""
            echo "pg_dump method environment variables:"
            echo "  SOURCE_HOST, SOURCE_PORT, SOURCE_DB, SOURCE_USER, SOURCE_PASSWORD"
            echo "  TARGET_HOST, TARGET_PORT, TARGET_DB, TARGET_USER, TARGET_PASSWORD"
            echo "  SOURCE_SECRET_ARN, TARGET_SECRET_ARN (optional, for Secrets Manager)"
            echo "  BACKUP_FILE (optional, default: /tmp/rds_backup_TIMESTAMP.dump)"
            echo "  CLEAN_FIRST (optional, default: false)"
            echo ""
            echo "snapshot method environment variables:"
            echo "  SOURCE_INSTANCE_ID, TARGET_INSTANCE_ID"
            echo "  SNAPSHOT_ID (optional, default: backup-TIMESTAMP)"
            echo "  INSTANCE_CLASS (optional, default: db.t3.micro)"
            echo "  AWS_REGION (optional, default: us-east-1)"
            exit 1
            ;;
    esac
    
    print_success "=== Backup completed successfully ==="
}

# Run main function
main "$@"
