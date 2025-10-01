# Multi-Environment Deployment Guide

This guide explains how to deploy the AWS Fargate infrastructure across multiple environments (dev, staging, prod).

## Architecture Overview

### Shared Resources (Single Instance)
- **NetworkStack**: VPC, subnets, NAT gateways
- **SharedStack**: ECS cluster, security groups
- **StorefrontECRStack**: ECR repositories (shared across all environments)

### Environment-Specific Resources
- **DatabaseStack-{env}**: RDS PostgreSQL instance per environment
- **MultiAlbStack-{env}**: Application Load Balancers per environment
- **OpenSearchStack-{env}**: OpenSearch domain per environment
- **SQSStack-{env}**: SQS queues per environment
- **APIServiceStack-{env}**: API ECS service per environment
- **WebServiceStack-{env}**: Web ECS service per environment
- **ListenerServiceStack-{env}**: Listener ECS service per environment
- **DNSWorkerServiceStack-{env}**: DNS Worker ECS service per environment

## Environment Configuration

Environment-specific settings are defined in `app.py`:

```python
env_config = {
    "dev": {
        "db_multi_az": False,
        "db_instance_class": "db.t3.micro",
        "ecs_desired_count": 1,
        "enable_deletion_protection": False,
    },
    "staging": {
        "db_multi_az": False,
        "db_instance_class": "db.t3.micro",
        "ecs_desired_count": 1,
        "enable_deletion_protection": False,
    },
    "prod": {
        "db_multi_az": False,
        "db_instance_class": "db.t3.micro",
        "ecs_desired_count": 1,
        "enable_deletion_protection": True,
    },
}
```

## Deployment Methods

### Method 1: Deploy Single Environment

```bash
# Deploy to dev (default)
cdk deploy --all

# Deploy to specific environment
cdk deploy --all --context env=staging
cdk deploy --all --context env=prod
```

### Method 2: Deploy All Environments at Once

```bash
# Deploy dev, staging, AND prod simultaneously
cdk deploy --all --context deploy-all=true
```

### Method 3: Deploy Specific Stack to Multiple Environments

```bash
# Deploy database stack to staging
cdk deploy --all --context env=staging

# Deploy database stack to prod
cdk deploy --all --context env=prod

# Or deploy specific stack with loop
for env in dev staging prod; do
  cdk deploy DatabaseStack-$env --context env=$env
done

# Note: You cannot deploy multiple environment stacks in one command like:
# cdk deploy DatabaseStack-dev DatabaseStack-staging  # ❌ This won't work
# You must use --context env=<environment> to create the stacks first
```

### Method 4: Via GitHub Actions (Automated)

#### Push with Commit Message
```bash
# Single environment (dev only)
git commit -m "fix: update API service"
git push origin main

# ALL environments (dev, staging, prod)
git commit -m "feat: major release [deploy-all]"
git push origin main
```

#### Manual Workflow Dispatch
```bash
# Single environment
gh workflow run semantic-release.yml -f environment=dev

# ALL environments - Use commit message approach (recommended)
# This triggers ONE workflow that deploys all environments in parallel
git commit --allow-empty -m "chore: deploy all environments [deploy-all]"
git push origin main

# Alternative: Trigger each environment separately (NOT recommended - causes collisions)
# gh workflow run semantic-release.yml -f environment=dev
# gh workflow run semantic-release.yml -f environment=staging
# gh workflow run semantic-release.yml -f environment=prod
```

## Container Image Strategy

### Shared ECR Repositories
All environments use the **same ECR repositories**:
- `storefront/api`
- `storefront/web`
- `storefront/listener`
- `storefront/dns-worker`

### Image Tagging
Images are tagged with **semantic versions** (no environment suffix):
- `storefront/api:v1.6.7`
- `storefront/web:v1.4.4`
- `storefront/listener:v1.52.8`
- `storefront/dns-worker:v1.0.13`

### How Environments Differ
The **same image** runs in all environments, but with different:
- Environment variables (injected by ECS)
- Infrastructure resources (database, ALB, etc.)
- Scaling configuration (task count)

This ensures **immutable artifacts** - what you test in staging is exactly what runs in prod.

## Stack Dependencies

### Deployment Order
1. **Shared Resources** (deployed once):
   - NetworkStack
   - SharedStack
   - StorefrontECRStack

2. **Per-Environment Resources** (deployed per environment):
   - DatabaseStack-{env}
   - OpenSearchStack-{env}
   - SQSStack-{env}
   - MultiAlbStack-{env}
   - DomainDnsStack-{env}-{domain}
   - ListenerServiceStack-{env}
   - DNSWorkerServiceStack-{env}
   - APIServiceStack-{env}
   - WebServiceStack-{env}

### Stack Dependencies
```
NetworkStack
    ↓
SharedStack
    ↓
DatabaseStack-{env} ← OpenSearchStack-{env} ← SQSStack-{env}
    ↓                          ↓                    ↓
MultiAlbStack-{env}           ↓                    ↓
    ↓                          ↓                    ↓
WebServiceStack-{env} ← APIServiceStack-{env} ← ListenerServiceStack-{env}
                                                     ↓
                                            DNSWorkerServiceStack-{env}
```

## Common Operations

### View All Stacks
```bash
cdk list
```

### Synthesize CloudFormation Templates
```bash
# Single environment
cdk synth --context env=staging

# All environments
cdk synth --context deploy-all=true
```

### Diff Changes Before Deployment
```bash
# Single environment
cdk diff --all --context env=prod

# All environments
cdk diff --all --context deploy-all=true
```

### Destroy Environment
```bash
# Destroy single environment
cdk destroy --all --context env=dev

# Destroy all environments (dangerous!)
cdk destroy --all --context deploy-all=true
```

### Deploy Specific Stack
```bash
# Deploy only database for staging
cdk deploy DatabaseStack-staging --context env=staging

# Deploy only API service for prod
cdk deploy APIServiceStack-prod --context env=prod
```

## Troubleshooting

### Issue: Stack Already Exists
If you see "Stack already exists" errors:
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name DatabaseStack-dev --region us-east-1

# If in failed state, delete and redeploy
aws cloudformation delete-stack --stack-name DatabaseStack-dev --region us-east-1
cdk deploy DatabaseStack-dev --context env=dev
```

### Issue: ECR Repository Conflicts
If ECR repositories already exist:
```bash
# The ECR stack will automatically import existing repositories
# No action needed - just deploy
cdk deploy StorefrontECRStack
```

### Issue: RDS Custom Name Conflicts
If you see "cannot update a stack when a custom-named resource requires replacing":
- Remove `instance_identifier` from DatabaseStack
- Let CDK auto-generate names
- Redeploy the stack

### Issue: Export Conflicts
If you see "export is in use by another stack":
- Delete dependent stacks first
- Then delete the stack with exports
- Redeploy in correct order

## Best Practices

### 1. Test in Lower Environments First
```bash
# Deploy to dev first
cdk deploy --all --context env=dev

# Test thoroughly, then deploy to staging
cdk deploy --all --context env=staging

# Finally deploy to prod
cdk deploy --all --context env=prod
```

### 2. Use Commit Messages for Multi-Environment Deployments
```bash
# Regular changes: deploy to dev only
git commit -m "fix: update API endpoint"

# Major releases: deploy to all environments
git commit -m "feat: new feature [deploy-all]"
```

### 3. Monitor Deployments
```bash
# Watch CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name APIServiceStack-prod \
  --region us-east-1 \
  --max-items 20
```

### 4. Use Separate AWS Accounts (Recommended)
For production workloads, consider:
- Dev account: 111111111111
- Staging account: 222222222222
- Prod account: 333333333333

Update `app.py` to use different accounts per environment.

## CI/CD Integration

### Automatic Deployments
- **Push to main**: Deploys to dev automatically
- **Commit with `[deploy-all]`**: Deploys to all environments
- **Manual trigger**: Deploy to any environment via GitHub Actions

### Workflow Files
- `.github/workflows/semantic-release.yml`: Main deployment workflow
- `.github/workflows/infra-build.yml`: Infrastructure deployment
- `.github/workflows/test-suite.yml`: Testing and validation

## Environment Variables

Each environment gets its own set of environment variables via SSM Parameter Store:
- `/storefront-{env}/database/url`
- `/storefront-{env}/opensearch/endpoint`
- `/storefront-{env}/sqs/dns-operations-queue-url`

These are automatically created by CDK and injected into ECS tasks.

## Scaling Configuration

Adjust `env_config` in `app.py` to change scaling per environment:

```python
"prod": {
    "db_multi_az": True,           # Enable Multi-AZ for HA
    "db_instance_class": "db.t3.medium",  # Larger instance
    "ecs_desired_count": 3,        # More ECS tasks
    "enable_deletion_protection": True,   # Prevent accidental deletion
}
```

## Support

For issues or questions:
1. Check CloudFormation events in AWS Console
2. Review CDK synthesis output: `cdk synth`
3. Check GitHub Actions logs for CI/CD issues
