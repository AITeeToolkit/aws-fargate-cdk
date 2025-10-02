# SQS Connectivity Guide

This guide explains how services connect to AWS SQS (Simple Queue Service) in the Fargate infrastructure.

## Architecture Overview

The infrastructure uses **AWS SQS** for asynchronous message processing between services, primarily for domain activation/deactivation workflows.

### Key Components

1. **SQS Queues**: Standard queues for message processing
2. **IAM Policies**: Managed policies for queue access
3. **SSM Parameters**: Store queue URLs for service configuration
4. **Service Integration**: Listener service (producer) and DNS worker (consumer)

---

## SQS Stack Configuration

### Queue Setup

The SQS stack creates queues for each environment with dead-letter queue (DLQ) support:

**File**: `/stacks/sqs_stack.py`

```python
# Main queue for domain operations
domain_queue = sqs.Queue(
    self, "DomainQueue",
    queue_name=f"domain-operations-{environment}",
    visibility_timeout=Duration.seconds(300),  # 5 minutes
    retention_period=Duration.days(14),
    dead_letter_queue=sqs.DeadLetterQueue(
        max_receive_count=3,
        queue=dlq
    )
)

# Dead letter queue for failed messages
dlq = sqs.Queue(
    self, "DomainQueueDLQ",
    queue_name=f"domain-operations-{environment}-dlq",
    retention_period=Duration.days(14)
)
```

### Queue Configuration

**Key Settings:**
- **Visibility Timeout**: 300 seconds (5 minutes) - Time a message is hidden after being received
- **Message Retention**: 14 days - How long messages are kept
- **Max Receive Count**: 3 - Messages moved to DLQ after 3 failed processing attempts
- **Queue Type**: Standard (at-least-once delivery, best-effort ordering)

### IAM Managed Policy

The stack creates a managed policy for queue access:

```python
sqs_policy = iam.ManagedPolicy(
    self, "SQSManagedPolicy",
    managed_policy_name=f"SQS-{environment}-Policy",
    statements=[
        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:GetQueueUrl",
            ],
            resources=[
                domain_queue.queue_arn,
                dlq.queue_arn,
            ],
        )
    ],
)
```

### SSM Parameter Storage

Queue URLs are stored in SSM Parameter Store:

```python
ssm.StringParameter(
    self, "DomainQueueUrl",
    parameter_name=f"/storefront-{environment}/sqs/domain-queue-url",
    string_value=domain_queue.queue_url,
)
```

**Parameter Paths:**
- Main Queue: `/storefront-{env}/sqs/domain-queue-url`
- DLQ: `/storefront-{env}/sqs/domain-queue-dlq-url`

---

## Service Integration

### Listener Service (Producer)

The listener service sends messages to SQS when domain changes occur.

**File**: `/stacks/listener_service_stack.py`

#### Environment Variables

```python
listener_environment = {
    "DOMAIN_QUEUE_URL": ssm.StringParameter.value_from_lookup(
        self,
        parameter_name=f"/storefront-{environment}/sqs/domain-queue-url",
    ),
}
```

#### IAM Permissions

```python
listener_service = ListenerServiceStack(
    app,
    f"ListenerServiceStack-{current_env}",
    sqs_managed_policy=sqs_stack.sqs_managed_policy,  # Attach SQS policy
    # ... other params
)
```

The managed policy is attached to the task role, granting:
- `sqs:SendMessage` - Send messages to queue
- `sqs:GetQueueUrl` - Retrieve queue URL
- `sqs:GetQueueAttributes` - Get queue metadata

### DNS Worker Service (Consumer)

The DNS worker service receives and processes messages from SQS.

**File**: `/stacks/dns_worker_service_stack.py`

#### Environment Variables

```python
dns_worker_environment = {
    "DOMAIN_QUEUE_URL": ssm.StringParameter.value_from_lookup(
        self,
        parameter_name=f"/storefront-{environment}/sqs/domain-queue-url",
    ),
}
```

#### IAM Permissions

```python
dns_worker_service = DNSWorkerServiceStack(
    app,
    f"DNSWorkerServiceStack-{current_env}",
    sqs_managed_policy=sqs_stack.sqs_managed_policy,  # Attach SQS policy
    # ... other params
)
```

The managed policy grants:
- `sqs:ReceiveMessage` - Poll for messages
- `sqs:DeleteMessage` - Remove processed messages
- `sqs:GetQueueAttributes` - Monitor queue depth

---

## Application Code Integration

### Python (Listener Service - Producer)

**Installation**:
```bash
pip install boto3
```

**Sending Messages**:

```python
import boto3
import json
import os

# Initialize SQS client
sqs = boto3.client('sqs', region_name='us-east-1')
queue_url = os.environ['DOMAIN_QUEUE_URL']

# Send message
def send_domain_activation(domain: str, action: str):
    message_body = {
        'domain': domain,
        'action': action,  # 'activate' or 'deactivate'
        'timestamp': datetime.now().isoformat()
    }
    
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body),
        MessageAttributes={
            'Action': {
                'StringValue': action,
                'DataType': 'String'
            }
        }
    )
    
    print(f"Message sent: {response['MessageId']}")
    return response['MessageId']
```

**Batch Sending** (more efficient):

```python
def send_domain_batch(domains: list):
    entries = []
    for idx, domain in enumerate(domains):
        entries.append({
            'Id': str(idx),
            'MessageBody': json.dumps({
                'domain': domain['name'],
                'action': domain['action']
            })
        })
    
    response = sqs.send_message_batch(
        QueueUrl=queue_url,
        Entries=entries
    )
    
    print(f"Sent {len(response['Successful'])} messages")
    return response
```

### Python (DNS Worker - Consumer)

**Receiving and Processing Messages**:

```python
import boto3
import json
import os

sqs = boto3.client('sqs', region_name='us-east-1')
queue_url = os.environ['DOMAIN_QUEUE_URL']

def poll_and_process():
    while True:
        # Long polling (wait up to 20 seconds for messages)
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,  # Process up to 10 messages at once
            WaitTimeSeconds=20,  # Long polling
            MessageAttributeNames=['All'],
            AttributeNames=['All']
        )
        
        messages = response.get('Messages', [])
        
        if not messages:
            print("No messages, continuing to poll...")
            continue
        
        for message in messages:
            try:
                # Parse message
                body = json.loads(message['Body'])
                domain = body['domain']
                action = body['action']
                
                # Process the domain operation
                if action == 'activate':
                    activate_domain(domain)
                elif action == 'deactivate':
                    deactivate_domain(domain)
                
                # Delete message after successful processing
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                
                print(f"Processed and deleted message: {message['MessageId']}")
                
            except Exception as e:
                print(f"Error processing message: {e}")
                # Message will be retried or moved to DLQ
```

**Batch Processing**:

```python
def process_batch(messages):
    delete_entries = []
    
    for message in messages:
        try:
            body = json.loads(message['Body'])
            # Process message
            process_domain_operation(body)
            
            # Add to batch delete
            delete_entries.append({
                'Id': message['MessageId'],
                'ReceiptHandle': message['ReceiptHandle']
            })
        except Exception as e:
            print(f"Error: {e}")
    
    # Batch delete successful messages
    if delete_entries:
        sqs.delete_message_batch(
            QueueUrl=queue_url,
            Entries=delete_entries
        )
```

---

## Message Flow

### Domain Activation Flow

1. **Listener Service** receives domain activation request
2. **Listener** sends message to SQS queue:
   ```json
   {
     "domain": "example.com",
     "action": "activate",
     "tenant_id": "123",
     "timestamp": "2025-10-02T12:00:00Z"
   }
   ```
3. **DNS Worker** polls SQS queue (long polling)
4. **DNS Worker** receives message and processes:
   - Updates database (mark domain active)
   - Creates Route53 hosted zone
   - Updates domains.json
5. **DNS Worker** deletes message from queue
6. If processing fails 3 times, message moves to DLQ

### Dead Letter Queue (DLQ) Handling

Messages that fail processing 3 times are moved to the DLQ:

```python
def process_dlq():
    dlq_url = os.environ['DOMAIN_QUEUE_DLQ_URL']
    
    response = sqs.receive_message(
        QueueUrl=dlq_url,
        MaxNumberOfMessages=10
    )
    
    for message in response.get('Messages', []):
        body = json.loads(message['Body'])
        
        # Log failed message for investigation
        print(f"Failed message: {body}")
        
        # Optionally: Send alert, store in database, etc.
        alert_operations_team(body)
        
        # Delete from DLQ after logging
        sqs.delete_message(
            QueueUrl=dlq_url,
            ReceiptHandle=message['ReceiptHandle']
        )
```

---

## Third-Party Application Access

To allow external applications or services to send/receive messages from SQS queues:

### Option 1: IAM User Credentials (For External Services)

**1. Create an IAM User**

```bash
aws iam create-user --user-name sqs-external-client

# Create access keys
aws iam create-access-key --user-name sqs-external-client
```

**2. Create IAM Policy for Queue Access**

```bash
# Create policy document
cat > sqs-external-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueUrl",
        "sqs:GetQueueAttributes"
      ],
      "Resource": [
        "arn:aws:sqs:us-east-1:156041439702:domain-operations-dev",
        "arn:aws:sqs:us-east-1:156041439702:domain-operations-staging",
        "arn:aws:sqs:us-east-1:156041439702:domain-operations-prod"
      ]
    }
  ]
}
EOF

# Create and attach policy
aws iam create-policy \
  --policy-name SQSExternalAccess \
  --policy-document file://sqs-external-policy.json

aws iam attach-user-policy \
  --user-name sqs-external-client \
  --policy-arn arn:aws:iam::156041439702:policy/SQSExternalAccess
```

**3. Configure Third-Party Application**

**Python Example:**
```python
import boto3

# Use IAM user credentials
sqs = boto3.client(
    'sqs',
    region_name='us-east-1',
    aws_access_key_id='AKIA...',
    aws_secret_access_key='...'
)

# Get queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/156041439702/domain-operations-dev'

# Send message
response = sqs.send_message(
    QueueUrl=queue_url,
    MessageBody='{"domain": "example.com", "action": "activate"}'
)
```

**Node.js Example:**
```javascript
const AWS = require('aws-sdk');

AWS.config.update({
  region: 'us-east-1',
  accessKeyId: 'AKIA...',
  secretAccessKey: '...'
});

const sqs = new AWS.SQS();

const params = {
  QueueUrl: 'https://sqs.us-east-1.amazonaws.com/156041439702/domain-operations-dev',
  MessageBody: JSON.stringify({
    domain: 'example.com',
    action: 'activate'
  })
};

sqs.sendMessage(params, (err, data) => {
  if (err) console.error(err);
  else console.log('Message sent:', data.MessageId);
});
```

### Option 2: IAM Role with AssumeRole (For AWS Services)

**1. Create IAM Role**

```bash
# Create trust policy
cat > sqs-trust-policy.json <<EOF
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
  --role-name SQSExternalAccess \
  --assume-role-policy-document file://sqs-trust-policy.json

# Attach SQS policy
aws iam attach-role-policy \
  --role-name SQSExternalAccess \
  --policy-arn arn:aws:iam::156041439702:policy/SQSExternalAccess
```

**2. Application Code (Assume Role)**

```python
import boto3

# Assume the role
sts = boto3.client('sts')
assumed_role = sts.assume_role(
    RoleArn='arn:aws:iam::156041439702:role/SQSExternalAccess',
    RoleSessionName='sqs-session'
)

credentials = assumed_role['Credentials']

# Use temporary credentials
sqs = boto3.client(
    'sqs',
    region_name='us-east-1',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken']
)
```

### Option 3: Cross-Account Access

**For services in different AWS accounts:**

```bash
# Update queue policy to allow cross-account access
cat > queue-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::EXTERNAL_ACCOUNT_ID:root"
      },
      "Action": [
        "sqs:SendMessage",
        "sqs:ReceiveMessage"
      ],
      "Resource": "arn:aws:sqs:us-east-1:156041439702:domain-operations-dev"
    }
  ]
}
EOF

# Set queue policy
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/156041439702/domain-operations-dev \
  --attributes Policy=file://queue-policy.json
```

### Available Queues

**Domain Operations Queue:**
- **Queue Name**: `domain-operations-{env}`
- **Queue URL**: `https://sqs.us-east-1.amazonaws.com/156041439702/domain-operations-{env}`
- **DLQ Name**: `domain-operations-{env}-dlq`
- **DLQ URL**: `https://sqs.us-east-1.amazonaws.com/156041439702/domain-operations-{env}-dlq`
- **Purpose**: Domain activation/deactivation workflows
- **Consumers**: DNS Worker Service
- **Producers**: Listener Service
- **AWS Console**: [View Queue](https://console.aws.amazon.com/sqs/v2/home?region=us-east-1#/queues/https%3A%2F%2Fsqs.us-east-1.amazonaws.com%2F156041439702%2Fdomain-operations-{env})

**Image Processing Queue:**
- **Queue Name**: `image-processing-{env}`
- **Queue URL**: `https://sqs.us-east-1.amazonaws.com/156041439702/image-processing-{env}`
- **DLQ Name**: `image-processing-{env}-dlq`
- **DLQ URL**: `https://sqs.us-east-1.amazonaws.com/156041439702/image-processing-{env}-dlq`
- **Purpose**: Asynchronous image optimization and transformation
- **Consumers**: Image Worker Service
- **Producers**: API Service, Web Service
- **AWS Console**: [View Queue](https://console.aws.amazon.com/sqs/v2/home?region=us-east-1#/queues/https%3A%2F%2Fsqs.us-east-1.amazonaws.com%2F156041439702%2Fimage-processing-{env})

**Order Processing Queue:**
- **Queue Name**: `order-processing-{env}`
- **Queue URL**: `https://sqs.us-east-1.amazonaws.com/156041439702/order-processing-{env}`
- **DLQ Name**: `order-processing-{env}-dlq`
- **DLQ URL**: `https://sqs.us-east-1.amazonaws.com/156041439702/order-processing-{env}-dlq`
- **Purpose**: Order fulfillment and notification workflows
- **Consumers**: Order Worker Service
- **Producers**: API Service, Webhook Handler
- **AWS Console**: [View Queue](https://console.aws.amazon.com/sqs/v2/home?region=us-east-1#/queues/https%3A%2F%2Fsqs.us-east-1.amazonaws.com%2F156041439702%2Forder-processing-{env})

**Notification Queue:**
- **Queue Name**: `notification-{env}`
- **Queue URL**: `https://sqs.us-east-1.amazonaws.com/156041439702/notification-{env}`
- **DLQ Name**: `notification-{env}-dlq`
- **DLQ URL**: `https://sqs.us-east-1.amazonaws.com/156041439702/notification-{env}-dlq`
- **Purpose**: Email, SMS, and push notification delivery
- **Consumers**: Notification Worker Service
- **Producers**: API Service, Order Worker, Domain Worker
- **AWS Console**: [View Queue](https://console.aws.amazon.com/sqs/v2/home?region=us-east-1#/queues/https%3A%2F%2Fsqs.us-east-1.amazonaws.com%2F156041439702%2Fnotification-{env})

**Note**: Replace `{env}` with `dev`, `staging`, or `prod` for the specific environment.

### Retrieve Queue URLs Programmatically

**Using AWS CLI:**
```bash
# Get queue URL from SSM Parameter Store
aws ssm get-parameter \
  --name /storefront-dev/sqs/domain-queue-url \
  --query 'Parameter.Value' \
  --output text

# Or get queue URL by name
aws sqs get-queue-url \
  --queue-name domain-operations-dev \
  --query 'QueueUrl' \
  --output text
```

**Using Python:**
```python
import boto3

ssm = boto3.client('ssm', region_name='us-east-1')
sqs = boto3.client('sqs', region_name='us-east-1')

# Method 1: From SSM Parameter Store
response = ssm.get_parameter(Name='/storefront-dev/sqs/domain-queue-url')
queue_url = response['Parameter']['Value']

# Method 2: By queue name
response = sqs.get_queue_url(QueueName='domain-operations-dev')
queue_url = response['QueueUrl']
```

### Security Best Practices for Third-Party Access

1. **Use IAM Roles over Users** - Temporary credentials are more secure
2. **Principle of Least Privilege** - Grant only required permissions:
   - Read-only: `sqs:ReceiveMessage`, `sqs:GetQueueAttributes`
   - Write-only: `sqs:SendMessage`, `sqs:GetQueueUrl`
3. **Rotate Credentials** - Regularly rotate IAM user access keys
4. **Use MFA** - Enable MFA for IAM users accessing production queues
5. **Monitor Access** - Enable CloudTrail logging for SQS API calls
6. **IP Restrictions** - Add IP-based conditions to IAM policies:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:us-east-1:156041439702:domain-operations-*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["203.0.113.0/24"]
        }
      }
    }
  ]
}
```

### Common Third-Party Tools

**AWS SDK Support:**
- Python (boto3)
- Node.js (aws-sdk)
- Java (AWS SDK for Java)
- .NET (AWS SDK for .NET)
- Go (AWS SDK for Go)
- Ruby (AWS SDK for Ruby)
- PHP (AWS SDK for PHP)

**Message Queue Clients:**
- Celery (Python) - Can use SQS as broker
- Bull (Node.js) - SQS adapter available
- Sidekiq (Ruby) - SQS adapter available

**Monitoring Tools:**
- CloudWatch Dashboards
- Datadog SQS Integration
- New Relic AWS Integration
- Grafana with CloudWatch data source

---

## Monitoring & Troubleshooting

### CloudWatch Metrics

Key metrics to monitor:

**Queue Metrics:**
- `ApproximateNumberOfMessagesVisible` - Messages available for retrieval
- `ApproximateNumberOfMessagesNotVisible` - Messages in flight (being processed)
- `ApproximateAgeOfOldestMessage` - Age of oldest message in queue
- `NumberOfMessagesSent` - Messages sent to queue
- `NumberOfMessagesReceived` - Messages retrieved from queue
- `NumberOfMessagesDeleted` - Successfully processed messages

**DLQ Metrics:**
- `ApproximateNumberOfMessagesVisible` - Failed messages in DLQ

### CloudWatch Alarms

Set up alarms for queue health:

```bash
# Alarm for messages stuck in queue
aws cloudwatch put-metric-alarm \
  --alarm-name sqs-old-messages-dev \
  --metric-name ApproximateAgeOfOldestMessage \
  --namespace AWS/SQS \
  --statistic Maximum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 3600 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=QueueName,Value=domain-operations-dev

# Alarm for DLQ messages
aws cloudwatch put-metric-alarm \
  --alarm-name sqs-dlq-messages-dev \
  --metric-name ApproximateNumberOfMessagesVisible \
  --namespace AWS/SQS \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=QueueName,Value=domain-operations-dev-dlq
```

### Common Issues

#### 1. Messages Not Being Processed

**Symptoms**: Messages accumulate in queue, `ApproximateNumberOfMessagesVisible` increases

**Causes**:
- DNS worker service not running
- DNS worker not polling queue
- Processing errors causing messages to return to queue

**Solution**:
```bash
# Check DNS worker service status
aws ecs describe-services --cluster storefront-cluster --services dns-worker-service-dev

# Check DNS worker logs
aws logs tail /ecs/storefront-dev-dns-worker --since 10m

# Check queue attributes
aws sqs get-queue-attributes \
  --queue-url $(aws ssm get-parameter --name /storefront-dev/sqs/domain-queue-url --query 'Parameter.Value' --output text) \
  --attribute-names All
```

#### 2. Messages Going to DLQ

**Symptoms**: Messages appearing in DLQ, `ApproximateNumberOfMessagesVisible` in DLQ > 0

**Causes**:
- Processing logic errors
- External service failures (Route53, database)
- Invalid message format

**Solution**:
```bash
# Inspect DLQ messages
aws sqs receive-message \
  --queue-url $(aws ssm get-parameter --name /storefront-dev/sqs/domain-queue-dlq-url --query 'Parameter.Value' --output text) \
  --max-number-of-messages 10

# Check DNS worker error logs
aws logs filter-log-events \
  --log-group-name /ecs/storefront-dev-dns-worker \
  --filter-pattern "ERROR"
```

#### 3. Visibility Timeout Issues

**Symptoms**: Same message processed multiple times

**Causes**:
- Processing takes longer than visibility timeout (300s)
- Worker crashes without deleting message

**Solution**:
- Increase visibility timeout if processing takes longer
- Implement heartbeat to extend visibility timeout
- Ensure proper error handling and message deletion

```python
# Extend visibility timeout during long processing
sqs.change_message_visibility(
    QueueUrl=queue_url,
    ReceiptHandle=receipt_handle,
    VisibilityTimeout=600  # Extend to 10 minutes
)
```

#### 4. Permission Errors

**Error**: `AccessDenied` when sending/receiving messages

**Solution**:
```bash
# Verify IAM policy is attached to task role
aws iam list-attached-role-policies --role-name <task-role-name>

# Check policy permissions
aws iam get-policy-version \
  --policy-arn <sqs-policy-arn> \
  --version-id v1
```

---

## Best Practices

### 1. Message Design

**Use structured messages:**
```json
{
  "version": "1.0",
  "action": "activate",
  "domain": "example.com",
  "tenant_id": "123",
  "metadata": {
    "source": "listener-service",
    "timestamp": "2025-10-02T12:00:00Z"
  }
}
```

**Include idempotency keys:**
```json
{
  "idempotency_key": "uuid-here",
  "domain": "example.com",
  "action": "activate"
}
```

### 2. Error Handling

**Implement retry logic with exponential backoff:**
```python
import time

def process_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            process_message(message)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

**Handle partial failures in batch processing:**
```python
def process_batch_safe(messages):
    failed_messages = []
    
    for message in messages:
        try:
            process_message(message)
            delete_message(message)
        except Exception as e:
            failed_messages.append(message)
            log_error(message, e)
    
    return failed_messages
```

### 3. Monitoring

**Log message processing:**
```python
import logging

logger = logging.getLogger(__name__)

def process_message(message):
    message_id = message['MessageId']
    logger.info(f"Processing message: {message_id}")
    
    try:
        # Process
        logger.info(f"Successfully processed: {message_id}")
    except Exception as e:
        logger.error(f"Failed to process {message_id}: {e}")
        raise
```

**Track processing metrics:**
```python
from datetime import datetime

def track_processing_time(func):
    def wrapper(message):
        start = datetime.now()
        result = func(message)
        duration = (datetime.now() - start).total_seconds()
        
        print(f"Processing took {duration}s")
        # Send to CloudWatch custom metrics
        cloudwatch.put_metric_data(
            Namespace='SQS/Processing',
            MetricData=[{
                'MetricName': 'ProcessingDuration',
                'Value': duration,
                'Unit': 'Seconds'
            }]
        )
        return result
    return wrapper
```

### 4. Scaling

**Adjust worker count based on queue depth:**
```python
# In DNS worker service
desired_count = min(
    max(queue_depth // 100, 1),  # 1 worker per 100 messages
    10  # Max 10 workers
)
```

**Use long polling to reduce costs:**
```python
# Always use WaitTimeSeconds for long polling
response = sqs.receive_message(
    QueueUrl=queue_url,
    WaitTimeSeconds=20,  # Max is 20 seconds
    MaxNumberOfMessages=10
)
```

### 5. Security

**Use IAM roles, not access keys:**
- ✅ ECS tasks use task roles automatically
- ❌ Never hardcode AWS credentials

**Encrypt sensitive data in messages:**
```python
import boto3
from cryptography.fernet import Fernet

kms = boto3.client('kms')

def encrypt_message(data):
    # Use KMS to encrypt sensitive data
    response = kms.encrypt(
        KeyId='alias/sqs-encryption-key',
        Plaintext=json.dumps(data)
    )
    return response['CiphertextBlob']
```

**Enable server-side encryption:**
```python
# In sqs_stack.py
queue = sqs.Queue(
    self, "DomainQueue",
    encryption=sqs.QueueEncryption.KMS_MANAGED,
    # Or use custom KMS key
    # encryption_master_key=kms_key
)
```

---

## Additional Resources

- [AWS SQS Documentation](https://docs.aws.amazon.com/sqs/)
- [Boto3 SQS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html)
- [SQS Best Practices](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html)
- [SQS Dead Letter Queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)

---

## Support

For issues or questions:
1. Check CloudWatch metrics for queue health
2. Inspect DLQ for failed messages
3. Review service logs for processing errors
4. Verify IAM permissions are correctly attached
5. Consult the troubleshooting section above
