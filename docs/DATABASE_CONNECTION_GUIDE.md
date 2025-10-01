# Database Connection Guide

## Overview

This guide explains how to connect to RDS PostgreSQL instances across different environments using various database clients.

## RDS Instance Details

### Environment-Specific Instances

| Environment | Instance ID | Database Name | Port |
|-------------|-------------|---------------|------|
| Dev | `rds-dev` | `storefront_dev` | 5432 |
| Staging | `rds-staging` | `storefront_staging` | 5432 |
| Prod | `rds-prod` | `storefront_prod` | 5432 |

### Connection Information Storage

Credentials are stored in AWS Secrets Manager:
- **Dev**: `storefront/dev/rds-credentials`
- **Staging**: `storefront/staging/rds-credentials`
- **Prod**: `storefront/prod/rds-credentials`

## Getting Connection Details

### Using AWS CLI

```bash
# Get dev database credentials
aws secretsmanager get-secret-value \
  --secret-id storefront/dev/rds-credentials \
  --query SecretString \
  --output text | jq .

# Output:
# {
#   "username": "postgres",
#   "password": "xxx",
#   "host": "rds-dev.xxx.us-east-1.rds.amazonaws.com",
#   "port": 5432,
#   "dbname": "storefront_{env}",
#   "engine": "postgres"
# }
```

### Extract Specific Values

```bash
# Get hostname
RDS_HOST=$(aws secretsmanager get-secret-value \
  --secret-id storefront/dev/rds-credentials \
  --query SecretString --output text | jq -r .host)

# Get password
RDS_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id storefront/dev/rds-credentials \
  --query SecretString --output text | jq -r .password)

# Get username
RDS_USER=$(aws secretsmanager get-secret-value \
  --secret-id storefront/dev/rds-credentials \
  --query SecretString --output text | jq -r .username)

echo "Host: $RDS_HOST"
echo "User: $RDS_USER"
```

## Connection Methods

### 1. psql (Command Line)

#### Direct Connection
```bash
# Get credentials
export PGPASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id storefront/dev/rds-credentials \
  --query SecretString --output text | jq -r .password)

export PGHOST=$(aws secretsmanager get-secret-value \
  --secret-id storefront/dev/rds-credentials \
  --query SecretString --output text | jq -r .host)

# Connect
psql -h $PGHOST -U postgres -d storefront_{env}
```

#### Using Connection String
```bash
# Build connection string
CONN_STRING=$(aws secretsmanager get-secret-value \
  --secret-id storefront/dev/rds-credentials \
  --query SecretString --output text | \
  jq -r '"postgresql://\(.username):\(.password)@\(.host):\(.port)/\(.dbname)"')

# Connect
psql "$CONN_STRING"
```

#### One-liner
```bash
psql "$(aws secretsmanager get-secret-value \
  --secret-id storefront/dev/rds-credentials \
  --query SecretString --output text | \
  jq -r '"postgresql://\(.username):\(.password)@\(.host):\(.port)/\(.dbname)"')"
```

### 2. pgAdmin (GUI)

1. **Get Connection Details**:
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id storefront/dev/rds-credentials \
     --query SecretString --output text | jq .
   ```

2. **Create New Server in pgAdmin**:
   - Right-click "Servers" → Create → Server
   - **General Tab**:
     - Name: `Storefront Dev`
   - **Connection Tab**:
     - Host: `rds-dev.xxx.us-east-1.rds.amazonaws.com`
     - Port: `5432`
     - Maintenance database: `storefront_{env}`
     - Username: `postgres`
     - Password: `[from secrets manager]`
     - Save password: ✓
   - **SSL Tab**:
     - SSL mode: `Require`

3. **Click Save**

### 3. DBeaver (GUI)

1. **Get Connection Details** (same as above)

2. **Create New Connection**:
   - Database → New Database Connection
   - Select **PostgreSQL**
   - Click **Next**

3. **Configure Connection**:
   - **Main Tab**:
     - Host: `rds-dev.xxx.us-east-1.rds.amazonaws.com`
     - Port: `5432`
     - Database: `storefront_{env}`
     - Username: `postgres`
     - Password: `[from secrets manager]`
     - Save password locally: ✓
   
   - **SSL Tab**:
     - Use SSL: ✓
     - SSL mode: `require`

4. **Test Connection** → **Finish**

### 4. DataGrip (JetBrains)

1. **Get Connection Details** (same as above)

2. **Create Data Source**:
   - Database → + → Data Source → PostgreSQL

3. **Configure**:
   - Host: `rds-dev.xxx.us-east-1.rds.amazonaws.com`
   - Port: `5432`
   - Database: `storefront_{env}`
   - User: `postgres`
   - Password: `[from secrets manager]`
   - Save password: ✓

4. **Advanced Settings**:
   - SSL → Mode: `require`

5. **Test Connection** → **OK**

### 5. TablePlus (macOS/Windows)

1. **Get Connection Details** (same as above)

2. **Create New Connection**:
   - Click **+** → PostgreSQL

3. **Configure**:
   - Name: `Storefront Dev`
   - Host: `rds-dev.xxx.us-east-1.rds.amazonaws.com`
   - Port: `5432`
   - User: `postgres`
   - Password: `[from secrets manager]`
   - Database: `storefront_{env}`
   - Over SSL: ✓

4. **Test** → **Connect**

### 6. Python (psycopg2)

```python
import boto3
import json
import psycopg2

# Get credentials from Secrets Manager
def get_db_credentials(secret_id):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_id)
    return json.loads(response['SecretString'])

# Connect to database
creds = get_db_credentials('storefront/dev/rds-credentials')

conn = psycopg2.connect(
    host=creds['host'],
    port=creds['port'],
    database=creds['dbname'],
    user=creds['username'],
    password=creds['password'],
    sslmode='require'
)

# Use connection
cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())

cursor.close()
conn.close()
```

### 7. Node.js (pg)

```javascript
const AWS = require('aws-sdk');
const { Client } = require('pg');

// Get credentials from Secrets Manager
async function getDbCredentials(secretId) {
  const client = new AWS.SecretsManager({ region: 'us-east-1' });
  const data = await client.getSecretValue({ SecretId: secretId }).promise();
  return JSON.parse(data.SecretString);
}

// Connect to database
async function connect() {
  const creds = await getDbCredentials('storefront/dev/rds-credentials');
  
  const client = new Client({
    host: creds.host,
    port: creds.port,
    database: creds.dbname,
    user: creds.username,
    password: creds.password,
    ssl: { rejectUnauthorized: false }
  });
  
  await client.connect();
  
  const res = await client.query('SELECT version()');
  console.log(res.rows[0]);
  
  await client.end();
}

connect();
```

## Security Best Practices

### 1. Use IAM Database Authentication (Optional)

For enhanced security, enable IAM authentication:

```bash
# Generate auth token
TOKEN=$(aws rds generate-db-auth-token \
  --hostname rds-dev.xxx.us-east-1.rds.amazonaws.com \
  --port 5432 \
  --username postgres \
  --region us-east-1)

# Connect using token as password
psql "postgresql://postgres:$TOKEN@rds-dev.xxx.us-east-1.rds.amazonaws.com:5432/storefront_{env}?sslmode=require"
```

### 2. Use SSL/TLS Connections

Always use SSL for connections:
- **psql**: Add `?sslmode=require` to connection string
- **GUI clients**: Enable SSL in connection settings
- **Application code**: Set `sslmode='require'`

### 3. Rotate Credentials Regularly

```bash
# Rotate secret in Secrets Manager
aws secretsmanager rotate-secret \
  --secret-id storefront/dev/rds-credentials \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:xxx:function:SecretsManagerRotation
```

### 4. Use Read-Only Users for Queries

Create read-only users for reporting/analytics:

```sql
-- Connect as postgres user
CREATE USER readonly_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE postgres TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;
```

## Troubleshooting

### Connection Timeout

**Problem**: Connection times out
```
psql: error: connection to server at "rds-dev.xxx.us-east-1.rds.amazonaws.com" (10.0.x.x), port 5432 failed: timeout expired
```

**Solutions**:
1. **Check Security Group**: Ensure your IP is allowed
   ```bash
   # Add your IP to RDS security group
   MY_IP=$(curl -s ifconfig.me)
   aws ec2 authorize-security-group-ingress \
     --group-id sg-xxx \
     --protocol tcp \
     --port 5432 \
     --cidr $MY_IP/32
   ```

2. **Check Public Accessibility**: RDS must be publicly accessible
   ```bash
   aws rds describe-db-instances \
     --db-instance-identifier rds-dev \
     --query 'DBInstances[0].PubliclyAccessible'
   ```

3. **Use VPN/Bastion**: Connect through VPN or bastion host if RDS is private

### Authentication Failed

**Problem**: Password authentication failed
```
psql: error: connection to server failed: FATAL: password authentication failed for user "postgres"
```

**Solutions**:
1. **Verify Credentials**: Check Secrets Manager for correct password
2. **Check Username**: Ensure using correct username (default: `postgres`)
3. **Password Special Characters**: Escape special characters in connection string

### SSL Required

**Problem**: SSL connection required
```
psql: error: connection to server failed: FATAL: no pg_hba.conf entry for host "x.x.x.x", user "postgres", database "storefront_{env}", SSL off
```

**Solution**: Always use SSL
```bash
psql "postgresql://postgres:password@host:5432/storefront_{env}?sslmode=require"
```

### Database Does Not Exist

**Problem**: Database doesn't exist
```
psql: error: connection to server failed: FATAL: database "storefront_dev" does not exist
```

**Solution**: Use correct database name (check Secrets Manager `dbname` field)
```bash
# Check database name
aws secretsmanager get-secret-value \
  --secret-id storefront/dev/rds-credentials \
  --query SecretString --output text | jq -r .dbname
```

## Quick Reference

### Connection String Format
```
postgresql://[user]:[password]@[host]:[port]/[database]?sslmode=require
```

### Common Commands

```bash
# List databases
\l

# Connect to database
\c database_name

# List tables
\dt

# Describe table
\d table_name

# List users
\du

# Show current connection info
\conninfo

# Execute SQL file
\i /path/to/file.sql

# Export query results to CSV
\copy (SELECT * FROM table) TO '/path/to/output.csv' CSV HEADER

# Quit
\q
```

### Environment Variables

```bash
# Set for current session
export PGHOST=rds-dev.xxx.us-east-1.rds.amazonaws.com
export PGPORT=5432
export PGDATABASE=storefront_{env}
export PGUSER=postgres
export PGPASSWORD=xxx

# Then simply run
psql
```

## Automated Connection Script

Create a helper script for easy connections:

```bash
#!/bin/bash
# File: connect-db.sh

ENVIRONMENT=${1:-dev}
SECRET_ID="storefront/${ENVIRONMENT}/rds-credentials"

echo "🔐 Fetching credentials for $ENVIRONMENT..."

CONN_STRING=$(aws secretsmanager get-secret-value \
  --secret-id $SECRET_ID \
  --query SecretString --output text | \
  jq -r '"postgresql://\(.username):\(.password)@\(.host):\(.port)/\(.dbname)?sslmode=require"')

echo "🔌 Connecting to $ENVIRONMENT database..."
psql "$CONN_STRING"
```

**Usage**:
```bash
chmod +x connect-db.sh

# Connect to dev
./connect-db.sh dev

# Connect to staging
./connect-db.sh staging

# Connect to prod
./connect-db.sh prod
```

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [AWS RDS PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [psql Command Reference](https://www.postgresql.org/docs/current/app-psql.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
