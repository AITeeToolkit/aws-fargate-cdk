# Simplified Architecture - No Listener Service

## Overview

Removed the listener service entirely. External systems (Jake's API) publish domain changes directly to SNS, which fans out to the DNS worker via SQS.

## Architecture Flow

```
External Application (Jake's API)
    ↓
Publishes to SNS Topic
    ↓
SNS Topic (storefront-{env}-domain-changes.fifo)
    ↓
SQS Queue (storefront-{env}-dns-operations-queue.fifo) - subscribed
    ↓
DNS Worker
    ├─ Validates SNS message
    ├─ Updates domains table
    ├─ Creates/deletes Route53 hosted zone
    ├─ Triggers GitHub workflow (repository_dispatch)
    └─ Garbage collects certificate stacks
```

## Components

### Removed
- ❌ **Listener Service** - No longer needed
- ❌ **Database triggers** - Not needed
- ❌ **Listener ECR repository** - Removed from infrastructure

### Kept
- ✅ **SNS Topic** - Entry point for domain changes
- ✅ **SQS Queue** - Subscribed to SNS, provides batching/retry
- ✅ **DNS Worker** - Handles everything atomically

## What Changed

### Before (With Listener)
```
Database Trigger → Listener Service → SQS → DNS Worker
```
- Listener listened to database notifications
- Listener published to SQS
- DNS worker processed messages

### After (No Listener)
```
External API → SNS → SQS → DNS Worker
```
- External system publishes to SNS directly
- SNS fans out to SQS queue
- DNS worker processes messages (same as before)

## Benefits

1. **Simpler** - One less service to maintain
2. **External Control** - Your application controls domain activation
3. **Decoupled** - Application doesn't need database triggers
4. **Fan-out Ready** - Easy to add more SNS subscribers
5. **Cost Savings** - No ECS task running 24/7 for listener

## SNS Message Format

External systems must publish messages in this format:

```json
{
  "full_url": "example.com",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "active_status": "Y",
  "hosted_zone_id": 123
}
```

**Required fields:**
- `full_url` - Domain name
- `tenant_id` - UUID of tenant
- `active_status` - "Y" or "N"

**Optional fields:**
- `hosted_zone_id` - AWS hosted zone ID (if already created)

## DNS Worker Responsibilities

The DNS worker now handles everything:

1. **Message Validation** - Validates required fields
2. **Database Operations** - Updates domains table with provided data
3. **Route53 Operations** - Creates/deletes hosted zones
4. **GitHub Workflow** - Triggers infrastructure deployment
5. **Garbage Collection** - Deletes certificate stacks for drained domains

## Migration Notes

### Infrastructure Changes
- Removed `ListenerServiceStack` from `app.py`
- Removed `listener` from ECR repositories
- Removed `listener_tag` resolution
- Added SNS topic to `SQSStack`
- SQS queue subscribes to SNS topic

### Code Changes
- DNS worker now validates SNS message format
- DNS worker uses provided `tenant_id` (no database lookup)
- DNS worker stores domain info in `domain_info_map`
- `update_domain_activation()` uses SNS message data

### External System Requirements
- Must publish to SNS topic with correct format
- Must provide `tenant_id` in message
- Must use FIFO message attributes (MessageGroupId, MessageDeduplicationId)

## Deployment

1. Deploy infrastructure with SNS topic
2. Update external application to publish to SNS
3. Remove listener service deployment
4. Test domain activation/deactivation flow

## See Also

- [SNS Domain Changes Integration](./SNS_DOMAIN_CHANGES.md) - Detailed SNS message format and examples
