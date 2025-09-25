#!/bin/bash
# AWS SSO Login and Profile Export Script

# Default profile name
PROFILE_NAME=${1:-"default"}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting AWS SSO login process for profile: ${PROFILE_NAME}${NC}"

# Attempt SSO login
aws sso login --profile ${PROFILE_NAME}
LOGIN_STATUS=$?

if [ $LOGIN_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ SSO login successful!${NC}"
    
    # Export AWS profile for current shell
    echo -e "${YELLOW}Exporting AWS_PROFILE=${PROFILE_NAME} to current shell${NC}"
    export AWS_PROFILE=${PROFILE_NAME}
    
    # Verify credentials
    echo -e "${YELLOW}Verifying AWS credentials...${NC}"
    aws sts get-caller-identity
    
    echo -e "${GREEN}✅ AWS profile ${PROFILE_NAME} is now active${NC}"
    echo -e "${YELLOW}Run the following command in your shell to use this profile:${NC}"
    echo -e "${GREEN}export AWS_PROFILE=${PROFILE_NAME}${NC}"
else
    echo -e "\033[0;31m❌ SSO login failed. Please check your AWS configuration and try again.${NC}"
    exit 1
fi
