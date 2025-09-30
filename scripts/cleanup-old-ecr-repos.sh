#!/bin/bash

# Cleanup script to delete old environment-specific ECR repositories
# Run this AFTER verifying the new shared repositories work correctly

set -e

AWS_REGION="us-east-1"
SERVICES=("api" "web" "listener" "dns-worker")
OLD_ENV="dev"

echo "⚠️  WARNING: This will DELETE old ECR repositories!"
echo "📍 Region: $AWS_REGION"
echo "🗑️  Repositories to delete:"
for service in "${SERVICES[@]}"; do
    echo "    - storefront/$OLD_ENV/$service"
done
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🗑️  Deleting old repositories..."

for service in "${SERVICES[@]}"; do
    OLD_REPO="storefront/$OLD_ENV/$service"
    
    echo "  🗑️  Deleting: $OLD_REPO"
    
    if aws ecr delete-repository \
        --repository-name "$OLD_REPO" \
        --region "$AWS_REGION" \
        --force 2>/dev/null; then
        echo "  ✅ Deleted: $OLD_REPO"
    else
        echo "  ⚠️  Could not delete $OLD_REPO (may not exist)"
    fi
done

echo ""
echo "✅ Cleanup complete!"
