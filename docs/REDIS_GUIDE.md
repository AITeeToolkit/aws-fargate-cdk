# ElastiCache Serverless (Valkey) Guide

## Overview

This project uses **AWS ElastiCache Serverless for Valkey** to provide a cost-effective, fully-managed caching solution across all environments.

**What is Valkey?**
Valkey is an open-source, high-performance key-value datastore that is fully compatible with Redis OSS APIs. AWS ElastiCache Serverless uses Valkey as the underlying engine, providing Redis-compatible caching without Redis licensing concerns.

## Architecture

```
Application (ECS Fargate)
    ↓
ElastiCache Serverless (Valkey Engine)
    ↓
VPC Private Subnets
```

**Key Features:**
- **Valkey Engine**: 100% Redis OSS API compatible
- **Serverless**: Auto-scales based on workload
- **Pay-per-use**: Only pay for storage and compute used
- **Multi-AZ**: Automatic failover and high availability
- **Snapshots**: Daily automated backups

## Cost Structure

### Environment Configuration

| Environment | Max Storage | Max ECPU | Storage Cost/Month | ECPU Cost/Month (light) | Total Est. Cost |
|-------------|-------------|----------|-------------------|------------------------|-----------------|
| **dev**     | 200 MB      | 3,000    | ~$12              | ~$0.07-$0.70          | ~$12-$13       |
| **staging** | 200 MB      | 5,000    | ~$12              | ~$0.07-$0.70          | ~$12-$13       |
| **prod**    | 200 MB      | 10,000   | ~$12              | ~$0.07-$0.70          | ~$12-$13       |

**Total estimated cost:** ~$36-$39/month for all environments

**Note**: Storage is the primary cost driver. Start with 200 MB and increase based on actual usage metrics.

### Pricing Breakdown (ElastiCache Serverless - US East N. Virginia)

**Storage Costs:**
- **Rate**: $0.0837 per GB-hour
- **Monthly calculation**: GB-hour * 730 hours/month
- **Dev (1 GB)**: 1 GB * $0.0837/hr * 730 hrs = ~$61/month
- **Staging (2 GB)**: 2 GB * $0.0837/hr * 730 hrs = ~$122/month
- **Prod (5 GB)**: 5 GB * $0.0837/hr * 730 hrs = ~$305/month
- **Minimum**: 100 MB for Valkey (1 GB for Redis OSS)

**Compute Costs (ECPU):**
- **Rate**: $0.00227 per million ECPUs
- **ECPU**: ElastiCache Processing Unit (vCPU time + data transferred)
- **Calculation**: 1 ECPU per KB of data transferred
- **Example**: GET request transferring 3.2 KB = 3.2 ECPUs
- **Light usage**: 10M requests/day * 1 ECPU = ~$0.07/month
- **Heavy usage**: 100M requests/day * 1 ECPU = ~$0.70/month

**Data Transfer:**
- **Within same AZ**: Free
- **Cross-AZ**: Free for ElastiCache Serverless
- **To Internet**: Standard AWS data transfer rates ($0.09/GB first 10 TB)

**Snapshot Storage:**
- **Included**: Daily automated snapshots included
- **Retention**: 1-7 days based on environment
- **No additional cost** for snapshot storage within retention period

### Cost Optimization Tips

1. **Right-size limits**: Start with lower limits and increase based on metrics
2. **Use TTLs**: Set expiration on cached data to reduce storage
3. **Monitor ECPU usage**: Adjust max_ecpu based on actual consumption
4. **Connection pooling**: Reduce overhead by reusing connections
5. **Efficient key design**: Use shorter key names and compact data structures

## Configuration

### Environment-Specific Limits

The stack automatically configures limits based on environment:

```python
# Dev environment
max_storage = 1 GB
max_ecpu = 3000

# Staging environment  
max_storage = 2 GB
max_ecpu = 5000

# Production environment
max_storage = 5 GB
max_ecpu = 10000
```

### Snapshots

- **Dev:** 1 day retention
- **Staging/Prod:** 7 days retention
- **Backup time:** 3:00 AM UTC daily

## Connection Information

### Retrieving Endpoint

The Valkey endpoint is stored in SSM Parameter Store:

```bash
# Get Valkey endpoint
aws ssm get-parameter \
  --name "/storefront-dev/redis/endpoint" \
  --query "Parameter.Value" \
  --output text

# Get Valkey port (default: 6379)
aws ssm get-parameter \
  --name "/storefront-dev/redis/port" \
  --query "Parameter.Value" \
  --output text
```

**Note**: Despite using Valkey, the parameter paths use "redis" for backward compatibility.

### Environment Variables

Set these in your ECS task definitions:

```bash
REDIS_HOST=/storefront-${ENVIRONMENT}/redis/endpoint
REDIS_PORT=/storefront-${ENVIRONMENT}/redis/port
REDIS_ENABLED=true  # Set to 'false' to disable caching
```

**Valkey Compatibility**: All Redis client libraries work seamlessly with Valkey since it's 100% Redis OSS API compatible.

## Application Integration

### Node.js (API/Web)

**Installation:**
```bash
npm install redis @aws-sdk/client-ssm
```

**Connection Example:**
```javascript
const { createClient } = require('redis');
const { SSMClient, GetParameterCommand } = require('@aws-sdk/client-ssm');

// Get Valkey config from SSM
const ssm = new SSMClient({ region: 'us-east-1' });
const environment = process.env.ENVIRONMENT || 'dev';

async function getRedisConfig() {
  const [hostParam, portParam] = await Promise.all([
    ssm.send(new GetParameterCommand({
      Name: `/storefront-${environment}/redis/endpoint`
    })),
    ssm.send(new GetParameterCommand({
      Name: `/storefront-${environment}/redis/port`
    }))
  ]);
  
  return {
    host: hostParam.Parameter.Value,
    port: parseInt(portParam.Parameter.Value)
  };
}

// Create Valkey client (uses Redis client library)
async function createRedisClient() {
  const config = await getRedisConfig();
  
  console.log(`Connecting to ElastiCache Valkey at ${config.host}:${config.port}`);
  
  const client = createClient({
    socket: {
      host: config.host,
      port: config.port,
      connectTimeout: 10000,
      keepAlive: true,
      reconnectStrategy: (retries) => {
        if (retries > 10) return new Error('Max reconnection attempts reached');
        return Math.min(retries * 100, 3000); // Exponential backoff
      }
    }
  });
  
  client.on('error', (err) => console.error('Valkey Client Error:', err));
  client.on('connect', () => console.log('Connected to ElastiCache Valkey'));
  client.on('ready', () => console.log('Valkey client ready'));
  
  await client.connect();
  return client;
}

// Usage
const redisClient = await createRedisClient();
await redisClient.set('key', 'value', { EX: 3600 }); // 1 hour TTL
const value = await redisClient.get('key');
```

**See `/api/src/config/redis.ts` for production implementation with fallback handling.**

### Python (Listener/DNS Worker)

**Installation:**
```bash
pip install redis boto3
```

**Connection Example:**
```python
import boto3
import redis
import os

def get_redis_config():
    """Get Valkey configuration from SSM Parameter Store"""
    ssm = boto3.client('ssm', region_name='us-east-1')
    environment = os.getenv('ENVIRONMENT', 'dev')
    
    host = ssm.get_parameter(
        Name=f'/storefront-{environment}/redis/endpoint'
    )['Parameter']['Value']
    
    port = ssm.get_parameter(
        Name=f'/storefront-{environment}/redis/port'
    )['Parameter']['Value']
    
    return host, int(port)

def create_redis_client():
    """Create Valkey client (uses Redis client library)"""
    host, port = get_redis_config()
    
    print(f"Connecting to ElastiCache Valkey at {host}:{port}")
    
    client = redis.Redis(
        host=host,
        port=port,
        decode_responses=True,
        socket_connect_timeout=10,
        socket_timeout=5,
        socket_keepalive=True,
        retry_on_timeout=True,
        health_check_interval=30
    )
    
    # Test connection
    client.ping()
    print("✅ Connected to ElastiCache Valkey")
    
    return client

# Usage
redis_client = create_redis_client()
redis_client.setex('key', 3600, 'value')  # 1 hour TTL
value = redis_client.get('key')
```

## Common Use Cases

### 1. Session Storage

```javascript
// Store session
await redisClient.setEx(
  `session:${sessionId}`,
  3600, // 1 hour TTL
  JSON.stringify(sessionData)
);

// Retrieve session
const session = await redisClient.get(`session:${sessionId}`);
```

### 2. API Response Caching

```javascript
// Cache API response
await redisClient.setEx(
  `api:products:${productId}`,
  300, // 5 minutes TTL
  JSON.stringify(productData)
);

// Get cached response
const cached = await redisClient.get(`api:products:${productId}`);
if (cached) {
  return JSON.parse(cached);
}
```

### 3. Rate Limiting

```javascript
// Increment request count
const count = await redisClient.incr(`ratelimit:${userId}:${minute}`);
await redisClient.expire(`ratelimit:${userId}:${minute}`, 60);

if (count > 100) {
  throw new Error('Rate limit exceeded');
}
```

### 4. Distributed Locks

```python
# Acquire lock
lock_acquired = redis_client.set(
    f'lock:{resource_id}',
    'locked',
    nx=True,  # Only set if not exists
    ex=30     # 30 second expiry
)

if lock_acquired:
    try:
        # Do work
        process_resource(resource_id)
    finally:
        # Release lock
        redis_client.delete(f'lock:{resource_id}')
```

## Security

### Network Security

- **Valkey runs in private subnets only** - No public internet access
- **Security group** allows traffic only from VPC CIDR (10.0.0.0/16)
- **VPC isolation** - All traffic stays within the VPC
- **No authentication required** - Security through VPC isolation (Valkey Serverless doesn't support AUTH)
- **Encryption in transit** - TLS 1.2+ for all connections
- **Encryption at rest** - Data encrypted using AWS-managed keys

### IAM Permissions

ECS tasks need SSM read permissions to retrieve Valkey endpoint:

```json
{
  "Effect": "Allow",
  "Action": [
    "ssm:GetParameter",
    "ssm:GetParameters"
  ],
  "Resource": [
    "arn:aws:ssm:us-east-1:156041439702:parameter/storefront-*/redis/*"
  ]
}
```

**Note**: No ElastiCache-specific IAM permissions needed - access is controlled via VPC security groups.

## Monitoring

### CloudWatch Metrics

ElastiCache Serverless (Valkey) provides these key metrics:

**Storage Metrics:**
- **BytesUsedForCache** - Current memory usage (compare to max_storage)
- **DatabaseMemoryUsagePercentage** - Percentage of max storage used

**Compute Metrics:**
- **ElastiCacheProcessingUnits** - Current ECPU usage
- **ECPUUtilization** - Percentage of max ECPU used

**Performance Metrics:**
- **CacheHits** - Successful cache retrievals
- **CacheMisses** - Cache misses (higher = less efficient caching)
- **CacheHitRate** - Percentage of successful cache hits

**Connection Metrics:**
- **CurrConnections** - Active client connections
- **NewConnections** - New connections per minute

**Network Metrics:**
- **NetworkBytesIn** - Data received by Valkey
- **NetworkBytesOut** - Data sent from Valkey
- **NetworkPacketsIn/Out** - Packet counts

**Latency Metrics:**
- **StringBasedCmdsLatency** - Average latency for string commands (GET, SET)
- **HashBasedCmdsLatency** - Average latency for hash commands (HGET, HSET)

### Recommended CloudWatch Alarms

```bash
# High storage usage (80% of max)
aws cloudwatch put-metric-alarm \
  --alarm-name "valkey-high-storage-${ENVIRONMENT}" \
  --metric-name DatabaseMemoryUsagePercentage \
  --namespace AWS/ElastiCache \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=CacheClusterId,Value=storefront-${ENVIRONMENT}-valkey

# High ECPU usage (80% of max)
aws cloudwatch put-metric-alarm \
  --alarm-name "valkey-high-ecpu-${ENVIRONMENT}" \
  --metric-name ECPUUtilization \
  --namespace AWS/ElastiCache \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# Low cache hit rate (<80%)
aws cloudwatch put-metric-alarm \
  --alarm-name "valkey-low-hit-rate-${ENVIRONMENT}" \
  --metric-name CacheHitRate \
  --namespace AWS/ElastiCache \
  --statistic Average \
  --period 300 \
  --evaluation-periods 3 \
  --threshold 80 \
  --comparison-operator LessThanThreshold

# High connection count
aws cloudwatch put-metric-alarm \
  --alarm-name "valkey-high-connections-${ENVIRONMENT}" \
  --metric-name CurrConnections \
  --namespace AWS/ElastiCache \
  --statistic Average \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold
```

## Troubleshooting

### Connection Issues

**Symptom**: Application can't connect to Valkey

1. **Check security group rules:**
```bash
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=*Redis*" \
  --query 'SecurityGroups[*].{Name:GroupName,ID:GroupId,Rules:IpPermissions}'
```

2. **Verify endpoint is accessible from ECS task:**
```bash
# Get endpoint
ENDPOINT=$(aws ssm get-parameter --name /storefront-dev/redis/endpoint --query 'Parameter.Value' --output text)

# Test from ECS task (requires execute-command enabled)
aws ecs execute-command --cluster storefront-cluster \
  --task <task-id> \
  --container api-service \
  --interactive \
  --command "/bin/sh -c 'nc -zv $ENDPOINT 6379'"
```

3. **Check SSM parameters exist:**
```bash
aws ssm get-parameters-by-path \
  --path "/storefront-dev/redis/" \
  --query 'Parameters[*].{Name:Name,Value:Value}'
```

4. **Verify ElastiCache Serverless cache is active:**
```bash
aws elasticache describe-serverless-caches \
  --serverless-cache-name storefront-dev-valkey \
  --query 'ServerlessCaches[0].Status'
```

### Performance Issues

**Symptom**: Slow cache operations or high latency

1. **Check ECPU utilization:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name ECPUUtilization \
  --dimensions Name=CacheClusterId,Value=storefront-dev-valkey \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

2. **Review cache hit rate:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name CacheHitRate \
  --dimensions Name=CacheClusterId,Value=storefront-dev-valkey \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

3. **Analyze key patterns** (from application):
```javascript
// Get all keys (use with caution in production)
const keys = await client.keys('*');
console.log(`Total keys: ${keys.length}`);

// Better: Use SCAN for large datasets
for await (const key of client.scanIterator()) {
  console.log(key);
}
```

4. **Check for large keys:**
```javascript
// Get memory usage of a key
const memory = await client.memoryUsage('key-name');
console.log(`Key uses ${memory} bytes`);
```

### Cost Optimization

**Symptom**: Higher than expected costs

1. **Review actual vs. max limits:**
```bash
# Check storage usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name BytesUsedForCache \
  --dimensions Name=CacheClusterId,Value=storefront-dev-valkey \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Maximum
```

2. **Set appropriate TTLs on all keys:**
```javascript
// Always set expiration
await client.setEx('key', 3600, 'value'); // 1 hour

// Or set TTL on existing key
await client.expire('key', 3600);
```

3. **Monitor and clean up unused keys:**
```javascript
// Find keys without TTL
for await (const key of client.scanIterator()) {
  const ttl = await client.ttl(key);
  if (ttl === -1) {
    console.log(`Key ${key} has no expiration`);
  }
}
```

4. **Adjust limits based on actual usage:**
```python
# In redis_stack.py, reduce limits if usage is consistently low
if environment == "dev":
    max_storage = 1  # Reduce from 2 GB if usage < 500 MB
    max_ecpu = 2000  # Reduce from 3000 if usage < 1000 ECPU
```

5. **Use connection pooling** - Reduces ECPU overhead
6. **Compress large values** - Reduces storage costs
7. **Use efficient data structures** - Hashes instead of multiple keys

## Deployment

### Deploy Valkey Stack

```bash
# Deploy to specific environment
cdk deploy RedisStack-dev --context env=dev

# Deploy to all environments
cdk deploy --all --context deploy-all=true
```

### Update Configuration

Edit `/stacks/redis_stack.py`:

```python
env_config = {
    "dev": {
        "redis_max_storage_gb": 1,
        "redis_max_ecpu": 3000,
    },
    "staging": {
        "redis_max_storage_gb": 2,
        "redis_max_ecpu": 5000,
    },
    "prod": {
        "redis_max_storage_gb": 5,
        "redis_max_ecpu": 10000,
    },
}
```

Then redeploy:

```bash
cdk deploy RedisStack-prod --context env=prod
```

### Verify Deployment

```bash
# Check cache status
aws elasticache describe-serverless-caches \
  --serverless-cache-name storefront-dev-valkey

# Test connection from application
aws logs tail APIServiceStack-dev-apiserviceapiserviceLogGroup --since 5m | grep -i valkey
```

## Best Practices

1. **Use connection pooling** - Reuse connections across requests
2. **Set appropriate TTLs** - Prevent memory bloat
3. **Use key prefixes** - Organize keys by type (e.g., `session:`, `cache:`)
4. **Monitor metrics** - Track usage and performance
5. **Handle connection failures** - Implement retry logic
6. **Use pipelining** - Batch multiple commands for efficiency
7. **Avoid large keys** - Keep values under 1 MB
8. **Use Redis data structures** - Leverage hashes, sets, sorted sets

## Migration from Other Redis Solutions

### From Redis on Fargate

1. **Export data** from existing Redis using `SAVE` or `BGSAVE`
2. **Deploy ElastiCache Serverless (Valkey)**
3. **Import data** using `redis-cli` with RDB file
4. **Update application configuration** to use new endpoint
5. **Test thoroughly** - Valkey is Redis-compatible but verify all operations
6. **Remove old Fargate Redis task**

### From ElastiCache Cluster Mode

1. **Create snapshot** of existing cluster
2. **Deploy ElastiCache Serverless**
3. **Restore snapshot** (if compatible - check Valkey version)
4. **Update application endpoints** in SSM Parameter Store
5. **Monitor performance** - Serverless has different scaling characteristics
6. **Delete old cluster** after validation

### From Redis Cloud / Other Providers

1. **Use redis-cli with --rdb flag** to export data
2. **Deploy ElastiCache Serverless**
3. **Import using redis-cli** connected to Valkey endpoint
4. **Update DNS/endpoints** in application
5. **Validate data integrity**
6. **Decommission old service**

## Valkey vs Redis OSS

### Compatibility

✅ **Fully Compatible:**
- All Redis OSS commands and data types
- Redis client libraries (no code changes needed)
- Existing Redis tools (redis-cli, RedisInsight, etc.)
- Redis protocols (RESP2, RESP3)

❌ **Not Supported:**
- Redis Enterprise features (RedisJSON, RedisSearch, etc.)
- Redis Modules
- Redis Cluster mode (Serverless handles scaling automatically)
- AUTH command (use VPC security instead)

### Why Valkey?

1. **Open Source** - No licensing concerns
2. **AWS Managed** - Fully integrated with AWS services
3. **Cost Effective** - Serverless pricing model
4. **High Performance** - Optimized for AWS infrastructure
5. **Active Development** - Backed by AWS and Linux Foundation

---

For questions or issues with Redis, check CloudWatch metrics or contact the DevOps team.
