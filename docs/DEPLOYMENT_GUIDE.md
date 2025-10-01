# Production Deployment Guide

## Overview

This guide outlines the complete process for promoting code changes from development to production using our multi-repository CI/CD pipeline with proper testing gates.

## Repository Architecture

```
storefront-cdk (Application Code)
     ↓
  Build & Push Images to ECR
     ↓
  Trigger → aws-fargate-cdk (Infrastructure)
     ↓
Development → Staging → Production
     ↓           ↓          ↓
   Feature    Integration  Manual
   Testing     Testing    Approval
```

### Repositories

- **storefront-cdk**: Application code (API, Web frontend)
  - Builds Docker images
  - Pushes to ECR
  - Triggers infrastructure deployments
  
- **aws-fargate-cdk**: Infrastructure as Code
  - Manages AWS resources (ECS, RDS, Route53, etc.)
  - Deploys application images to environments
  - Runs integration and performance tests

### Environment Configurations

| Environment | Database | ECS Tasks | Multi-AZ | Deletion Protection |
|-------------|----------|-----------|----------|-------------------|
| **dev**     | db.t3.micro | 1 | No | No |
| **staging** | db.t3.small | 2 | No | No |
| **prod**    | db.t3.medium | 3 | No | Yes |

## Deployment Process

### 1. Development Environment (Automatic)

**Repository:** `storefront-cdk` → `aws-fargate-cdk`

**Triggers:**
- Push to any branch (except `main`)
- Pull request creation

**Process:**

#### In storefront-cdk:
1. **Change Detection** - Identifies modified services (API/Web)
2. **Semantic Versioning** - Generates version tags
3. **Build Images** - Builds only changed services
4. **Push to ECR** - Uploads images with version tags
5. **Trigger Infrastructure** - Sends `deploy-infrastructure` event to aws-fargate-cdk

#### In aws-fargate-cdk:
6. **Receive Event** - Gets image tags from storefront-cdk
7. **Deploy to Dev** - Updates ECS services with new images
8. **Health Checks** - Verifies services are running

**Requirements:**
- No test requirements (fast feedback loop)
- No manual approval required
- Automatic rollback on health check failure

**Image Tags:** `api:dev-<sha>`, `web:dev-<sha>`

---

### 2. Staging Environment (Semi-Automatic)

**Repository:** `storefront-cdk` → `aws-fargate-cdk`

**Triggers:**
- Push to `main` branch in storefront-cdk (after PR merge)

**Process:**

#### In storefront-cdk:
1. **Change Detection** - Identifies modified services
2. **Semantic Release** - Generates semantic version (e.g., v1.2.3)
3. **Build Images** - Builds API and Web services
4. **Push to ECR** - Uploads images with semantic version tags
5. **Trigger Staging** - Sends `staging-deploy` event to aws-fargate-cdk

#### In aws-fargate-cdk:
6. **Test Gate** - Runs full test suite
   - Unit tests (80% coverage required)
   - Lint & security scans (Bandit, Safety)
   - Integration tests (ECS, RDS, SQS connectivity)
   - Performance tests (API load, Web concurrency)
7. **Deploy to Staging** - Updates infrastructure with new images
   - NetworkStack-staging
   - DatabaseStack-staging
   - APIServiceStack-staging (new image)
   - WebServiceStack-staging (new image)
   - All supporting stacks
8. **Post-deployment Verification** - Health checks and smoke tests
9. **Staging Summary** - Reports deployment status

**Requirements:**
- All pre-deployment tests must pass
- Integration tests must complete successfully
- Performance benchmarks must be met (95% success rate, <2s avg response)
- Post-deployment health checks must pass

**Image Tags:** `api:v1.2.3`, `web:v1.2.3`

**Deployment Time:** ~15-20 minutes (including tests)

---

### 3. Production Environment (Manual Approval)

**Repository:** `aws-fargate-cdk` only

**Triggers:**
- Manual workflow dispatch in GitHub Actions
- Requires staging to be healthy and validated

**Process:**

1. **Pre-deployment Validation** 
   - Verify staging deployment is successful
   - Confirm staging health checks passed
   - Review staging performance metrics

2. **Manual Workflow Trigger**
   - Go to [Production Deployment Workflow](https://github.com/AITeeToolkit/aws-fargate-cdk/actions/workflows/production-deployment.yml)
   - Click "Run workflow"
   - Confirm image tags from staging (e.g., `api:v1.2.3`, `web:v1.2.3`)

3. **Pre-deployment Tests**
   - Unit tests (80% coverage)
   - Security scans
   - Integration tests against production

4. **Manual Approval Gate**
   - 5-minute wait timer
   - Requires approval from authorized personnel
   - Safety checks validation

5. **Production Deployment**
   - Blue-green deployment strategy
   - Zero-downtime rolling updates
   - Gradual traffic shift

6. **Post-deployment Monitoring**
   - Enhanced monitoring for 24 hours
   - Automatic rollback triggers
   - Alert thresholds active

**Requirements:**
- Staging environment must be healthy and stable
- Manual approval from authorized personnel
- All safety checks must pass
- Rollback plan must be validated

**Image Tags:** Same as staging (e.g., `api:v1.2.3`, `web:v1.2.3`)

**Deployment Time:** ~25-30 minutes (including approval wait)

## Testing Strategy

### Unit Tests
- **Location:** `tests/unit/`
- **Coverage:** 80% minimum required
- **Scope:** Individual components and functions
- **Runtime:** < 5 minutes

### Integration Tests
- **Location:** `tests/integration/`
- **Scope:** Service interactions, database connectivity, AWS services
- **Environment:** Staging and production (requires deployed infrastructure)
- **Runtime:** < 15 minutes
- **Note:** Tests will skip gracefully if infrastructure is not deployed

### Performance Tests
- **Scope:** Load testing, response times, resource utilization
- **Environment:** Staging only
- **Tools:** Locust, custom performance scripts
- **Runtime:** < 30 minutes

### Security Tests
- **Tools:** Bandit (Python security), Safety (dependency scanning)
- **Scope:** Code vulnerabilities, dependency issues
- **Runtime:** < 5 minutes

## Workflow Commands

### Running Tests Locally

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run unit tests
pytest tests/unit/ -v --cov=stacks --cov=apps

# Run integration tests (requires AWS credentials and deployed infrastructure)
# Tests will skip gracefully if resources don't exist
pytest tests/integration/ -v -m "not slow"

# Run performance tests
export WEB_ENDPOINT="https://staging.cidertees.com"
export ENVIRONMENT=staging
pytest tests/integration/test_performance.py -v -m "performance"

# Run all tests with coverage
pytest tests/ -v --cov-report=html
```

### Deployment Workflows

#### Deploy to Development

**In storefront-cdk repository:**
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes to API or Web code
# Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/my-feature

# This automatically:
# 1. Builds changed images
# 2. Pushes to ECR with dev-<sha> tags
# 3. Triggers aws-fargate-cdk dev deployment
```

**Result:** Changes deployed to dev environment in ~5-10 minutes

---

#### Deploy to Staging

**In storefront-cdk repository:**
```bash
# Merge PR to main
# This automatically:
# 1. Runs semantic-release (generates v1.2.3)
# 2. Builds API and Web images
# 3. Pushes to ECR with v1.2.3 tags
# 4. Triggers aws-fargate-cdk staging deployment

git checkout main
git pull origin main
# Or merge PR via GitHub UI
```

**In aws-fargate-cdk repository:**
- Receives `staging-deploy` event
- Runs full test suite
- Deploys to staging if tests pass
- Runs post-deployment health checks

**Result:** Changes deployed to staging in ~15-20 minutes

---

#### Deploy to Production

**Prerequisites:**
1. Staging deployment must be successful
2. Staging health checks must pass
3. Manual testing in staging completed

**Steps:**
1. Go to [Production Deployment Workflow](https://github.com/AITeeToolkit/aws-fargate-cdk/actions/workflows/production-deployment.yml)
2. Click "Run workflow"
3. Enter parameters:
   - `api_tag`: Version from staging (e.g., `v1.2.3`)
   - `web_tag`: Version from staging (e.g., `v1.2.3`)
   - `listener_tag`: `latest` (or specific version)
   - `dns_worker_tag`: `latest` (or specific version)
4. Click "Run workflow"
5. Wait for pre-deployment tests
6. **Approve deployment** when prompted (5-minute timer)
7. Monitor deployment progress

**Result:** Changes deployed to production in ~25-30 minutes

---

#### Emergency Deployment (Hotfix)

**For critical production issues:**

1. Create hotfix branch from main
```bash
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix
```

2. Make minimal fix and commit
```bash
git add .
git commit -m "fix: critical security patch"
git push origin hotfix/critical-fix
```

3. Merge to main (fast-track PR approval)
4. Wait for staging deployment
5. Immediately trigger production deployment with `emergency_deploy: true`

**Note:** Emergency deploys skip some safety checks but still require approval

---

#### Rollback Production

**If issues detected after deployment:**

1. Go to [Production Deployment Workflow](https://github.com/AITeeToolkit/aws-fargate-cdk/actions/workflows/production-deployment.yml)
2. Click "Run workflow"
3. Enter previous working version:
   - `api_tag`: Previous version (e.g., `v1.2.2`)
   - `web_tag`: Previous version (e.g., `v1.2.2`)
4. Add note: "Rollback due to [issue]"
5. Approve rollback

**Alternative - ECS Console:**
```bash
# Quick rollback via AWS CLI
aws ecs update-service \
  --cluster storefront-cluster-prod \
  --service api-service-prod \
  --task-definition api-service-prod:previous-revision \
  --force-new-deployment
```

---

### Infrastructure-Only Deployments (aws-fargate-cdk)

When making changes to infrastructure code (CDK stacks, configurations) without application code changes:

#### Deploy Infrastructure to Development

**In aws-fargate-cdk repository:**
```bash
# Create feature branch
git checkout -b feature/add-new-stack

# Make infrastructure changes
# Edit stacks, add resources, etc.
git add .
git commit -m "feat: add new monitoring stack"
git push origin feature/add-new-stack

# This automatically:
# 1. Runs unit tests
# 2. Runs lint & security scans
# 3. Deploys changed stacks to dev
# 4. Uses latest images from ECR
```

**Result:** Infrastructure changes deployed to dev in ~10-15 minutes

---

#### Deploy Infrastructure to All Environments

**Use `[deploy-all]` commit message to deploy to dev, staging, AND prod:**

```bash
# Make infrastructure change
git add .
git commit -m "feat: update security group rules [deploy-all]"
git push origin main

# This automatically:
# 1. Runs full test suite
# 2. Deploys to dev environment
# 3. Deploys to staging environment
# 4. Deploys to prod environment (in sequence)
# 5. Uses latest images from ECR for each environment
```

**When to use `[deploy-all]`:**
- ✅ Security group updates
- ✅ IAM policy changes
- ✅ Database configuration updates
- ✅ Infrastructure-wide changes
- ❌ Application code changes (use storefront-cdk instead)

**Result:** Infrastructure changes deployed to all environments in ~30-40 minutes

---

#### Deploy Infrastructure to Staging Only

**Push to main without `[deploy-all]`:**

```bash
# Make infrastructure change
git add .
git commit -m "feat: add new SQS queue"
git push origin main

# This automatically:
# 1. Runs full test suite
# 2. Detects infrastructure changes
# 3. Deploys to staging only (main branch default)
# 4. Uses latest images from ECR
```

**Result:** Infrastructure changes deployed to staging in ~15-20 minutes

---

#### Manual Infrastructure Deployment

**For specific environment or stack:**

1. Go to [CI/CD Pipeline Workflow](https://github.com/AITeeToolkit/aws-fargate-cdk/actions/workflows/semantic-release.yml)
2. Click "Run workflow"
3. Select parameters:
   - `environment`: dev, staging, or prod
   - `force_infra`: true (force deployment even if no changes)
   - `deploy_all_environments`: true (deploy to all environments)
4. Click "Run workflow"

**Use cases:**
- Deploy specific stack to specific environment
- Force re-deployment without code changes
- Deploy infrastructure after manual ECR image push

---

### Skip CI/CD Workflows

**To push code without triggering any workflows, use `[skip ci]` in commit message:**

```bash
# In either repository (storefront-cdk or aws-fargate-cdk)
git add .
git commit -m "docs: update documentation [skip ci]"
git push origin main

# Alternative syntax (also works)
git commit -m "chore: update config [ci skip]"
```

**When to use `[skip ci]`:**
- ✅ Documentation updates (README, guides, comments)
- ✅ Configuration file changes that don't affect deployment
- ✅ Workflow file fixes (to avoid recursive triggers)
- ✅ Minor formatting or typo fixes
- ❌ Code changes (always test and deploy)
- ❌ Infrastructure changes (always validate)

**Effect:**
- **storefront-cdk**: Skips image builds, ECR pushes, deployment triggers
- **aws-fargate-cdk**: Skips tests, infrastructure deployments

**Example use cases:**
```bash
# Update README
git commit -m "docs: add deployment examples [skip ci]"

# Fix typo in comments
git commit -m "chore: fix typo in comments [skip ci]"

# Update GitHub workflow (avoid triggering itself)
git commit -m "ci: fix workflow syntax [skip ci]"
```

---

## Monitoring and Alerts

### Key Metrics
- **ECS Service Health** - Task counts, CPU/memory utilization
- **Database Performance** - Connection counts, query performance
- **Route53 Operations** - Hosted zone creation/deletion success rates
- **SQS Queue Health** - Message processing rates, dead letter queues

### Alert Thresholds
- **High Error Rate** - >5% error rate for 5 minutes
- **High Response Time** - >2s average response time for 10 minutes
- **Resource Utilization** - >80% CPU/memory for 15 minutes
- **Failed Deployments** - Any deployment failure

### Dashboards
- [ECS Clusters](https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters)
- [CloudWatch Metrics](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1)
- [Application Logs](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)

## Troubleshooting

### Common Issues

#### Deployment Failures
1. **Check CloudFormation Events** - Look for stack update failures
2. **Verify IAM Permissions** - Ensure service roles have required permissions
3. **Check Resource Limits** - Verify AWS service quotas
4. **Review Application Logs** - Check ECS task logs for errors

#### Test Failures
1. **Unit Test Failures** - Fix code issues and re-run tests
2. **Integration Test Failures** - Check AWS service connectivity and ensure infrastructure is deployed
3. **Performance Test Failures** - Investigate resource constraints
4. **Security Test Failures** - Update dependencies or fix vulnerabilities
5. **Integration Tests Skipping** - Normal behavior when infrastructure isn't deployed yet

#### Rollback Scenarios
1. **Application Errors** - Use rollback workflow with previous version
2. **Database Issues** - Restore from automated backup
3. **Infrastructure Problems** - Revert CloudFormation stack changes
### Emergency Contacts
- **DevOps Team** - For infrastructure issues
- **Development Team** - For application issues
- **Security Team** - For security incidents

## Best Practices

### Code Changes
1. **Small, Incremental Changes** - Easier to test and rollback
2. **Conventional Commits** - Enables automatic versioning
3. **Comprehensive Tests** - Unit, integration, and performance tests
4. **Security Scanning** - Regular dependency updates

### Deployment Strategy
1. **Test in Staging First** - Never skip staging validation
2. **Deploy During Low Traffic** - Minimize user impact
3. **Monitor Post-Deployment** - Watch metrics for 24 hours
4. **Have Rollback Plan** - Always be prepared to rollback

### Environment Management
1. **Environment Parity** - Keep environments as similar as possible
2. **Configuration Management** - Use environment-specific configs
3. **Secret Management** - Use AWS Secrets Manager for sensitive data
4. **Resource Tagging** - Proper tagging for cost allocation

## Compliance and Auditing

### Change Management
- All production changes require approval
- Deployment history tracked in GitHub Actions
- Change logs maintained in CHANGELOG.md

### Security
- All deployments use IAM roles with least privilege
- Secrets stored in AWS Secrets Manager
- Regular security scanning and updates

### Backup and Recovery
- Automated database backups (7 days dev/staging, 30 days production)
- Infrastructure as Code for rapid recovery
- Tested rollback procedures

---

For questions or issues with this deployment process, please contact the DevOps team or create an issue in this repository.
