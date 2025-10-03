#!/bin/bash

# Resilient CloudFormation deployment script
# Usage: ./deploy-resilient.sh <stack-name> <template-file> [parameters...]

set -e

STACK_NAME=$1
TEMPLATE_FILE=$2
shift 2
PARAMETERS="$@"

MAX_RETRIES=3
RETRY_COUNT=0

deploy_stack() {
    echo "🚀 Deploying stack: $STACK_NAME"
    
    # Check if stack exists and its status
    STACK_STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "DOES_NOT_EXIST")
    
    case $STACK_STATUS in
        "ROLLBACK_COMPLETE"|"CREATE_FAILED"|"DELETE_FAILED")
            echo "⚠️  Stack in failed state: $STACK_STATUS"
            echo "🔄 Attempting to continue rollback..."
            
            # Try to continue rollback first
            aws cloudformation continue-update-rollback --stack-name "$STACK_NAME" 2>/dev/null || true
            aws cloudformation wait stack-rollback-complete --stack-name "$STACK_NAME" 2>/dev/null || true
            
            # If still in failed state, delete and recreate
            CURRENT_STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "DOES_NOT_EXIST")
            if [[ "$CURRENT_STATUS" == *"FAILED"* ]] || [[ "$CURRENT_STATUS" == "ROLLBACK_COMPLETE" ]]; then
                echo "🗑️  Deleting failed stack..."
                aws cloudformation delete-stack --stack-name "$STACK_NAME"
                aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME"
            fi
            ;;
        "DELETE_IN_PROGRESS"|"CREATE_IN_PROGRESS"|"UPDATE_IN_PROGRESS")
            echo "⏳ Stack operation in progress: $STACK_STATUS"
            echo "⏳ Waiting for operation to complete..."
            
            # Wait for current operation to complete
            case $STACK_STATUS in
                "DELETE_IN_PROGRESS")
                    aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" || true
                    ;;
                "CREATE_IN_PROGRESS")
                    aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" || true
                    ;;
                "UPDATE_IN_PROGRESS")
                    aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME" || true
                    ;;
            esac
            ;;
    esac
    
    # Deploy the stack
    echo "📦 Deploying CloudFormation template..."
    aws cloudformation deploy \
        --template-file "$TEMPLATE_FILE" \
        --stack-name "$STACK_NAME" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --no-fail-on-empty-changeset \
        $PARAMETERS
}

# Retry logic
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if deploy_stack; then
        echo "✅ Stack deployment successful!"
        exit 0
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "❌ Deployment failed. Retrying in 30 seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)"
            sleep 30
        else
            echo "❌ Deployment failed after $MAX_RETRIES attempts"
            exit 1
        fi
    fi
done
