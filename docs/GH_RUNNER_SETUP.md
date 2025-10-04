# GitHub Self-Hosted Runner Setup

## Overview

A self-hosted GitHub Actions runner is deployed in the VPC to enable database connectivity during CDK synthesis. This runner has direct access to RDS databases across all environments (dev, staging, prod).

## Architecture

- **Location**: Private isolated subnet in VPC
- **Instance Type**: t3.small
- **OS**: Amazon Linux 2
- **Access**: SSM Session Manager (no SSH required)
- **Environments**: Shared across dev, staging, and prod

## Initial Configuration

### 1. Get GitHub Runner Token

1. Go to: https://github.com/AITeeToolkit/aws-fargate-cdk/settings/actions/runners/new
2. Copy the registration token (valid for 1 hour)

### 2. Connect to Runner Instance

```bash
# Get instance ID
aws cloudformation describe-stacks \
  --stack-name GitHubRunnerStack \
  --query 'Stacks[0].Outputs[?OutputKey==`RunnerInstanceId`].OutputValue' \
  --output text

# Connect via SSM
aws ssm start-session --target i-0a62a9fa756025ef6
```

# Create a folder
sudo mkdir actions-runner && cd actions-runner

# Download the latest runner package
sudo curl -o actions-runner-linux-x64-2.328.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.328.0/actions-runner-linux-x64-2.328.0.tar.gz

# Optional: Validate the hash
sudo echo "01066fad3a2893e63e6ca880ae3a1fad5bf9329d60e77ee15f2b97c148c3cd4e  actions-runner-linux-x64-2.328.0.tar.gz" | shasum -a 256 -c

# Extract the installer
sudo tar xzf ./actions-runner-linux-x64-2.328.0.tar.gz

# Create the runner and start the configuration experience
sudo dnf install dotnet-sdk-9.0
./config.sh --url https://github.com/AITeeToolkit/aws-fargate-cdk --token BNL5V4R6KFLYIBY3THVMLTTI4CYUU

./run.sh

# Use this YAML in your workflow file for each job
runs-on: self-hosted
