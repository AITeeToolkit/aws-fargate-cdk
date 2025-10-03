# Branch Protection Configuration

This document describes the recommended branch protection rules for the `main` branch.

## GitHub Branch Protection Settings

Navigate to: **Settings → Branches → Add branch protection rule**

### Rule Configuration for `main` branch:

#### 1. Require Pull Request Reviews
- ✅ **Require a pull request before merging**
- ✅ **Require approvals**: 1 (can be 0 for solo projects)
- ✅ **Dismiss stale pull request approvals when new commits are pushed**

#### 2. Require Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**

**Required status checks:**
- Existing test gate workflows (test-suite.yml or similar)
- Pre-commit hooks handle formatting locally

#### 3. Additional Settings
- ✅ **Require conversation resolution before merging**
- ✅ **Do not allow bypassing the above settings** (recommended for teams)
- ❌ **Allow force pushes** (disabled for safety)
- ❌ **Allow deletions** (disabled for safety)

## Setup Instructions

### 1. Install Pre-commit Hooks (Local Development)

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
cd /Users/nel/Repos/aws-fargate-cdk
pre-commit install

# Test it works
pre-commit run --all-files
```

### 2. Enable Branch Protection (GitHub)

1. Go to: https://github.com/AITeeToolkit/aws-fargate-cdk/settings/branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Configure settings as listed above
5. Click "Create" or "Save changes"

### 3. Verify CI Checks

Push a test commit to a feature branch and create a PR:

```bash
git checkout -b test-branch-protection
echo "# Test" >> README.md
git add README.md
git commit -m "test: verify branch protection"
git push origin test-branch-protection
```

Then create a PR and verify:
- ✅ Pre-commit hooks ran locally
- ✅ CI format checks run on GitHub
- ✅ PR cannot be merged until checks pass

## Benefits

### Pre-commit Hooks (#1)
- Catches formatting issues before commit
- Runs instantly on developer machine
- Prevents bad code from entering Git history

### CI Format Checks (#2)
- Validates code quality on every PR
- Catches issues that bypass pre-commit hooks
- Provides clear error messages with fix instructions

### Branch Protection (#3)
- Enforces quality gates at repository level
- Prevents direct pushes to main
- Ensures all code goes through review + checks

### DNS Worker Tag-based Updates (#4)
- DNS worker only uses released, stable code
- Uncommitted changes never affect domain updates
- Clear separation between development and automation

## Troubleshooting

### Pre-commit hook not running?

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Update hooks to latest version
pre-commit autoupdate
```

### CI check failing?

```bash
# Run locally to see what's wrong
black --check --line-length=100 .
isort --check --profile=black --line-length=100 .

# Auto-fix issues
black .
isort --profile=black .
```

### Need to bypass checks temporarily?

```bash
# Skip pre-commit hooks (not recommended)
git commit --no-verify -m "emergency fix"

# Note: CI checks will still run and may block PR
```

## Maintenance

### Update black version

Edit `.pre-commit-config.yaml`:
```yaml
- repo: https://github.com/psf/black
  rev: 24.10.0  # Update this version
```

Then run:
```bash
pre-commit autoupdate
```

### Add new status checks

1. Add new job to `.github/workflows/code-quality.yml`
2. Update branch protection rules to require the new check
3. Test with a PR to verify it works
