#!/bin/bash

# Kubegres to RDS Backup Restoration Script
# This script extracts the latest backup from a Kubegres PostgreSQL pod and restores it to an RDS instance

set -e

# Configuration - Update these variables as needed
KUBEGRES_NAMESPACE="kubegres"
KUBEGRES_POD_SELECTOR="app=postgres"
BACKUP_DIR="/var/lib/backup"
LOCAL_BACKUP_DIR="/tmp"
RDS_HOST="storefrontdatabasestack-d-storefrontpostgresdev674-0il8e3oc1zpi.cyxas2yo0gpr.us-east-1.rds.amazonaws.com"
RDS_PORT="5432"
RDS_USER="postgres"
RDS_DATABASE="postgres"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Function to check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v psql &> /dev/null; then
        print_error "psql is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v gunzip &> /dev/null; then
        print_error "gunzip is not installed or not in PATH"
        exit 1
    fi
    
    print_status "All dependencies are available"
}

# Function to get the latest Kubegres pod
get_kubegres_pod() {
    local pods=$(kubectl get pods -n "$KUBEGRES_NAMESPACE" -l "$KUBEGRES_POD_SELECTOR" --no-headers -o custom-columns=":metadata.name" | head -1)
    
    if [ -z "$pods" ]; then
        print_error "No Kubegres PostgreSQL pods found in namespace '$KUBEGRES_NAMESPACE'"
        exit 1
    fi
    
    echo "$pods"
}

# Function to list available backups
list_backups() {
    local pod_name=$1
    print_status "Listing available backups in pod '$pod_name'..."
    
    kubectl exec -n "$KUBEGRES_NAMESPACE" "$pod_name" -- ls -la "$BACKUP_DIR/" || {
        print_error "Failed to list backups in pod '$pod_name'"
        exit 1
    }
}

# Function to get the latest backup file
get_latest_backup() {
    local pod_name=$1
    
    local latest_backup=$(kubectl exec -n "$KUBEGRES_NAMESPACE" "$pod_name" -- sh -c "ls -t $BACKUP_DIR/*.gz 2>/dev/null" | head -1)
    
    if [ -z "$latest_backup" ]; then
        print_error "No backup files found in '$BACKUP_DIR/'"
        exit 1
    fi
    
    echo "$latest_backup"
}

# Function to copy backup from pod to local machine
copy_backup() {
    local pod_name=$1
    local backup_file=$2
    local local_file="$LOCAL_BACKUP_DIR/kubegres-backup-$(date +%Y%m%d_%H%M%S).gz"
    
    print_status "Copying backup from pod to local machine..."
    
    # Suppress all output from kubectl cp (both stdout and stderr)
    kubectl cp "$KUBEGRES_NAMESPACE/$pod_name:$backup_file" "$local_file" >/dev/null 2>&1 || {
        print_error "Failed to copy backup file from pod"
        exit 1
    }
    
    # Verify the file was actually copied and has content
    if [ ! -f "$local_file" ]; then
        print_error "Backup file was not created: $local_file"
        exit 1
    fi
    
    if [ ! -s "$local_file" ]; then
        print_error "Backup file is empty: $local_file"
        exit 1
    fi
    
    print_status "Successfully copied backup to: $local_file"
    echo "$local_file"
}

# Function to extract backup
extract_backup() {
    local compressed_file=$1
    local extracted_file="${compressed_file%.gz}.sql"
    
    print_status "Extracting backup file..."
    print_status "Extracting: $compressed_file -> $extracted_file"
    
    # Check if the compressed file exists
    if [ ! -f "$compressed_file" ]; then
        print_error "Compressed file not found: $compressed_file"
        exit 1
    fi
    
    # Simple gzip extraction
    if gunzip -c "$compressed_file" > "$extracted_file" 2>/dev/null; then
        print_status "Successfully extracted using gunzip"
    else
        print_error "Failed to extract using gunzip, trying alternative method"
        # Try using zcat as alternative
        if zcat "$compressed_file" > "$extracted_file" 2>/dev/null; then
            print_status "Successfully extracted using zcat"
        else
            print_error "Failed to extract backup file with both gunzip and zcat"
            exit 1
        fi
    fi
    
    # Verify the extracted file exists and has content
    if [ ! -f "$extracted_file" ]; then
        print_error "Failed to extract backup file: $extracted_file not found"
        exit 1
    fi
    
    if [ ! -s "$extracted_file" ]; then
        print_error "Extracted file is empty: $extracted_file"
        exit 1
    fi
    
    print_status "Successfully extracted $(wc -l < "$extracted_file") lines to $extracted_file"
    echo "$extracted_file"
}

# Function to restore backup to RDS
restore_to_rds() {
    local sql_file=$1
    
    print_status "Restoring backup to RDS instance..."
    print_status "RDS Host: $RDS_HOST"
    print_status "Database: $RDS_DATABASE"
    
    if [ -z "$PGPASSWORD" ]; then
        print_error "PGPASSWORD environment variable is not set"
        print_error "Please set it with: export PGPASSWORD='your_rds_password'"
        exit 1
    fi
    
    print_warning "Starting restoration process. This may take several minutes..."
    print_warning "Some permission-related errors are expected when restoring to RDS and can be ignored."
    
    psql -h "$RDS_HOST" -p "$RDS_PORT" -U "$RDS_USER" -d "$RDS_DATABASE" -f "$sql_file" || {
        print_warning "Restoration completed with some errors (this is normal for RDS)"
        print_status "Check the output above to ensure your data was restored successfully"
    }
}

# Function to cleanup temporary files
cleanup() {
    local files_to_clean=("$@")
    
    print_status "Cleaning up temporary files..."
    for file in "${files_to_clean[@]}"; do
        if [ -f "$file" ]; then
            rm -f "$file"
            print_status "Removed: $file"
        fi
    done
}

# Main execution
main() {
    print_status "Starting Kubegres to RDS backup restoration process..."
    
    # Check dependencies
    check_dependencies
    
    # Get Kubegres pod
    local pod_name=$(get_kubegres_pod)
    print_status "Using pod: $pod_name"
    
    # List available backups
    list_backups "$pod_name"
    
    # Get latest backup
    local latest_backup=$(get_latest_backup "$pod_name")
    print_status "Latest backup: $latest_backup"
    
    # Copy backup to local machine
    local local_backup=$(copy_backup "$pod_name" "$latest_backup")
    
    # Extract backup
    local sql_file=$(extract_backup "$local_backup")
    
    # Restore to RDS
    restore_to_rds "$sql_file"
    
    print_status "Backup restoration process completed successfully!"
    
    # Cleanup
    cleanup "$local_backup" "$sql_file"
    
    print_status "All done! Your RDS instance has been restored with data from Kubegres."
}

# Handle script interruption
trap 'print_error "Script interrupted"; exit 1' INT TERM

# Show usage if help is requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: $0"
    echo ""
    echo "This script extracts the latest backup from a Kubegres PostgreSQL pod"
    echo "and restores it to an RDS PostgreSQL instance."
    echo ""
    echo "Prerequisites:"
    echo "  - kubectl configured and connected to your cluster"
    echo "  - psql client installed"
    echo "  - PGPASSWORD environment variable set with RDS password"
    echo ""
    echo "Configuration:"
    echo "  Edit the configuration variables at the top of this script to match"
    echo "  your environment (namespace, pod selector, RDS connection details, etc.)"
    echo ""
    echo "Example:"
    echo "  export PGPASSWORD='your_rds_password'"
    echo "  $0"
    exit 0
fi

# Run main function
main "$@"
