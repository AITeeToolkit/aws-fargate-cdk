# Security Group IP Management

## Overview

All security groups in the infrastructure support dynamic IP allowlisting via CDK context. This allows you to add your IP addresses without modifying code.

## Quick Start

### Add IPs via cdk.json (Persistent)

Edit `cdk.json` and add:

```json
{
  "context": {
    "allowed_ips": [
      "70.122.3.208/32",
      "192.168.1.100/32",
      "10.0.0.0/8"
    ]
  }
}
```

Then deploy:
```bash
cdk deploy --all
```

### Add IPs via Command Line (One-time)

```bash
# Single environment
cdk deploy --all --context env=dev \
  --context allowed_ips='["70.122.3.208/32","192.168.1.100/32"]'

# All environments
for env in dev staging prod; do
  cdk deploy --all --context env=$env \
    --context allowed_ips='["70.122.3.208/32"]'
done
```

## What Gets Updated

When you add IPs via context, the following resources are automatically updated:

### 1. RDS Database Security Groups (All 3 Environments)
- **Port**: 5432 (PostgreSQL)
- **Resources**: `rds-dev`, `rds-staging`, `rds-prod`
- **Access**: Direct database connections
- **Use Case**: Database clients (pgAdmin, DBeaver, psql)

### 2. ECS Task Security Group
- **Ports**: 3000 (web service), 3001 (API service)
- **Access**: Direct container access
- **Use Case**: Debugging, testing, direct API calls

### 3. OpenSearch Domain Access Policy
- **Port**: 443 (HTTPS)
- **Access**: OpenSearch API and Dashboards
- **Use Case**: Kibana/OpenSearch Dashboards, direct API queries
- **Note**: Uses IAM policy conditions, not security groups

## Get Your Current IP

```bash
# Get your public IP
curl -s ifconfig.me

# Add to CDK context
MY_IP=$(curl -s ifconfig.me)
cdk deploy --all --context allowed_ips="[\"$MY_IP/32\"]"
```

## IP Format

Always use CIDR notation:
- **Single IP**: `70.122.3.208/32`
- **Subnet**: `10.0.0.0/24`
- **Range**: `192.168.1.0/16`

## Examples

### Example 1: Add Your Home and Office IPs

```json
{
  "context": {
    "allowed_ips": [
      "70.122.3.208/32", 
      "203.0.113.50/32"    
    ]
  }
}
```

### Example 2: Add Entire Office Network

```json
{
  "context": {
    "allowed_ips": [
      "10.0.0.0/8",          
      "203.0.113.0/24"       
    ]
  }
}
```

### Example 3: Temporary Access via CLI

```bash
# Add IP for this deployment only (not saved)
cdk deploy DatabaseStack-dev --context env=dev \
  --context allowed_ips='["$(curl -s ifconfig.me)/32"]'
```

### Example 4: Environment-Specific IPs

You can use different IPs per environment by checking the environment in code, but the simplest approach is to deploy with different context:

```bash
# Dev - allow all developers
cdk deploy --all --context env=dev \
  --context allowed_ips='["70.122.3.208/32","192.168.1.100/32"]'

# Prod - restrict to ops team only
cdk deploy --all --context env=prod \
  --context allowed_ips='["203.0.113.50/32"]'
```

## Verify Security Group Rules

### Via AWS Console
1. Go to EC2 → Security Groups
2. Search for:
   - `DatabaseSecurityGroup-{env}`
   - `AlbSecurityGroup`
   - `ECSTaskSecurityGroup`
3. Check "Inbound rules" tab

### Via AWS CLI

```bash
# Get RDS security group rules
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=*DatabaseSecurityGroup*" \
  --query 'SecurityGroups[*].[GroupId,GroupName,IpPermissions]' \
  --output table

# Get ALB security group rules
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=*AlbSecurityGroup*" \
  --query 'SecurityGroups[*].[GroupId,GroupName,IpPermissions]' \
  --output table
```

## Remove IP Access

### Option 1: Update cdk.json (Recommended)

Remove the IP from the list and redeploy:

```json
{
  "context": {
    "allowed_ips": [
      "192.168.1.100/32"
    ]
  }
}
```

Then deploy:
```bash
cdk deploy --all --require-approval never
```

### Option 2: Update via Command Line

**Important**: When deploying with `--context allowed_ips`, you must specify the same IPs for ALL deployments. Otherwise, CDK will overwrite security groups with only the IPs from the current deployment.

**Correct approach** - Store IPs in cdk.json:
```json
{
  "context": {
    "allowed_ips": {
      "70.122.3.208/32": "Nel home",
      "75.40.190.44/32": "Raphael home"
    }
  }
}
```

Then deploy without context flags:
```bash
cdk deploy --all --require-approval never
```

**Why this matters**: If you deploy different stacks separately with different `--context allowed_ips` values, each deployment will overwrite the security group rules with only the IPs specified in that deployment.

### Option 3: Manual Removal via AWS CLI

```bash
# Get security group ID
SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=*DatabaseSecurityGroup-dev*" \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

# Revoke ingress rule
aws ec2 revoke-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 5432 \
  --cidr 70.122.3.208/32
```

## Security Best Practices

### 1. Use /32 for Single IPs
Always use `/32` suffix for individual IP addresses:
```json
"allowed_ips": ["70.122.3.208/32"] 
"allowed_ips": ["70.122.3.208"] 
```

### 2. Limit Production Access
Only allow necessary IPs in production:
```json
Dev - more permissive
"allowed_ips": ["10.0.0.0/8", "70.122.3.208/32"]

Prod - restrictive
"allowed_ips": ["203.0.113.50/32"]      
```

### 3. Use VPN for Team Access
Instead of adding many individual IPs, use a VPN:
```json
"allowed_ips": ["vpn.company.com/32"]
```

### 4. Rotate IPs Regularly
Review and remove unused IPs monthly:
```bash
# List all custom ingress rules
aws ec2 describe-security-groups \
  --query 'SecurityGroups[*].IpPermissions[?contains(IpRanges[].Description, `external`)]'
```

### 5. Use Bastion Host for Production
For production database access, use a bastion host instead of direct IP allowlisting:
```bash
# SSH tunnel through bastion
ssh -L 5432:rds-prod.xxx.rds.amazonaws.com:5432 user@bastion.company.com

# Connect to localhost
psql -h localhost -U postgres -d storefront_prod
```

## Troubleshooting

### IP Not Working After Deployment

1. **Verify IP was added**:
   ```bash
   aws ec2 describe-security-groups \
     --filters "Name=group-name,Values=*DatabaseSecurityGroup*" \
     --query 'SecurityGroups[*].IpPermissions[*].IpRanges[*].CidrIp'
   ```

2. **Check your current IP**:
   ```bash
   curl -s ifconfig.me
   # Compare with IP in security group
   ```

3. **Verify CIDR format**:
   - Must include `/32` for single IP
   - Must be valid CIDR notation

### Connection Still Timing Out

1. **Check RDS is publicly accessible**:
   ```bash
   aws rds describe-db-instances \
     --db-instance-identifier rds-dev \
     --query 'DBInstances[0].PubliclyAccessible'
   ```

2. **Verify VPC route tables**:
   - Internet Gateway attached
   - Route to 0.0.0.0/0 exists

3. **Check Network ACLs**:
   - Default ACLs allow all traffic
   - Custom ACLs may block

### Dynamic IP Address

If your IP changes frequently:

**Option 1: Use Dynamic DNS**
```bash
# Update IP automatically
MY_IP=$(curl -s ifconfig.me)
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 5432 \
  --cidr $MY_IP/32
```

**Option 2: Use VPN with Static IP**

**Option 3: Use AWS Client VPN**

## Automation

### Script to Update Your IP

```bash
#!/bin/bash
# File: update-my-ip.sh

# Get current IP
CURRENT_IP=$(curl -s ifconfig.me)
echo "Current IP: $CURRENT_IP"

# Update cdk.json
jq --arg ip "$CURRENT_IP/32" '.context.allowed_ips = [$ip]' cdk.json > cdk.json.tmp
mv cdk.json.tmp cdk.json

# Deploy
echo "Deploying with updated IP..."
cdk deploy --all --require-approval never

echo "✅ Security groups updated with IP: $CURRENT_IP"
```

**Usage**:
```bash
chmod +x update-my-ip.sh
./update-my-ip.sh
```

### GitHub Actions Integration

Add to your deployment workflow:

```yaml
- name: Add GitHub Actions IP to security groups
  run: |
    RUNNER_IP=$(curl -s ifconfig.me)
    echo "Runner IP: $RUNNER_IP"
    cdk deploy --all \
      --context allowed_ips="[\"$RUNNER_IP/32\"]" \
      --require-approval never
```

## Additional Resources

- [AWS Security Groups Documentation](https:docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)
- [CIDR Notation Guide](https:en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
- [Database Connection Guide](./DATABASE_CONNECTION_GUIDE.md)
