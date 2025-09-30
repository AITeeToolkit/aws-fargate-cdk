# Production Deployment Guide

## Overview

This guide outlines the complete process for promoting code changes from development to production using our multi-environment CI/CD pipeline with proper testing gates.

## Environment Architecture

```
Development → Staging → Production
     ↓           ↓          ↓
   Feature    Integration  Manual
   Testing     Testing    Approval
```

### Environment Configurations

| Environment | Database | ECS Tasks | Multi-AZ | Deletion Protection |
|-------------|----------|-----------|----------|-------------------|
| **dev**     | db.t3.micro | 1 | No | No |
| **staging** | db.t3.small | 2 | No | No |
| **prod**    | db.t3.medium | 3 | No | Yes |

## Deployment Process

### 1. Development Environment (Automatic)

**Triggers:**
- Push to any branch
- Pull request creation

**Process:**
1. **Change Detection** - Identifies modified services
2. **Unit Tests** - Runs comprehensive test suite
3. **Lint & Security** - Code quality and security scanning
4. **Build Images** - Builds only changed services
5. **Deploy to Dev** - Automatic deployment to development environment

**Requirements:**
- All unit tests must pass (80% coverage minimum)
- Code must pass linting and security scans
- No manual approval required

### 2. Staging Environment (Semi-Automatic)

**Triggers:**
- Push to `main` branch (after PR merge)

**Process:**
1. **Pre-deployment Tests** - Full test suite execution
2. **Integration Tests** - Tests against staging environment
3. **Performance Tests** - Load and performance validation
4. **Deploy to Staging** - Automatic deployment if tests pass
5. **Post-deployment Verification** - Health checks and smoke tests

**Requirements:**
- All pre-deployment tests must pass
- Integration tests must complete successfully
- Performance benchmarks must be met
- Post-deployment health checks must pass

### 3. Production Environment (Manual Approval)

**Triggers:**
- Manual workflow dispatch (after staging validation)

**Process:**
1. **Pre-deployment Validation** - Verify staging deployment status
2. **Manual Approval** - Required approval with 5-minute wait timer
3. **Pre-deployment Backup** - Database and configuration backup
4. **Blue-Green Deployment** - Zero-downtime production deployment
5. **Post-deployment Monitoring** - 24-hour enhanced monitoring
6. **Rollback Plan** - Automatic rollback triggers if issues detected

**Requirements:**
- Staging environment must be healthy and stable
- Manual approval from authorized personnel
- All safety checks must pass
- Rollback plan must be validated

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

# Run all tests with coverage
pytest tests/ -v --cov-report=html
```

### Manual Deployments

#### Deploy to Development
```bash
# Automatic on push to any branch
git push origin feature-branch
```

#### Deploy to Staging
```bash
# Automatic on push to main
git push origin main
```

#### Deploy to Production
1. Go to [GitHub Actions](https://github.com/AITeeToolkit/aws-fargate-cdk/actions)
2. Select "Production Deployment" workflow
3. Click "Run workflow"
4. Confirm deployment parameters
5. Approve when prompted

#### Emergency Deployment
```bash
# For critical hotfixes (skips some safety checks)
# Use GitHub Actions UI with emergency_deploy: true
```

#### Rollback Production
```bash
# Use GitHub Actions UI with rollback_version parameter
# Example: rollback_version: "v1.75.0"
```

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
