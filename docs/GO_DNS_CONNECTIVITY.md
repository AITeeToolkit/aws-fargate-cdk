# Go-DNS Service Connectivity Guide

This document explains how to connect to the Go-DNS service both externally (from the internet) and internally (from other ECS services).

## Overview

The Go-DNS service is deployed as a Fargate task in the ECS cluster and is accessible through:
- **External Access**: Via Application Load Balancer (ALB) with HTTPS
- **Internal Access**: Via ECS Service Discovery (private DNS)

## External Access (Public Internet)

### Configuration
- **Domain**: Configured via SSM Parameter Store at `/storefront-dev/go-dns/url`
- **Protocol**: HTTPS (port 443)
- **Certificate**: ACM certificate for the subdomain
- **Load Balancer**: Shared ALB with host-based routing

### Connection Details

**Endpoint:**
The endpoint URL is stored in SSM Parameter Store and should be fetched dynamically:
- **Parameter Name**: `/storefront-dev/go-dns/url`
- **Current Value**: `dns.042322.xyz`
- **Protocol**: `https://`

**Fetching the URL (TypeScript/Node.js):**
```typescript
import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';

async function getGoDnsUrl(environment: string = 'dev'): Promise<string> {
  const client = new SSMClient({ region: process.env.AWS_REGION || 'us-east-1' });
  const command = new GetParameterCommand({
    Name: `/storefront-${environment}/go-dns/url`
  });

  const result = await client.send(command);
  const domain = result.Parameter?.Value;

  if (!domain) {
    throw new Error('Go-DNS URL not found in SSM');
  }

  return `https://${domain}`;
}

// Usage
const goDnsUrl = await getGoDnsUrl();
const response = await fetch(`${goDnsUrl}/api/endpoint`);
```

**Fetching the URL (Python):**
```python
import boto3

def get_go_dns_url(environment='dev'):
    ssm = boto3.client('ssm', region_name='us-east-1')
    parameter = ssm.get_parameter(Name=f'/storefront-{environment}/go-dns/url')
    domain = parameter['Parameter']['Value']
    return f'https://{domain}'

# Usage
go_dns_url = get_go_dns_url()
response = requests.get(f'{go_dns_url}/api/endpoint')
```

**Fetching the URL (Bash):**
```bash
# Get the URL from SSM
GO_DNS_DOMAIN=$(aws ssm get-parameter \
  --name /storefront-dev/go-dns/url \
  --region us-east-1 \
  --query 'Parameter.Value' \
  --output text)

GO_DNS_URL="https://${GO_DNS_DOMAIN}"

# Use it
curl -X GET "${GO_DNS_URL}/api/endpoint" \
  -H "Content-Type: application/json"
```

**Health Check:**
```bash
GO_DNS_URL=$(aws ssm get-parameter --name /storefront-dev/go-dns/url --region us-east-1 --query 'Parameter.Value' --output text)
curl https://${GO_DNS_URL}/health
```

### How It Works

1. **DNS Resolution**: `dns.042322.xyz` → Route53 A record → ALB DNS name
2. **TLS Termination**: ALB terminates HTTPS using ACM certificate
3. **Host-Based Routing**: ALB routes requests with `Host: dns.042322.xyz` header to go-dns target group
4. **Target Group**: Forwards to ECS tasks on port 8080
5. **Security**: ALB security group (sg-0543ab2771cae3f25) → ECS task security group (sg-001946b0036e3a4d5) on port 8080

### Security Groups

**ALB Security Group** (`sg-0543ab2771cae3f25`):
- Inbound: 443 (HTTPS) from 0.0.0.0/0
- Outbound: 8080 to ECS task security group

**ECS Task Security Group** (`sg-001946b0036e3a4d5`):
- Inbound: 8080 from ALB security group
- Outbound: All traffic

## Internal Access (ECS Service-to-Service)

### Configuration
- **Service Discovery**: AWS Cloud Map namespace
- **Private DNS**: `go-dns-service.storefront-cluster.local`
- **Protocol**: HTTP (port 8080)
- **Network**: VPC private subnets

### Connection Details

**Endpoint (from other ECS services):**
```
http://go-dns-service.storefront-cluster.local:8080
```

**Health Check:**
```bash
curl http://go-dns-service.storefront-cluster.local:8080/health
```

**Example Request (from API/Web service):**
```python
import requests

# Internal service-to-service call
response = requests.get(
    "http://go-dns-service.storefront-cluster.local:8080/api/endpoint",
    headers={"Content-Type": "application/json"}
)
```

### How It Works

1. **Service Discovery**: ECS registers tasks with Cloud Map
2. **DNS Resolution**: Cloud Map provides private DNS name
3. **Direct Connection**: Services connect directly via VPC networking
4. **Security**: ECS task security group allows all traffic between tasks

### Benefits of Internal Access

- **Lower Latency**: Direct VPC networking, no ALB hop
- **No TLS Overhead**: HTTP within secure VPC
- **Cost Savings**: No ALB data transfer charges
- **Automatic Discovery**: DNS updates automatically as tasks scale

## Configuration Management

### Setting the Go-DNS Domain

The go-dns domain is configured via SSM Parameter Store:

```bash
# Set the domain
aws ssm put-parameter \
  --name /storefront-dev/go-dns/url \
  --value "dns.042322.xyz" \
  --type String \
  --description "Go-DNS service domain URL" \
  --region us-east-1 \
  --overwrite

# Get the current domain
aws ssm get-parameter \
  --name /storefront-dev/go-dns/url \
  --region us-east-1 \
  --query 'Parameter.Value' \
  --output text
```

### Updating the Domain

1. Update the SSM parameter with the new domain
2. Ensure the domain is in the active domains list in the database
3. Redeploy the infrastructure: `cdk deploy --all`
4. The new domain will be added to the ALB with a new certificate

## Troubleshooting

### External Access Issues

**Problem: Connection timeout or refused**
```bash
# Check ALB target health
aws elbv2 describe-target-health \
  --target-group-arn <target-group-arn> \
  --region us-east-1
```

**Problem: SSL certificate error**
```bash
# Verify certificate is attached to listener
aws elbv2 describe-listeners \
  --load-balancer-arn <alb-arn> \
  --region us-east-1
```

**Problem: 503 Service Unavailable**
- Check ECS service is running: `aws ecs list-tasks --cluster storefront-cluster --service-name go-dns-service`
- Check target health (see above)
- Verify security group rules allow port 8080

### Internal Access Issues

**Problem: DNS resolution fails**
```bash
# Check service discovery registration
aws servicediscovery list-services --region us-east-1

# Check Cloud Map namespace
aws servicediscovery list-namespaces --region us-east-1
```

**Problem: Connection refused**
- Verify service is running in the same VPC
- Check security group allows traffic between tasks
- Ensure service discovery is enabled

### Health Check Failures

**Check ECS task logs:**
```bash
aws logs tail /ecs/go-dns-service --follow --region us-east-1
```

**Verify health endpoint:**
```bash
# External
curl -v https://dns.042322.xyz/health

# Internal (from another ECS task)
curl -v http://go-dns-service.storefront-cluster.local:8080/health
```

## Architecture Diagram

```
External Request Flow:
Internet → Route53 (dns.042322.xyz) → ALB (HTTPS:443) → Target Group → ECS Task (HTTP:8080)

Internal Request Flow:
ECS Service → Cloud Map DNS → ECS Task (HTTP:8080)
```

## Environment Variables

The go-dns service receives these environment variables:

```bash
PORT=8080                    # Container port
ENVIRONMENT=dev              # Deployment environment (dev/staging/prod)
```

## Related Resources

- **ALB**: `web-alb-dev-1`
- **Target Group**: Auto-generated by CDK (format: `MultiA-Alb1H-*`)
- **ECS Cluster**: `storefront-cluster`
- **Service Name**: `go-dns-service`
- **VPC**: `StorefrontVPC` (10.0.0.0/16)
- **Subnets**: Private subnets in us-east-1a and us-east-1b

## Monitoring

### CloudWatch Metrics

**ALB Metrics:**
- `TargetResponseTime`: Response time from go-dns service
- `HealthyHostCount`: Number of healthy targets
- `UnHealthyHostCount`: Number of unhealthy targets
- `RequestCount`: Total requests to go-dns

**ECS Metrics:**
- `CPUUtilization`: Task CPU usage
- `MemoryUtilization`: Task memory usage

### CloudWatch Logs

**Log Group:** Auto-generated by CDK (format: `/ecs/go-dns-service-*`)

**View logs:**
```bash
aws logs tail <log-group-name> --follow --region us-east-1
```

## Security Best Practices

1. **Use HTTPS for external access** - Always use the HTTPS endpoint for external requests
2. **Use HTTP for internal access** - Within VPC, HTTP is secure and more efficient
3. **Rotate credentials regularly** - If using authentication, rotate API keys/tokens
4. **Monitor access logs** - Review ALB access logs for suspicious activity
5. **Keep security groups minimal** - Only allow necessary ports and sources
6. **Use IAM roles** - For AWS service access, use task IAM roles instead of credentials

## Support

For issues or questions:
1. Check CloudWatch logs for errors
2. Verify target health in ALB console
3. Review ECS service events
4. Contact the infrastructure team
