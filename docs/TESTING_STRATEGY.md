# Testing Strategy - Multi-Environment CI/CD

## Overview

Comprehensive testing framework for dev, staging, and production environments with automated gates and manual approvals.

## Testing Levels

### 1. Unit Tests
**When**: Every commit, PR, and deployment
**Coverage Requirement**: 80%
**Location**: `/tests/unit/`

```bash
pytest tests/unit/ -v --cov=stacks --cov=apps --cov-report=html
```

**Tests**:
- CDK stack synthesis
- Stack configuration validation
- Resource property verification

### 2. Lint & Security Scanning
**When**: Every commit, PR, and deployment
**Tools**: Black, isort, flake8, Bandit, Safety

```bash
black --check .
isort --check-only .
flake8 .
bandit -r .
safety check
```

### 3. Integration Tests
**When**: After unit tests pass, before deployment
**Environment**: Dev (default), Staging, Prod
**Location**: `/tests/integration/`

```bash
pytest tests/integration/ -v -m "not slow"
```

**Tests**:
- ECS service health and task counts
- RDS database connectivity and status
- SQS queue existence and accessibility
- Route53 hosted zone operations
- Service endpoint responses

### 4. Performance Tests
**When**: After integration tests, on staging environment
**Location**: `/tests/integration/` (marked with `@pytest.mark.performance`)

```bash
pytest tests/integration/ -v -m "performance"
```

**Tests**:
- Domain processing performance under load
- Database connection pooling
- API response times
- Concurrent request handling

## Deployment Pipeline

### Development Environment
```
Code Push → Unit Tests → Lint/Security → Integration Tests → Deploy to Dev
```

**Trigger**: Automatic on push to main
**Approval**: None required
**Testing**: Unit + Lint only (fast feedback)

### Staging Environment
```
Main Branch → Full Test Suite → Deploy to Staging → Post-Deployment Tests → Ready for Prod
```

**Trigger**: Automatic on push to main
**Approval**: None required
**Testing**: Unit + Lint + Integration + Performance
**Post-Deployment**: Health checks and smoke tests

**Workflow**: `.github/workflows/staging-deployment.yml`

### Production Environment
```
Manual Trigger → Staging Validation → Manual Approval → Deploy to Prod → Monitoring
```

**Trigger**: Manual workflow dispatch only
**Approval**: **Required** - GitHub environment protection
**Testing**: Validates staging deployment success
**Safety Features**:
- Staging validation (must be green)
- Manual approval gate
- Emergency deployment option
- Rollback capability

**Workflow**: `.github/workflows/production-deployment.yml`

## Running Tests Locally

### All Tests
```bash
# Install dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=stacks --cov=apps --cov-report=html
```

### Specific Test Types
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Performance tests only
pytest tests/integration/ -v -m "performance"

# Skip slow tests
pytest tests/ -v -m "not slow"
```

### Environment-Specific Tests
```bash
# Test against dev
TEST_ENVIRONMENT=dev pytest tests/integration/ -v

# Test against staging
TEST_ENVIRONMENT=staging pytest tests/integration/ -v

# Test against prod (read-only tests only)
TEST_ENVIRONMENT=prod pytest tests/integration/ -v -m "readonly"
```

## Test Markers

Tests can be marked with pytest markers:

```python
@pytest.mark.slow  # Long-running tests
@pytest.mark.performance  # Performance/load tests
@pytest.mark.readonly  # Safe to run on production
@pytest.mark.destructive  # Modifies data (dev/staging only)
```

## CI/CD Workflows

### Test Suite Workflow
**File**: `.github/workflows/test-suite.yml`
**Trigger**: Pull requests, workflow_call
**Jobs**:
1. Unit Tests (parallel)
2. Lint & Security (parallel)
3. Integration Tests (after unit tests)
4. Performance Tests (after integration)
5. Test Summary (aggregates results)

### Staging Deployment Workflow
**File**: `.github/workflows/staging-deployment.yml`
**Trigger**: Push to main, manual
**Jobs**:
1. Test Gate (runs full test suite)
2. Deploy to Staging (if tests pass)
3. Post-Deployment Tests (health checks)
4. Staging Summary (deployment report)

### Production Deployment Workflow
**File**: `.github/workflows/production-deployment.yml`
**Trigger**: Manual only
**Jobs**:
1. Pre-deployment Validation (checks staging)
2. **Manual Approval Gate** ⚠️
3. Deploy to Production
4. Post-Deployment Monitoring
5. Production Summary

## Environment Protection Rules

### Staging
- ✅ Automatic deployment from main
- ✅ Full test suite required
- ✅ Post-deployment health checks
- ❌ No manual approval

### Production
- ✅ Manual deployment only
- ✅ Staging validation required
- ✅ **Manual approval required**
- ✅ Emergency deployment option
- ✅ Rollback capability

## Test Results

### GitHub Actions
Test results are automatically uploaded as artifacts:
- `unit-test-results` - JUnit XML format
- `integration-test-results` - JUnit XML format
- `performance-test-results` - JUnit XML format
- `coverage-report` - HTML coverage report
- `security-reports` - Bandit and Safety JSON reports

### Viewing Results
1. Go to Actions tab
2. Select workflow run
3. Download artifacts
4. Open HTML reports in browser

## Monitoring and Alerts

### Post-Deployment Monitoring
- Service health checks (60s stabilization period)
- Task count verification
- Database connectivity
- API endpoint responses

### Rollback Triggers
- Health check failures
- Error rate > 5%
- Response time > 2s (p95)
- Task crash loops

## Best Practices

1. **Write tests first** - TDD approach for new features
2. **Keep tests fast** - Unit tests < 1s each
3. **Mark slow tests** - Use `@pytest.mark.slow`
4. **Test in isolation** - No dependencies between tests
5. **Clean up resources** - Use fixtures for setup/teardown
6. **Mock external services** - Unit tests shouldn't hit AWS
7. **Test failure scenarios** - Not just happy paths
8. **Document test purpose** - Clear docstrings

## Troubleshooting

### Tests Failing Locally But Pass in CI
- Check Python version (should be 3.11)
- Verify dependencies: `pip install -r tests/requirements.txt`
- Check AWS credentials if running integration tests

### Integration Tests Failing
- Verify AWS credentials are configured
- Check environment variable: `TEST_ENVIRONMENT=dev`
- Ensure services are deployed and running
- Check security group rules allow test access

### Performance Tests Timing Out
- Increase timeout: `pytest --timeout=300`
- Check staging environment resources
- Verify no rate limiting or throttling

## Next Steps

1. ✅ Enable integration tests (now active)
2. ✅ Enable performance tests (now active)
3. ✅ Enable staging deployment (now active)
4. ⏳ Set up GitHub environment protection for prod
5. ⏳ Configure Slack/email notifications
6. ⏳ Add more performance test scenarios
7. ⏳ Implement automated rollback on failures

## References

- [Test Suite Workflow](.github/workflows/test-suite.yml)
- [Staging Deployment](.github/workflows/staging-deployment.yml)
- [Production Deployment](.github/workflows/production-deployment.yml)
- [Multi-Environment Deployment](MULTI_ENVIRONMENT_DEPLOYMENT.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
