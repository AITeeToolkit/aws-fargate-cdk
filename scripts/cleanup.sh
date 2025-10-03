#!/bin/bash

# Cleanup CloudFormation stacks in reverse order
# Usage: ./cleanup.sh [environment] [region]

set -e

ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
PROJECT_NAME="storefront"

echo "Deleting CloudFormation stacks for environment: $ENVIRONMENT in region: $REGION"

# Function to delete a stack
delete_stack() {
    local stack_name=$1
    
    echo "Deleting stack: $stack_name"
    
    aws cloudformation delete-stack \
        --stack-name "$stack_name" \
        --region "$REGION"
    
    echo "Waiting for stack deletion: $stack_name"
    aws cloudformation wait stack-delete-complete \
        --stack-name "$stack_name" \
        --region "$REGION"
    
    if [ $? -eq 0 ]; then
        echo " Successfully deleted $stack_name"
    else
        echo " Failed to delete $stack_name"
        exit 1
    fi
}

# Delete stacks in reverse order
echo "\n Starting cleanup..."

# 6. Web Service Stack
delete_stack "${PROJECT_NAME}-${ENVIRONMENT}-web"

# 5. API Service Stack
delete_stack "${PROJECT_NAME}-${ENVIRONMENT}-api"

# 4. ECR Repositories
delete_stack "${PROJECT_NAME}-${ENVIRONMENT}-ecr"

# 3. Database Stack
delete_stack "${PROJECT_NAME}-${ENVIRONMENT}-database"

# 2. Shared Stack
delete_stack "${PROJECT_NAME}-${ENVIRONMENT}-shared"

# 1. Network Stack (only if no other environments are using it)
read -p "Delete network stack ${PROJECT_NAME}-network? This affects ALL environments (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    delete_stack "${PROJECT_NAME}-network"
else
    echo "Skipping network stack deletion"
fi

echo "\n🎉 Cleanup completed for environment: $ENVIRONMENT"
