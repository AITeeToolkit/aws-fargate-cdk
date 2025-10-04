# SNS Domain Changes Integration

## Architecture (Simplified - No Listener Service)

```
External Application (Jake's API)
    ↓
Publishes to SNS Topic (domain-changes.fifo)
    ↓
SQS Queue (dns-operations.fifo) - subscribed
    ↓
DNS Worker
    ├─ Updates domains table
    ├─ Creates Route53 hosted zone
    └─ Triggers GitHub workflow
```

## Required SNS Message Format

**All fields are required except `hosted_zone_id`:**

```json
{
  "full_url": "example.com",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "active_status": "Y",
  "hosted_zone_id": 123
}
```

### Test Message
```bash
aws sns publish --topic-arn arn:aws:sns:us-east-1:156041439702:storefront-staging-domain-changes.fifo \
  --message file://test-deactivation-message.json \
  --message-group-id "domain-changes" \
  --message-deduplication-id "040992-xyz-deactivate-$(date +%s)"
```

### Field Descriptions:

- **`full_url`** (string, required): The domain name
- **`tenant_id`** (string, required): UUID of the tenant who owns the domain
- **`active_status`** (string, required): `"Y"` for activation, `"N"` for deactivation
- **`hosted_zone_id`** (integer, optional): AWS hosted zone ID if already created

## Publishing Domain Changes

### From Python Application

```python
import boto3
import json
import time

sns = boto3.client('sns')

# Get topic ARN from SSM Parameter Store
ssm = boto3.client('ssm')
topic_arn = ssm.get_parameter(
    Name='/storefront-dev/sns/domain-changes-topic-arn'
)['Parameter']['Value']

# Publish domain activation
sns.publish(
    TopicArn=topic_arn,
    Message=json.dumps({
        'full_url': 'example.com',
        'tenant_id': '550e8400-e29b-41d4-a716-446655440000',
        'active_status': 'Y'
    }),
    MessageGroupId='domain-changes',  # Required for FIFO
    MessageDeduplicationId=f'example.com-{int(time.time())}'  # Required for FIFO
)
```

### From API Endpoint (FastAPI Example)

```python
import boto3
import json
import time
from fastapi import FastAPI, HTTPException

app = FastAPI()
sns = boto3.client('sns')
TOPIC_ARN = os.environ['DOMAIN_CHANGES_TOPIC_ARN']

@app.post("/domains/{domain_id}/activate")
async def activate_domain(domain_id: str, tenant_id: str):
    """
    Activate a domain by publishing to SNS.
    DNS worker will handle database updates and Route53 operations.
    """
    try:
        # Publish to SNS
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps({
                'full_url': domain_id,
                'tenant_id': tenant_id,
                'active_status': 'Y'
            }),
            MessageGroupId='domain-changes',
            MessageDeduplicationId=f'{domain_id}-{int(time.time())}'
        )

        return {"status": "activation_queued", "domain": domain_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/domains/{domain_id}/deactivate")
async def deactivate_domain(domain_id: str):
    """
    Deactivate a domain by publishing to SNS.
    DNS worker will handle database updates and Route53 cleanup.
    """
    try:
        # Publish to SNS
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps({
                'full_url': domain_id,
                'tenant_id': '',  # Not needed for deactivation
                'active_status': 'N'
            }),
            MessageGroupId='domain-changes',
            MessageDeduplicationId=f'{domain_id}-{int(time.time())}'
        )

        return {"status": "deactivation_queued", "domain": domain_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Message Validation

DNS Worker validates all incoming messages:

- **Missing required fields** → Message deleted, error logged (no retry)
- **Invalid `active_status`** → Message deleted, error logged (no retry)
- **Invalid JSON** → Message deleted, error logged (no retry)
- **Processing errors** → Message retried (transient errors)

## Benefits

✅ **No Listener Service** - Removed entirely, one less service to maintain
✅ **External Control** - Your application controls domain activation
✅ **Fan-out Ready** - Easy to add more SNS subscribers (analytics, webhooks)
✅ **Decoupled** - Application doesn't know about DNS worker internals
✅ **Reliable** - SNS → SQS guarantees delivery with retry logic
✅ **Simple** - Just publish to SNS, DNS worker handles everything else

## Environment Variables

### For External Application (Publisher):
- `DOMAIN_CHANGES_TOPIC_ARN` - SNS topic ARN for publishing

### Read from SSM Parameter Store:
- `/storefront-{env}/sns/domain-changes-topic-arn`

## SNS Topic Details

- **Name**: `storefront-{env}-domain-changes.fifo`
- **Type**: FIFO (First-In-First-Out)
- **Deduplication**: Explicit (you provide MessageDeduplicationId)
- **Ordering**: By MessageGroupId

## What DNS Worker Does

1. **Receives SNS message** from SQS queue
2. **Validates** required fields
3. **Updates domains table** with provided data
4. **Creates/deletes Route53 hosted zone**
5. **Triggers GitHub workflow** via repository_dispatch
6. **Garbage collects** certificate stacks for drained domains
