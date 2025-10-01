# RDS to RDS Backup Script

Comprehensive script for backing up and restoring PostgreSQL RDS instances using either logical backups (pg_dump) or AWS snapshots.

## Features

- **Two backup methods**: pg_dump (logical) or AWS snapshots (physical)
- **Secrets Manager integration**: Automatically fetch credentials from AWS Secrets Manager
- **Environment variable configuration**: Flexible configuration via environment variables
- **Automatic database creation**: Creates target database if it doesn't exist
- **Clean restore option**: Optionally clean target database before restore
- **Colored output**: Easy-to-read status messages
- **Error handling**: Comprehensive error checking and validation

## Prerequisites

### For pg_dump Method
- PostgreSQL client tools (pg_dump, pg_restore, psql) matching your RDS version
- AWS CLI configured with appropriate credentials
- `jq` for JSON parsing (if using Secrets Manager)

### For Snapshot Method
- AWS CLI configured with appropriate credentials
- Appropriate IAM permissions for RDS snapshot operations

## Installation

### Install PostgreSQL 17 Client Tools

```bash
# macOS
brew install postgresql@17

# Add to PATH (add to ~/.zshrc or ~/.bashrc for persistence)
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"

# Verify installation
pg_dump --version  # Should show version 17.x
```

### Install jq (for Secrets Manager support)

```bash
# macOS
brew install jq

# Linux (Debian/Ubuntu)
sudo apt-get install jq

# Linux (RHEL/CentOS)
sudo yum install jq
```

## Usage

### Method 1: pg_dump (Logical Backup)

Best for:
- Selective backup/restore
- Cross-version PostgreSQL migrations
- Smaller databases
- When you need data-only or schema-only backups

#### Using Secrets Manager (Recommended)

```bash
SOURCE_SECRET_ARN=arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:storefront/dev/rds-credentials-XXX \
TARGET_SECRET_ARN=arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:storefront/staging/rds-credentials-XXX \
SOURCE_DB=postgres \
TARGET_DB=postgres \
./scripts/backup-rds-to-rds.sh pg_dump
```

#### Using Direct Credentials

```bash
SOURCE_HOST=dev-db.xxx.rds.amazonaws.com \
SOURCE_PORT=5432 \
SOURCE_DB=postgres \
SOURCE_USER=postgres \
SOURCE_PASSWORD=your-password \
TARGET_HOST=staging-db.xxx.rds.amazonaws.com \
TARGET_PORT=5432 \
TARGET_DB=postgres \
TARGET_USER=postgres \
TARGET_PASSWORD=your-password \
./scripts/backup-rds-to-rds.sh pg_dump
```

#### With Clean Option (Drops existing objects first)

```bash
SOURCE_SECRET_ARN=... \
TARGET_SECRET_ARN=... \
SOURCE_DB=postgres \
TARGET_DB=postgres \
CLEAN_FIRST=true \
./scripts/backup-rds-to-rds.sh pg_dump
```

#### Custom Backup File Location

```bash
SOURCE_SECRET_ARN=... \
TARGET_SECRET_ARN=... \
SOURCE_DB=postgres \
TARGET_DB=postgres \
BACKUP_FILE=/path/to/backup.dump \
./scripts/backup-rds-to-rds.sh pg_dump
```

### Method 2: AWS Snapshot (Physical Backup)

Best for:
- Large databases
- Full instance backup/restore
- Point-in-time recovery
- When you want AWS-managed backups

```bash
SOURCE_INSTANCE_ID=dev-db \
TARGET_INSTANCE_ID=staging-db-restored \
SNAPSHOT_ID=backup-20250930 \
INSTANCE_CLASS=db.t3.micro \
AWS_REGION=us-east-1 \
./scripts/backup-rds-to-rds.sh snapshot
```

## Environment Variables

### pg_dump Method

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SOURCE_HOST` | Yes* | - | Source RDS endpoint |
| `SOURCE_PORT` | No | 5432 | Source database port |
| `SOURCE_DB` | No | storefront | Source database name |
| `SOURCE_USER` | No | postgres | Source database username |
| `SOURCE_PASSWORD` | Yes* | - | Source database password |
| `SOURCE_SECRET_ARN` | Yes* | - | AWS Secrets Manager ARN for source credentials |
| `TARGET_HOST` | Yes* | - | Target RDS endpoint |
| `TARGET_PORT` | No | 5432 | Target database port |
| `TARGET_DB` | No | storefront | Target database name |
| `TARGET_USER` | No | postgres | Target database username |
| `TARGET_PASSWORD` | Yes* | - | Target database password |
| `TARGET_SECRET_ARN` | Yes* | - | AWS Secrets Manager ARN for target credentials |
| `BACKUP_FILE` | No | /tmp/rds_backup_TIMESTAMP.dump | Path to backup file |
| `CLEAN_FIRST` | No | false | Clean target database before restore |

\* Either provide direct credentials (HOST, PASSWORD) OR Secrets Manager ARN

### snapshot Method

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SOURCE_INSTANCE_ID` | Yes | - | Source RDS instance identifier |
| `TARGET_INSTANCE_ID` | Yes | - | Target RDS instance identifier |
| `SNAPSHOT_ID` | No | backup-TIMESTAMP | Snapshot identifier |
| `INSTANCE_CLASS` | No | db.t3.micro | Instance class for restored instance |
| `AWS_REGION` | No | us-east-1 | AWS region |

## Secrets Manager Format

The script expects Secrets Manager secrets in this format:

```json
{
  "username": "postgres",
  "password": "your-password",
  "host": "your-db.xxx.rds.amazonaws.com",
  "port": 5432,
  "dbname": "postgres",
  "engine": "postgres"
}
```

This is the default format created by RDS when you enable Secrets Manager integration.

## Examples

### Example 1: Backup Dev to Staging

```bash
#!/bin/bash
# backup-dev-to-staging.sh

SOURCE_SECRET_ARN=arn:aws:secretsmanager:us-east-1:156041439702:secret:storefront/dev/rds-credentials-Rrah6R
TARGET_SECRET_ARN=arn:aws:secretsmanager:us-east-1:156041439702:secret:storefront/staging/rds-credentials-vV0Zcv

SOURCE_DB=postgres
TARGET_DB=postgres
CLEAN_FIRST=true

./scripts/backup-rds-to-rds.sh pg_dump
```

### Example 2: Create Snapshot and Restore

```bash
#!/bin/bash
# snapshot-and-restore.sh

SOURCE_INSTANCE_ID=prod-db
TARGET_INSTANCE_ID=prod-db-clone
SNAPSHOT_ID=prod-backup-$(date +%Y%m%d)
INSTANCE_CLASS=db.t3.medium
AWS_REGION=us-east-1

./scripts/backup-rds-to-rds.sh snapshot
```

### Example 3: Backup to Local File Only

```bash
# Just backup, don't restore
SOURCE_SECRET_ARN=arn:aws:secretsmanager:us-east-1:xxx:secret:prod/rds-xxx
SOURCE_DB=postgres
BACKUP_FILE=./prod-backup-$(date +%Y%m%d).dump

# Modify script to skip restore or just run pg_dump directly
pg_dump -h $(aws secretsmanager get-secret-value --secret-id $SOURCE_SECRET_ARN --query SecretString --output text | jq -r .host) \
        -U postgres \
        -d postgres \
        -Fc \
        -f $BACKUP_FILE
```

## Troubleshooting

### Version Mismatch Error

```
pg_dump: error: server version: 17.6; pg_dump version: 14.19
pg_dump: error: aborting because of server version mismatch
```

**Solution**: Install PostgreSQL client tools matching your RDS version:
```bash
brew install postgresql@17
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
```

### Connection Failed

```
connection to server at "xxx.rds.amazonaws.com" failed
```

**Possible causes**:
- Security group not allowing your IP
- Wrong credentials
- RDS instance not publicly accessible
- VPC/subnet configuration issues

**Solution**: 
- Check RDS security group inbound rules
- Verify credentials in Secrets Manager
- Ensure RDS instance is publicly accessible (or use bastion host)

### Database Does Not Exist

```
FATAL: database "storefront" does not exist
```

**Solution**: Check the actual database name in your RDS instance:
```bash
psql -h your-db.rds.amazonaws.com -U postgres -d postgres -c "\l"
```

Set `SOURCE_DB` and `TARGET_DB` to the correct database name (often `postgres`).

### Permission Denied

```
ERROR: permission denied to create database
```

**Solution**: Ensure your database user has appropriate permissions:
```sql
GRANT CREATE ON DATABASE postgres TO your_user;
```

Or use a superuser account (like `postgres`).

## Best Practices

1. **Test restores regularly**: Verify backups work by testing restores to a temporary instance
2. **Use Secrets Manager**: Avoid hardcoding credentials in scripts
3. **Monitor backup size**: Large databases may take significant time and storage
4. **Clean up old backups**: Remove temporary backup files after successful restore
5. **Use snapshots for large databases**: Snapshots are faster for databases > 100GB
6. **Verify data after restore**: Always check data integrity after restore
7. **Schedule regular backups**: Use cron or AWS EventBridge for automated backups
8. **Tag snapshots**: Use meaningful snapshot IDs with dates and purposes

## Automation

### Cron Job Example

```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup-rds-to-rds.sh pg_dump >> /var/log/rds-backup.log 2>&1
```

### AWS Lambda Example

Create a Lambda function that runs this script in a container or uses boto3 for snapshot operations.

## Security Considerations

- Never commit credentials to version control
- Use IAM roles and Secrets Manager for credential management
- Restrict security groups to known IP addresses
- Enable encryption at rest for RDS instances
- Use SSL/TLS for database connections
- Rotate credentials regularly
- Audit backup access with CloudTrail

## Performance Tips

- **pg_dump**: Use `--jobs` flag for parallel dumps of large databases
- **Compression**: Backup files are compressed by default (`--compress=9`)
- **Network**: Run from EC2 instance in same region as RDS for faster transfers
- **Snapshots**: Faster for databases > 100GB
- **Incremental**: Consider AWS Backup for incremental backups

## Support

For issues or questions:
1. Check CloudWatch Logs for RDS errors
2. Verify IAM permissions for Secrets Manager and RDS
3. Test connectivity with `psql` directly
4. Check script output for specific error messages

## License

This script is part of the aws-fargate-cdk infrastructure project.
