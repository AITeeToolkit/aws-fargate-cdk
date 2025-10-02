# OpenSearch Connectivity Guide

This guide explains how services connect to AWS OpenSearch in the Fargate infrastructure.

## Architecture Overview

The infrastructure uses **AWS OpenSearch Service** with **public access** (not VPC-based) and **IAM authentication** via SigV4 signing.

### Key Components

1. **OpenSearch Domain**: Public endpoint with IAM-based access control
2. **IAM Roles**: Fargate task roles with OpenSearch permissions
3. **SSM Parameters**: Store OpenSearch endpoint URLs
4. **SigV4 Authentication**: AWS request signing for secure access

### Security Model

**Important**: The OpenSearch endpoint is **publicly resolvable** but **NOT open to the internet**.

- ✅ **DNS is public** - The hostname can be resolved from anywhere
- ❌ **Access is restricted** - Only specific IAM principals can make requests
- ✅ **SigV4 signing required** - Every request must be signed with valid AWS credentials
- ✅ **IAM policy enforcement** - Only allowed IAM roles/users can access

**Who can access:**
- Fargate tasks with the OpenSearch IAM role
- AWS users/roles explicitly added to the access policy
- Third-party applications with valid AWS credentials and proper IAM permissions

**Who cannot access:**
- Random internet users (no credentials)
- AWS accounts not in the access policy
- AWS users without the required IAM permissions

---

## OpenSearch Stack Configuration

### Domain Setup

The OpenSearch domain is created with:
- **Public access** (no VPC attachment)
- **IAM-based authentication** (no master user/password)
- **Fine-grained access control disabled**
- **Encryption at rest and in transit**

**File**: `/stacks/opensearch_stack.py`

```python
domain = opensearch.Domain(
    self, "OpenSearchDomain",
    version=opensearch.EngineVersion.OPENSEARCH_3_11,
    capacity=opensearch.CapacityConfig(
        data_node_instance_type="t3.small.search",
        data_nodes=1,
    ),
    ebs=opensearch.EbsOptions(
        volume_size=10,
        volume_type=ec2.EbsDeviceVolumeType.GP3,
    ),
    enforce_https=True,
    node_to_node_encryption=True,
    encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
)
```

### IAM Access Policy

The domain allows access from specific IAM roles:

```python
domain.add_access_policies(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        principals=[iam.ArnPrincipal(self.fargate_opensearch_role.role_arn)],
        actions=["es:*"],
        resources=[f"{domain.domain_arn}/*"],
    )
)
```

### SSM Parameter Storage

The OpenSearch endpoint is stored in SSM Parameter Store for each environment:

```python
ssm.StringParameter(
    self, "OpenSearchEndpoint",
    parameter_name=f"/storefront-{environment}/opensearch/endpoint",
    string_value=f"https://{domain.domain_endpoint}",
)
```

**Parameter Path**: `/storefront-{env}/opensearch/endpoint`
- Dev: `/storefront-dev/opensearch/endpoint`
- Staging: `/storefront-staging/opensearch/endpoint`
- Prod: `/storefront-prod/opensearch/endpoint`

---

## Service Integration

### API Service

The API service connects to OpenSearch for search and indexing operations.

**File**: `/stacks/api_service_stack.py`

#### Environment Variables

```python
environment={
    "OPENSEARCH_ENDPOINT": ssm.StringParameter.value_from_lookup(
        self,
        parameter_name=f"/storefront-{environment}/opensearch/endpoint",
    ),
}
```

#### IAM Permissions

The API service task role receives the OpenSearch role:

```python
api_service = APIServiceStack(
    app,
    f"APIServiceStack-{current_env}",
    opensearch_role=opensearch_stack.fargate_opensearch_role,
    # ... other params
)
```

This grants the following permissions:
- `es:ESHttpGet`
- `es:ESHttpPost`
- `es:ESHttpPut`
- `es:ESHttpDelete`
- `es:ESHttpHead`

### Web Service

The web service also has OpenSearch access for search functionality.

**File**: `/stacks/web_service_stack.py`

Same configuration as API service:
- Environment variable: `OPENSEARCH_ENDPOINT`
- IAM role: `opensearch_role` parameter
- Full ES HTTP permissions

---

## Application Code Integration

### Node.js/TypeScript (API Service)

**Installation**:
```bash
npm install @opensearch-project/opensearch @aws-sdk/credential-providers aws4
```

**Connection Example**:

```typescript
import { Client } from '@opensearch-project/opensearch';
import { defaultProvider } from '@aws-sdk/credential-providers';
import { AwsSigv4Signer } from '@opensearch-project/opensearch/aws';

const client = new Client({
  ...AwsSigv4Signer({
    region: 'us-east-1',
    service: 'es',
    getCredentials: () => defaultProvider()(),
  }),
  node: process.env.OPENSEARCH_ENDPOINT,
});

// Use the client
const response = await client.search({
  index: 'products',
  body: {
    query: {
      match: { name: 'shirt' }
    }
  }
});
```

### Python (If needed)

**Installation**:
```bash
pip install opensearch-py boto3 requests-aws4auth
```

**Connection Example**:

```python
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    'us-east-1',
    'es',
    session_token=credentials.token
)

client = OpenSearch(
    hosts=[{'host': os.environ['OPENSEARCH_ENDPOINT'].replace('https://', ''), 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Use the client
response = client.search(
    index='products',
    body={'query': {'match_all': {}}}
)
```

---

## Third-Party Application Access

To allow external applications (e.g., OpenSearch Dashboards, Kibana, custom tools) to access OpenSearch:

### Option 1: IAM User Credentials (Recommended for Tools)

**1. Create an IAM User**

```bash
aws iam create-user --user-name opensearch-client

# Create access keys
aws iam create-access-key --user-name opensearch-client
```

**2. Update OpenSearch Access Policy**

Add the IAM user to the domain access policy in `/stacks/opensearch_stack.py`:

```python
# Add after the Fargate role policy
domain.add_access_policies(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        principals=[
            iam.ArnPrincipal(self.fargate_opensearch_role.role_arn),
            iam.ArnPrincipal("arn:aws:iam::156041439702:user/opensearch-client"),  # Add this
        ],
        actions=["es:*"],
        resources=[f"{domain.domain_arn}/*"],
    )
)
```

**3. Deploy the Updated Stack**

```bash
cdk deploy OpenSearchStack-dev --context env=dev
```

**4. Configure Third-Party Application**

Use the IAM user credentials with SigV4 signing:

**OpenSearch Dashboards Example:**
```yaml
# opensearch_dashboards.yml
opensearch.hosts: ["https://opensearch-dev-xyz.us-east-1.es.amazonaws.com"]
opensearch.ssl.verificationMode: full
opensearch.requestHeadersWhitelist: ["authorization", "x-amz-date", "x-amz-security-token"]

# AWS SigV4 authentication
opensearch.aws:
  enabled: true
  region: us-east-1
  credentials:
    accessKeyId: "AKIA..."
    secretAccessKey: "..."
```

**Postman Example:**
1. Set request URL: `https://opensearch-dev-xyz.us-east-1.es.amazonaws.com/_search`
2. Authorization → AWS Signature
3. Access Key: `AKIA...`
4. Secret Key: `...`
5. AWS Region: `us-east-1`
6. Service Name: `es`

**cURL with aws-sigv4 Example:**
```bash
# Install awscurl
pip install awscurl

# Make request
awscurl --service es \
  --region us-east-1 \
  https://opensearch-dev-xyz.us-east-1.es.amazonaws.com/_search \
  -H "Content-Type: application/json" \
  -d '{"query": {"match_all": {}}}'
```

### Option 2: IAM Role with AssumeRole (Recommended for Applications)

**1. Create an IAM Role**

```bash
# Create trust policy
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::156041439702:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name opensearch-external-access \
  --assume-role-policy-document file://trust-policy.json
```

**2. Update OpenSearch Access Policy**

```python
domain.add_access_policies(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        principals=[
            iam.ArnPrincipal(self.fargate_opensearch_role.role_arn),
            iam.ArnPrincipal("arn:aws:iam::156041439702:role/opensearch-external-access"),
        ],
        actions=["es:*"],
        resources=[f"{domain.domain_arn}/*"],
    )
)
```

**3. Application Code (Assume Role)**

```python
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Assume the role
sts = boto3.client('sts')
assumed_role = sts.assume_role(
    RoleArn='arn:aws:iam::156041439702:role/opensearch-external-access',
    RoleSessionName='opensearch-session'
)

credentials = assumed_role['Credentials']
awsauth = AWS4Auth(
    credentials['AccessKeyId'],
    credentials['SecretAccessKey'],
    'us-east-1',
    'es',
    session_token=credentials['SessionToken']
)

client = OpenSearch(
    hosts=[{'host': 'opensearch-dev-xyz.us-east-1.es.amazonaws.com', 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
```

### Option 3: Temporary Credentials (For Testing)

**1. Use AWS CLI Credentials**

If you have AWS CLI configured with appropriate permissions:

```bash
# Get OpenSearch endpoint
ENDPOINT=$(aws ssm get-parameter \
  --name /storefront-dev/opensearch/endpoint \
  --query 'Parameter.Value' \
  --output text)

# Make request using your AWS CLI credentials
awscurl --service es \
  --region us-east-1 \
  $ENDPOINT/_search \
  -H "Content-Type: application/json" \
  -d '{"query": {"match_all": {}}}'
```

**2. Add Your AWS User to Access Policy**

Temporarily add your IAM user for testing:

```python
domain.add_access_policies(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        principals=[
            iam.ArnPrincipal(self.fargate_opensearch_role.role_arn),
            iam.ArnPrincipal("arn:aws:iam::156041439702:user/your-username"),  # Testing only
        ],
        actions=["es:*"],
        resources=[f"{domain.domain_arn}/*"],
    )
)
```

### Security Best Practices for Third-Party Access

1. **Use IAM Roles over Users** - Roles have temporary credentials
2. **Principle of Least Privilege** - Grant only required permissions (e.g., `es:ESHttpGet` for read-only)
3. **Rotate Credentials** - Regularly rotate IAM user access keys
4. **Use MFA** - Enable MFA for IAM users accessing production data
5. **Audit Access** - Monitor CloudWatch logs for unauthorized access attempts
6. **IP Restrictions** - Consider adding IP-based conditions to IAM policies:

```python
domain.add_access_policies(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        principals=[iam.ArnPrincipal("arn:aws:iam::156041439702:user/opensearch-client")],
        actions=["es:*"],
        resources=[f"{domain.domain_arn}/*"],
        conditions={
            "IpAddress": {
                "aws:SourceIp": ["203.0.113.0/24"]  # Your office IP range
            }
        }
    )
)
```

### Common Third-Party Tools

**OpenSearch Dashboards (Self-Hosted)**:
- Install OpenSearch Dashboards locally
- Configure with IAM user credentials
- Access via `http://localhost:5601`

**Grafana**:
- Use OpenSearch data source plugin
- Configure with AWS SigV4 authentication
- Create dashboards and alerts

**Logstash**:
- Use OpenSearch output plugin
- Configure with IAM credentials for ingestion

**Elasticsearch Clients**:
- Most Elasticsearch clients work with OpenSearch
- Ensure SigV4 signing is enabled
- Use OpenSearch-specific clients when possible

---

## Troubleshooting

### Common Issues

#### 1. Access Denied Errors

**Error**: `User: arn:aws:sts::xxx:assumed-role/xxx is not authorized to perform: es:ESHttpGet`

**Solution**: Verify the task role has the OpenSearch role attached:
```bash
aws iam list-attached-role-policies --role-name <task-role-name>
```

Check the OpenSearch domain access policy:
```bash
aws opensearch describe-domain --domain-name <domain-name> --query 'DomainStatus.AccessPolicies'
```

#### 2. Connection Timeout

**Error**: `Connection timeout` or `ECONNREFUSED`

**Causes**:
- OpenSearch domain not fully deployed
- Incorrect endpoint URL
- Network connectivity issues

**Solution**:
```bash
# Check domain status
aws opensearch describe-domain --domain-name opensearch-dev --query 'DomainStatus.Processing'

# Verify endpoint
aws ssm get-parameter --name /storefront-dev/opensearch/endpoint --query 'Parameter.Value'

# Test connectivity from ECS task
aws ecs execute-command --cluster storefront-cluster \
  --task <task-id> \
  --container api-service \
  --interactive \
  --command "curl -I $OPENSEARCH_ENDPOINT"
```

#### 3. Invalid Signature

**Error**: `The request signature we calculated does not match the signature you provided`

**Causes**:
- Incorrect AWS credentials
- Clock skew between client and AWS
- Wrong region in SigV4 signer

**Solution**:
- Verify task role credentials are being used
- Check system time: `date`
- Ensure region matches OpenSearch domain region

#### 4. Index Not Found

**Error**: `index_not_found_exception`

**Solution**: Create the index first:
```typescript
await client.indices.create({
  index: 'products',
  body: {
    mappings: {
      properties: {
        name: { type: 'text' },
        price: { type: 'float' },
        description: { type: 'text' }
      }
    }
  }
});
```

---

## Monitoring & Logging

### CloudWatch Logs

OpenSearch logs are available in CloudWatch:
- **Application logs**: `/aws/opensearch/domains/<domain-name>/application-logs`
- **Slow logs**: `/aws/opensearch/domains/<domain-name>/slow-logs`
- **Error logs**: `/aws/opensearch/domains/<domain-name>/error-logs`

### Metrics

Key metrics to monitor:
- **ClusterStatus.green**: Domain health
- **SearchRate**: Search requests per minute
- **IndexingRate**: Indexing operations per minute
- **CPUUtilization**: Node CPU usage
- **FreeStorageSpace**: Available disk space

### Alarms

Set up CloudWatch alarms for:
```bash
# Cluster status not green
aws cloudwatch put-metric-alarm \
  --alarm-name opensearch-cluster-red \
  --metric-name ClusterStatus.red \
  --namespace AWS/ES \
  --statistic Maximum \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold

# Low disk space
aws cloudwatch put-metric-alarm \
  --alarm-name opensearch-low-disk \
  --metric-name FreeStorageSpace \
  --namespace AWS/ES \
  --statistic Minimum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 2000 \
  --comparison-operator LessThanThreshold
```

---

## Best Practices

### 1. Connection Pooling

Reuse OpenSearch client instances:

```typescript
// ❌ Bad: Creating new client for each request
export async function searchProducts(query: string) {
  const client = new Client({ /* config */ });
  return await client.search({ /* ... */ });
}

// ✅ Good: Reuse client instance
const client = new Client({ /* config */ });

export async function searchProducts(query: string) {
  return await client.search({ /* ... */ });
}
```

### 2. Error Handling

Always handle OpenSearch errors gracefully:

```typescript
try {
  const response = await client.search({ /* ... */ });
  return response.body.hits.hits;
} catch (error) {
  if (error.meta?.statusCode === 404) {
    console.log('Index not found, creating...');
    await createIndex();
  } else {
    console.error('OpenSearch error:', error);
    throw new Error('Search service unavailable');
  }
}
```

### 3. Bulk Operations

Use bulk API for multiple operations:

```typescript
const body = products.flatMap(doc => [
  { index: { _index: 'products', _id: doc.id } },
  doc
]);

await client.bulk({ body });
```

### 4. Index Management

- Use index templates for consistent mappings
- Implement index rotation for time-series data
- Set up index lifecycle policies for automatic cleanup

### 5. Security

- Never expose OpenSearch endpoint publicly
- Use IAM roles, not access keys
- Enable audit logging for compliance
- Regularly review access policies

---

## Migration from Kubernetes Elasticsearch

If migrating from K8s Elasticsearch to AWS OpenSearch:

### 1. Export Data

```bash
# From K8s Elasticsearch
kubectl port-forward svc/elasticsearch-master 9200:9200
python scripts/direct_migration.py
```

### 2. Import to OpenSearch

The migration script handles:
- Bulk export from source
- Index creation in OpenSearch
- Bulk import with proper authentication
- Error handling and retry logic

**Script**: `/scripts/direct_migration.py`

### 3. Update Application Configuration

Change environment variables:
- Old: `ELASTICSEARCH_URL=http://elasticsearch-master:9200`
- New: `OPENSEARCH_ENDPOINT=https://xxx.us-east-1.es.amazonaws.com`

Update client initialization to use SigV4 authentication.

---

## Additional Resources

- [AWS OpenSearch Service Documentation](https://docs.aws.amazon.com/opensearch-service/)
- [OpenSearch Client for JavaScript](https://github.com/opensearch-project/opensearch-js)
- [Fine-grained Access Control](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html)
- [Best Practices for Amazon OpenSearch Service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp.html)

---

## Support

For issues or questions:
1. Check CloudWatch logs for error details
2. Verify IAM permissions and access policies
3. Test connectivity from ECS tasks
4. Review OpenSearch domain health metrics
5. Consult the troubleshooting section above
