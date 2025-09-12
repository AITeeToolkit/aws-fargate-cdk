#!/bin/bash

# Deploy CloudFormation stacks in order
# Usage: ./deploy.sh [environment] [region]

set -e

ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
PROJECT_NAME="storefront"

echo "Deploying CloudFormation stacks for environment: $ENVIRONMENT in region: $REGION"

# Function to deploy a stack
deploy_stack() {
    local stack_name=$1
    local template_file=$2
    local parameters=$3
    
    echo "Deploying stack: $stack_name"
    
    aws cloudformation deploy \
        --template-file "$template_file" \
        --stack-name "$stack_name" \
        --parameter-overrides $parameters \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --no-fail-on-empty-changeset
    
    if [ $? -eq 0 ]; then
        echo " Successfully deployed $stack_name"
    else
        echo " Failed to deploy $stack_name"
        exit 1
    fi
}

# Deploy stacks in order
echo "\n Starting deployment..."

# 1. Network Stack
deploy_stack \
    "${PROJECT_NAME}-network" \
    "templates/01-network.yaml" \
    "ProjectName=${PROJECT_NAME}"

# 2. Shared Stack (environment-level resources)
deploy_stack \
    "${PROJECT_NAME}-${ENVIRONMENT}-shared" \
    "templates/02-shared.yaml" \
    "ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT}"

# 3. Database Stack
deploy_stack \
    "${PROJECT_NAME}-${ENVIRONMENT}-database" \
    "templates/03-database.yaml" \
    "ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT}"

# 4. ECR Repositories
deploy_stack \
    "${PROJECT_NAME}-${ENVIRONMENT}-ecr" \
    "templates/06-ecr.yaml" \
    "ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT}"

# 5. API Service Stack
deploy_stack \
    "${PROJECT_NAME}-${ENVIRONMENT}-api" \
    "templates/04-api-service.yaml" \
    "ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT}"

# 6. Web Service Stack
deploy_stack \
    "${PROJECT_NAME}-${ENVIRONMENT}-web" \
    "templates/05-web-service.yaml" \
    "ProjectName=${PROJECT_NAME} Environment=${ENVIRONMENT}"

echo "\n🎉 All stacks deployed successfully!"

# Display outputs
echo "\n📋 Stack Outputs:"
aws cloudformation describe-stacks \
    --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-shared" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ALBDNSName`].OutputValue' \
    --output text 2>/dev/null && echo "ALB DNS Name: $(aws cloudformation describe-stacks --stack-name "${PROJECT_NAME}-${ENVIRONMENT}-shared" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`ALBDNSName`].OutputValue' --output text 2>/dev/null)"

echo "\nDeployment completed for environment: $ENVIRONMENT"
