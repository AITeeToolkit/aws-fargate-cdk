# Redis Serverless Guide

## Overview

This project uses **AWS ElastiCache Serverless for Redis** to provide a cost-effective, fully-managed caching solution across all environments.

## Architecture

```
Application (ECS Fargate)
    ↓
Redis Serverless (ElastiCache)
    ↓
VPC Private Subnets
```

## Cost Structure

| Environment | Max Storage | Max ECPU | Estimated Monthly Cost |
|-------------|-------------|----------|------------------------|
| **dev**     | 1 GB        | 3,000    | ~$0.10 - $0.50        |
| **staging** | 2 GB        | 5,000    | ~$0.50 - $2.00        |
| **prod**    | 5 GB        | 10,000   | ~$2.00 - $10.00       |

**Total estimated cost:** $3-13/month for all environments

### Pricing Breakdown
- **Storage:** $0.125/GB-month
- **Compute:** $0.0034 per million ECPUs
- **Data transfer:** Within VPC is free

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

The Redis endpoint is stored in SSM Parameter Store:

```bash
# Get Redis endpoint
aws ssm get-parameter \
  --name "/storefront/dev/redis/endpoint" \
  --query "Parameter.Value" \
  --output text

# Get Redis port
aws ssm get-parameter \
  --name "/storefront/dev/redis/port" \
  --query "Parameter.Value" \
  --output text
```

### Environment Variables

Set these in your ECS task definitions:

```bash
REDIS_HOST=/storefront/${ENVIRONMENT}/redis/endpoint
REDIS_PORT=/storefront/${ENVIRONMENT}/redis/port
```

## Application Integration

### Node.js (API/Web)

```javascript
const redis = require('redis');
const { SSMClient, GetParameterCommand } = require('@aws-sdk/client-ssm');

// Get Redis config from SSM
const ssm = new SSMClient({ region: 'us-east-1' });
const environment = process.env.ENVIRONMENT || 'dev';

async function getRedisConfig() {
  const [hostParam, portParam] = await Promise.all([
    ssm.send(new GetParameterCommand({
      Name: `/storefront/${environment}/redis/endpoint`
    })),
    ssm.send(new GetParameterCommand({
      Name: `/storefront/${environment}/redis/port`
    }))
  ]);
  
  return {
    host: hostParam.Parameter.Value,
    port: parseInt(portParam.Parameter.Value)
  };
}

// Create Redis client
async function createRedisClient() {
  const config = await getRedisConfig();
  
  const client = redis.createClient({
    socket: {
      host: config.host,
      port: config.port
    }
  });
  
  await client.connect();
  return client;
}

// Usage
const redisClient = await createRedisClient();
await redisClient.set('key', 'value');
const value = await redisClient.get('key');
```

### Python (Listener/DNS Worker)

```python
import boto3
import redis
import os

def get_redis_config():
    """Get Redis configuration from SSM Parameter Store"""
    ssm = boto3.client('ssm', region_name='us-east-1')
    environment = os.getenv('ENVIRONMENT', 'dev')
    
    host = ssm.get_parameter(
        Name=f'/storefront/{environment}/redis/endpoint'
    )['Parameter']['Value']
    
    port = ssm.get_parameter(
        Name=f'/storefront/{environment}/redis/port'
    )['Parameter']['Value']
    
    return host, int(port)

def create_redis_client():
    """Create Redis client"""
    host, port = get_redis_config()
    
    client = redis.Redis(
        host=host,
        port=port,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    
    return client

# Usage
redis_client = create_redis_client()
redis_client.set('key', 'value')
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

- Redis runs in **private subnets** only
- Security group allows traffic only from VPC CIDR
- No public internet access

### IAM Permissions

ECS tasks need SSM read permissions:

```json
{
  "Effect": "Allow",
  "Action": [
    "ssm:GetParameter",
    "ssm:GetParameters"
  ],
  "Resource": [
    "arn:aws:ssm:us-east-1:*:parameter/storefront/*/redis/*"
  ]
}
```

## Monitoring

### CloudWatch Metrics

Key metrics to monitor:

- **BytesUsedForCache** - Memory usage
- **CurrConnections** - Active connections
- **CacheHits** - Successful cache retrievals
- **CacheMisses** - Cache misses
- **NetworkBytesIn/Out** - Network traffic

### Alarms

Recommended CloudWatch alarms:

```bash
# High memory usage
aws cloudwatch put-metric-alarm \
  --alarm-name "redis-high-memory-${ENVIRONMENT}" \
  --metric-name BytesUsedForCache \
  --threshold 4000000000 \  # 4 GB
  --comparison-operator GreaterThanThreshold

# High connection count
aws cloudwatch put-metric-alarm \
  --alarm-name "redis-high-connections-${ENVIRONMENT}" \
  --metric-name CurrConnections \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold
```

## Troubleshooting

### Connection Issues

1. **Check security group rules:**
```bash
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=*Redis*"
```

2. **Verify endpoint is accessible from ECS task:**
```bash
# From ECS task
nc -zv <redis-endpoint> 6379
```

3. **Check SSM parameters:**
```bash
aws ssm get-parameters-by-path \
  --path "/storefront/dev/redis/"
```

### Performance Issues

1. **Check ECPU usage** - May need to increase max_ecpu
2. **Review cache hit rate** - Low hit rate = inefficient caching
3. **Analyze key patterns** - Use `SCAN` to identify large keys

### Cost Optimization

1. **Set appropriate TTLs** - Expire unused keys
2. **Monitor storage usage** - Delete unnecessary keys
3. **Review ECPU limits** - Adjust based on actual usage
4. **Use connection pooling** - Reduce connection overhead

## Deployment

### Deploy Redis Stack

```bash
# Deploy to specific environment
cdk deploy RedisStack-dev --context env=dev

# Deploy to all environments
cdk deploy --all --context deploy-all=true
```

### Update Limits

Edit `stacks/redis_stack.py`:

```python
if environment == "prod":
    max_storage = 10  # Increase to 10 GB
    max_ecpu = 20000  # Increase compute
```

Then redeploy:

```bash
cdk deploy RedisStack-prod --context env=prod
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

1. Export data from existing Redis
2. Deploy ElastiCache Serverless
3. Import data to new Redis
4. Update application configuration
5. Remove old Fargate Redis task

### From ElastiCache Cluster

1. Create snapshot of existing cluster
2. Deploy ElastiCache Serverless
3. Restore snapshot (if compatible)
4. Update application endpoints
5. Delete old cluster

---

For questions or issues with Redis, check CloudWatch metrics or contact the DevOps team.
