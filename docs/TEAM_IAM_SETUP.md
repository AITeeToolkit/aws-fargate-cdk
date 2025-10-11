# Team IAM Permissions Setup (AWS IAM Identity Center / SSO)

This guide explains how to set up fine-grained IAM permissions for your team using **AWS IAM Identity Center (SSO)** to prevent accidental infrastructure deletion.

## Permission Levels

### 1. **Team Developer** (Can Deploy, Cannot Delete)
- ✅ View all infrastructure
- ✅ Deploy and update services
- ✅ Update ECS task definitions
- ✅ Push/pull Docker images
- ✅ Read logs and metrics
- ✅ Send/receive SQS messages
- ✅ Update SSM parameters
- ❌ **Cannot delete** any infrastructure
- ❌ **Cannot stop** databases or services

**Use Case:** Regular developers who deploy code changes

### 2. **Read-Only** (View Only)
- ✅ View all infrastructure
- ✅ Read logs and metrics
- ✅ Query CloudWatch
- ❌ Cannot make any changes

**Use Case:** Junior developers, QA, observers

### 3. **Admin** (Full Access)
- ✅ Everything
- ✅ Can delete infrastructure

**Use Case:** DevOps leads, platform engineers

---

## Setup Instructions

### Step 1: Create IAM Policies

```bash
cd /Users/nel/Repos/aws-fargate-cdk

# Create Developer Policy
aws iam create-policy \
  --policy-name TeamDeveloper \
  --policy-document file://iam-policies/team-developer-policy.json \
  --description "Allows deployment and updates but prevents deletion"

# Create Read-Only Policy
aws iam create-policy \
  --policy-name TeamReadOnly \
  --policy-document file://iam-policies/team-readonly-policy.json \
  --description "Read-only access to Storefront infrastructure"

# Note the policy ARNs from the output
```

### Step 2: Create Permission Sets in IAM Identity Center

#### Via AWS Console (Recommended)

1. Go to **IAM Identity Center** console
2. Click **Permission sets** → **Create permission set**
3. Choose **Custom permission set**
4. Name it `Developer`
5. Click **Attach policies** → **Customer managed policies**
6. Select `TeamDeveloper`
7. Click **Next** → **Create**

Repeat for `ReadOnly` permission set.

#### Via AWS CLI

```bash
# Get your IAM Identity Center instance ARN
INSTANCE_ARN=$(aws sso-admin list-instances --query 'Instances[0].InstanceArn' --output text)

# Create Developer Permission Set
aws sso-admin create-permission-set \
  --instance-arn $INSTANCE_ARN \
  --name Developer \
  --description "Developer access - can deploy but not delete"

# List all permission sets to find the ARN
aws sso-admin list-permission-sets --instance-arn $INSTANCE_ARN

# Describe each to find "Developer" (copy the ARN from output above)
DEV_PERMISSION_SET_ARN="arn:aws:sso:::permissionSet/ssoins-72232c60ff39d5ca/ps-9f75bcba863ff47b"

# Attach the Developer policy (customer managed policy)
aws sso-admin attach-customer-managed-policy-reference-to-permission-set \
  --instance-arn $INSTANCE_ARN \
  --permission-set-arn $DEV_PERMISSION_SET_ARN \
  --customer-managed-policy-reference Name=TeamDeveloper,Path=/

# # Create Read-Only Permission Set
# aws sso-admin create-permission-set \
#   --instance-arn $INSTANCE_ARN \
#   --name ReadOnly \
#   --description "Read-only access to infrastructure"

# # Find the ReadOnly permission set ARN from the list above
# RO_PERMISSION_SET_ARN="<paste-arn-here>"

# # Attach the Read-Only policy (customer managed policy)
# aws sso-admin attach-customer-managed-policy-reference-to-permission-set \
#   --instance-arn $INSTANCE_ARN \
#   --permission-set-arn $RO_PERMISSION_SET_ARN \
#   --customer-managed-policy-reference Name=TeamReadOnly,Path=/

# Provision the permission sets (required before assignment)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws sso-admin provision-permission-set \
  --instance-arn $INSTANCE_ARN \
  --permission-set-arn $DEV_PERMISSION_SET_ARN \
  --target-type AWS_ACCOUNT \
  --target-id $ACCOUNT_ID

# aws sso-admin provision-permission-set \
#   --instance-arn $INSTANCE_ARN \
#   --permission-set-arn $RO_PERMISSION_SET_ARN \
#   --target-type AWS_ACCOUNT \
#   --target-id $ACCOUNT_ID
```

### Step 3: Assign Groups to AWS Accounts

#### Via AWS Console (Recommended)

1. Go to **IAM Identity Center** → **AWS accounts**
2. Select your AWS account
3. Click **Assign users or groups**
4. Select users/groups
5. Click **Next**
6. Select the permission set (`Developer` or `ReadOnly`)
7. Click **Next** → **Submit**

#### Via AWS CLI

```bash
# Get identity store ID
IDENTITY_STORE_ID=$(aws sso-admin list-instances --query 'Instances[0].IdentityStoreId' --output text)

# List groups to find group IDs
aws identitystore list-groups --identity-store-id $IDENTITY_STORE_ID

# Assign GROUP to account with Developer permission set
aws sso-admin create-account-assignment \
  --instance-arn $INSTANCE_ARN \
  --target-id $ACCOUNT_ID \
  --target-type AWS_ACCOUNT \
  --permission-set-arn $DEV_PERMISSION_SET_ARN \
  --principal-type GROUP \
  --principal-id <GROUP_ID>

# Assign GROUP to account with Read-Only permission set
aws sso-admin create-account-assignment \
  --instance-arn $INSTANCE_ARN \
  --target-id $ACCOUNT_ID \
  --target-type AWS_ACCOUNT \
  --permission-set-arn $RO_PERMISSION_SET_ARN \
  --principal-type GROUP \
  --principal-id <GROUP_ID>
```

**Note:** Use GROUP assignments instead of USER for easier management.

---

## What Each Policy Allows/Denies

### Developer Policy

**✅ Allowed Actions:**
- Deploy CloudFormation stacks (create/update)
- Update ECS services and task definitions
- Push/pull ECR images
- Read/write SQS messages
- Publish to SNS topics
- Update SSM parameters
- Read secrets (but not delete)
- View all infrastructure
- Read CloudWatch logs

**❌ Denied Actions:**
- Delete CloudFormation stacks
- Delete ECS services/clusters
- Delete RDS databases
- Delete load balancers
- Delete Route53 hosted zones
- Delete S3 buckets
- Delete log groups
- Delete SSM parameters
- Delete secrets
- Delete SQS queues
- Delete SNS topics
- Delete ECR repositories
- Delete VPCs/subnets/security groups
- Stop/reboot RDS instances
- Stop ECS tasks

### Read-Only Policy

**✅ Allowed Actions:**
- View all infrastructure (Describe*, Get*, List*)
- Read CloudWatch logs
- Query CloudWatch metrics

**❌ Denied Actions:**
- Everything else (all Create*, Update*, Delete*, Put*, Modify* actions)

---

## Testing Permissions

### Access AWS via SSO

```bash
# Configure AWS CLI for SSO
aws configure sso

# Login via SSO
aws sso login --profile <profile-name>

# Use the profile
export AWS_PROFILE=<profile-name>
```

### Test Developer Access
```bash
# Should work - Deploy a stack
cdk deploy WebServiceStack-dev

# Should work - Update ECS service
aws ecs update-service \
  --cluster storefront-cluster \
  --service web-service \
  --force-new-deployment

# Should FAIL - Delete a stack
cdk destroy WebServiceStack-dev
# Error: User is not authorized to perform: cloudformation:DeleteStack

# Should FAIL - Delete database
aws rds delete-db-instance --db-instance-identifier rds-dev
# Error: User is not authorized to perform: rds:DeleteDBInstance
```

### Test Read-Only Access
```bash
# Should work - View stacks
aws cloudformation list-stacks

# Should work - View ECS services
aws ecs list-services --cluster storefront-cluster

# Should FAIL - Deploy
cdk deploy WebServiceStack-dev
# Error: User is not authorized to perform: cloudformation:CreateStack
```

---

## Updating Policies

If you need to modify permissions:

```bash
# Update Developer policy
aws iam create-policy-version \
  --policy-arn arn:aws:iam::156041439702:policy/TeamDeveloper \
  --policy-document file://iam-policies/team-developer-policy.json \
  --set-as-default

# Update Read-Only policy
aws iam create-policy-version \
  --policy-arn arn:aws:iam::156041439702:policy/TeamReadOnly \
  --policy-document file://iam-policies/team-readonly-policy.json \
  --set-as-default
```

---

## Emergency Access

If a developer needs temporary admin access for a critical fix:

```bash
# Temporarily add to admin group
aws iam add-user-to-group \
  --group-name Admins \
  --user-name john.doe

# After the fix, remove from admin group
aws iam remove-user-from-group \
  --group-name Admins \
  --user-name john.doe
```

---

## Best Practices

1. **Principle of Least Privilege**: Start with read-only, grant developer access as needed
2. **Use Groups**: Never attach policies directly to users
3. **Regular Audits**: Review group membership quarterly
4. **MFA Required**: Enforce MFA for all users with write access
5. **CloudTrail Monitoring**: Monitor for denied actions (potential security issues)
6. **Separate Prod Access**: Consider separate policies for prod vs dev/staging

---

## Troubleshooting

### "Access Denied" Errors

1. Check which permission sets the user has:
```bash
# List account assignments
aws sso-admin list-account-assignments \
  --instance-arn $INSTANCE_ARN \
  --account-id $ACCOUNT_ID
```

2. Check which policies are attached to the permission set:
```bash
aws sso-admin list-managed-policies-in-permission-set \
  --instance-arn $INSTANCE_ARN \
  --permission-set-arn $PERMISSION_SET_ARN
```

3. Verify the user is logged in via SSO:
```bash
aws sts get-caller-identity
```

### User Can't Deploy

- Verify they're assigned the `Developer` permission set
- Check if the policy is attached to the permission set
- Ensure they're logged in via SSO (`aws sso login`)
- Verify they have `iam:PassRole` permission for ECS

### User Can Still Delete

- Check if they have multiple permission sets (e.g., also assigned AdministratorAccess)
- Verify the Deny statement is in the policy
- Remember: Explicit Deny always wins over Allow
- Check if they're using a different AWS profile with admin access

---

## Security Considerations

⚠️ **Important Notes:**

1. The Developer policy allows **PassRole** for ECS - this is necessary for deployments but could be abused
2. Developers can still **update** infrastructure (e.g., change instance sizes) - just not delete
3. Read-Only users can see **secret names** but not values
4. Consider using **AWS Organizations SCPs** for additional guardrails
5. Enable **CloudTrail** to audit all actions
6. Set up **CloudWatch Alarms** for denied actions

---

## Next Steps

1. Create the policies using the commands above
2. Create IAM groups
3. Add team members to appropriate groups
4. Test permissions with each user
5. Document any custom permissions needed for your team
6. Set up MFA enforcement
7. Enable CloudTrail logging
