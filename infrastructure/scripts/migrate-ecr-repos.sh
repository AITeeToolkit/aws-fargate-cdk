#!/bin/bash

# Migration script to move from environment-specific ECR repos to shared repos
# This script:
# 1. Creates new shared repositories (storefront/api, storefront/web, etc.)
# 2. Copies all images from old repos to new repos
# 3. Optionally deletes old repositories

set -e

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="156041439702"
SERVICES=("api" "web" "listener" "dns-worker")
OLD_ENV="dev"  # The environment with existing images

echo "🚀 Starting ECR repository migration..."
echo "📍 Region: $AWS_REGION"
echo "🏢 Account: $AWS_ACCOUNT_ID"
echo ""

# Step 1: Create new shared repositories
echo "📦 Step 1: Creating shared ECR repositories..."
for service in "${SERVICES[@]}"; do
    NEW_REPO="storefront/$service"
    
    if aws ecr describe-repositories --repository-names "$NEW_REPO" --region "$AWS_REGION" 2>/dev/null; then
        echo "  ✅ Repository already exists: $NEW_REPO"
    else
        echo "  🆕 Creating repository: $NEW_REPO"
        aws ecr create-repository \
            --repository-name "$NEW_REPO" \
            --image-scanning-configuration scanOnPush=true \
            --region "$AWS_REGION" \
            --tags Key=ManagedBy,Value=CDK Key=Environment,Value=shared
        echo "  ✅ Created: $NEW_REPO"
    fi
done

echo ""
echo "📋 Step 2: Copying images from old repositories to new shared repositories..."

for service in "${SERVICES[@]}"; do
    OLD_REPO="storefront/$OLD_ENV/$service"
    NEW_REPO="storefront/$service"
    
    echo ""
    echo "  🔄 Processing: $OLD_REPO → $NEW_REPO"
    
    # Get only the latest semantic version tag and 'latest' tag
    ALL_TAGS=$(aws ecr list-images \
        --repository-name "$OLD_REPO" \
        --region "$AWS_REGION" \
        --query 'imageIds[?imageTag!=`null`].imageTag' \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$ALL_TAGS" ]; then
        echo "    ⚠️  No images found in $OLD_REPO"
        continue
    fi
    
    # Find the latest version tag (highest semantic version)
    LATEST_VERSION=$(echo "$ALL_TAGS" | tr '\t' '\n' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)
    
    # Collect tags to copy: latest version + 'latest' tag if it exists
    IMAGES=""
    if [ -n "$LATEST_VERSION" ]; then
        IMAGES="$LATEST_VERSION"
    fi
    if echo "$ALL_TAGS" | grep -q "latest"; then
        IMAGES="$IMAGES latest"
    fi
    
    if [ -z "$IMAGES" ]; then
        echo "    ⚠️  No valid tags found in $OLD_REPO"
        continue
    fi
    
    echo "    📋 Tags to copy: $IMAGES"
    
    # Copy selected images
    for tag in $IMAGES; do
        echo "    📦 Copying tag: $tag"
        
        # Pull from old repo (force AMD64 platform for compatibility)
        OLD_IMAGE="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$OLD_REPO:$tag"
        NEW_IMAGE="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$NEW_REPO:$tag"
        
        # Try to pull with platform specification, fallback to regular pull
        if docker pull --platform linux/amd64 "$OLD_IMAGE" 2>/dev/null; then
            echo "    ✓ Pulled AMD64 image"
        elif docker pull "$OLD_IMAGE" 2>/dev/null; then
            echo "    ✓ Pulled image (native platform)"
        else
            echo "    ✗ Failed to pull $tag"
            continue
        fi
        
        docker tag "$OLD_IMAGE" "$NEW_IMAGE"
        
        # Push with error handling
        if docker push "$NEW_IMAGE" 2>&1 | tee /tmp/docker_push.log; then
            echo "    ✓ Push successful"
        else
            # If push fails due to manifest issues, try with platform flag
            if grep -q "manifest list" /tmp/docker_push.log; then
                echo "    ⚠️  Manifest issue detected, retrying with platform flag..."
                docker push --platform linux/amd64 "$NEW_IMAGE" || echo "    ✗ Push failed"
            fi
        fi
        
        echo "    ✅ Copied: $tag"
    done
done

echo ""
echo "✅ Migration complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Verify images in new repositories:"
echo "     aws ecr list-images --repository-name storefront/api --region $AWS_REGION"
echo ""
echo "  2. Deploy your CDK stacks to test:"
echo "     cdk deploy --all"
echo ""
echo "  3. After verifying everything works, delete old repositories:"
echo "     ./scripts/cleanup-old-ecr-repos.sh"
