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
aws ssm start-session --target <INSTANCE_ID>
```

### 3. Configure Runner

```bash
# Switch to runner user
sudo su - runner

# Navigate to runner directory
cd actions-runner

# Configure runner (replace YOUR_TOKEN with actual token)
./config.sh \
  --url https://github.com/AITeeToolkit/aws-fargate-cdk \
  --token YOUR_TOKEN \
  --labels dev,staging,prod,self-hosted,linux,x64 \
  --name aws-vpc-runner

# Exit back to ec2-user
exit
```

### 4. Install and Start Service

```bash
# Install as systemd service
cd /home/runner/actions-runner
sudo ./svc.sh install runner

# Start the service
sudo ./svc.sh start

# Verify it's running
sudo ./svc.sh status
```

## Verification

### Check Runner Status

```bash
# On the instance
sudo ./svc.sh status

# Check logs
sudo journalctl -u actions.runner.AITeeToolkit-aws-fargate-cdk.aws-vpc-runner.service -f
```

### Verify in GitHub

1. Go to: https://github.com/AITeeToolkit/aws-fargate-cdk/settings/actions/runners
2. You should see the runner listed as "Idle" with labels: `dev`, `staging`, `prod`, `self-hosted`, `linux`, `x64`

## Workflow Usage

The runner is automatically used by workflows that specify:

```yaml
runs-on: [self-hosted, linux, x64]
```

### Current Workflows Using Runner

- **infra-build.yml**: Infrastructure deployment (needs database access for CDK synth)

## Database Access

The runner can access all RDS databases:

- **Dev**: `rds-dev.cyxas2yo0gpr.us-east-1.rds.amazonaws.com`
- **Staging**: Via VPC (same security group as ECS tasks)
- **Prod**: Via VPC (same security group as ECS tasks)

Security groups allow:
- VPC internal traffic (10.0.0.0/16)
- Allowed IPs from context (for specific users)

## Maintenance

### Restart Service

```bash
aws ssm start-session --target <INSTANCE_ID>
sudo systemctl restart actions.runner.AITeeToolkit-aws-fargate-cdk.aws-vpc-runner.service
```

### Update Runner

```bash
aws ssm start-session --target <INSTANCE_ID>
sudo su - runner
cd actions-runner
./svc.sh stop
./config.sh remove --token YOUR_REMOVAL_TOKEN
# Download latest version
curl -o actions-runner-linux-x64-VERSION.tar.gz -L https://github.com/actions/runner/releases/download/vVERSION/actions-runner-linux-x64-VERSION.tar.gz
tar xzf ./actions-runner-linux-x64-VERSION.tar.gz
./config.sh --url https://github.com/AITeeToolkit/aws-fargate-cdk --token YOUR_TOKEN --labels dev,staging,prod,self-hosted,linux,x64
exit
sudo ./svc.sh install runner
sudo ./svc.sh start
```

### View Logs

```bash
# Real-time logs
aws ssm start-session --target <INSTANCE_ID>
sudo journalctl -u actions.runner.AITeeToolkit-aws-fargate-cdk.aws-vpc-runner.service -f

# Last 100 lines
sudo journalctl -u actions.runner.AITeeToolkit-aws-fargate-cdk.aws-vpc-runner.service -n 100
```

## Troubleshooting

### Runner Not Appearing in GitHub

1. Check service status: `sudo ./svc.sh status`
2. Check logs: `sudo journalctl -u actions.runner.* -f`
3. Verify token hasn't expired (tokens expire after 1 hour)
4. Reconfigure with new token

### Database Connection Issues

1. Verify security group allows VPC traffic
2. Test database connection:
   ```bash
   aws ssm start-session --target <INSTANCE_ID>
   psql -h rds-dev.cyxas2yo0gpr.us-east-1.rds.amazonaws.com -U postgres -d storefront_dev
   ```

### Workflow Not Using Runner

1. Verify runner is online in GitHub settings
2. Check workflow `runs-on` labels match runner labels
3. Ensure runner has required labels: `self-hosted`, `linux`, `x64`

## IAM Permissions

The runner has the following permissions:
- **CloudFormation**: Full access for CDK deployments
- **ECR**: Full access for Docker images
- **ECS**: Full access for service deployments
- **Route53**: Full access for DNS management
- **RDS**: Read access for database queries
- **SSM**: Full access for parameter store
- **Secrets Manager**: Full access for secrets

## Security Notes

- Runner is in **private isolated subnet** (no internet access)
- Uses **VPC endpoints** for AWS service access
- **SSM Session Manager** for secure access (no SSH keys)
- **IAM role** for AWS permissions (no access keys)
- **Security group** restricts database access to VPC only

## Cost

- **EC2 Instance**: ~$15/month (t3.small, 24/7)
- **Data Transfer**: Minimal (within VPC)
- **Total**: ~$15-20/month

## Decommissioning

To remove the runner:

```bash
# Remove from GitHub
aws ssm start-session --target <INSTANCE_ID>
sudo su - runner
cd actions-runner
./config.sh remove --token YOUR_REMOVAL_TOKEN

# Delete CloudFormation stack
cdk destroy GitHubRunnerStack
```
