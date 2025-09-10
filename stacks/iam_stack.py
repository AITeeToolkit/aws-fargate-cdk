from aws_cdk import (
    Stack,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct


class IAMStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM user for CI/CD
        self.ci_user = iam.User(
            self, "FargateApplicationCIUser",
            user_name="fargate-application-ci",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryPowerUser")
            ]
        )

        # CDK Bootstrap and Deployment permissions
        cdk_policy = iam.Policy(
            self, "CDKDeploymentPolicy",
            policy_name="CDKDeploymentPolicy",
            statements=[
                # CDK Bootstrap SSM access
                iam.PolicyStatement(
                    sid="CDKBootstrapAccess",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ssm:GetParameter",
                        "ssm:GetParameters"
                    ],
                    resources=[
                        f"arn:aws:ssm:*:{self.account}:parameter/cdk-bootstrap/*"
                    ]
                ),
                # CDK Role assumption
                iam.PolicyStatement(
                    sid="CDKRoleAssumption",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sts:AssumeRole"
                    ],
                    resources=[
                        f"arn:aws:iam::{self.account}:role/cdk-hnb659fds-deploy-role-*",
                        f"arn:aws:iam::{self.account}:role/cdk-hnb659fds-file-publishing-role-*",
                        f"arn:aws:iam::{self.account}:role/cdk-hnb659fds-image-publishing-role-*",
                        f"arn:aws:iam::{self.account}:role/cdk-hnb659fds-lookup-role-*"
                    ]
                ),
                # CloudFormation read access
                iam.PolicyStatement(
                    sid="CloudFormationReadAccess",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "cloudformation:DescribeStacks",
                        "cloudformation:DescribeStackEvents",
                        "cloudformation:DescribeStackResources",
                        "cloudformation:GetTemplate",
                        "cloudformation:ListStacks",
                        "cloudformation:ListStackResources"
                    ],
                    resources=["*"]
                ),
                # S3 CDK Assets access
                iam.PolicyStatement(
                    sid="S3CDKAssetsAccess",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:ListBucket"
                    ],
                    resources=[
                        f"arn:aws:s3:::cdk-hnb659fds-assets-{self.account}-*",
                        f"arn:aws:s3:::cdk-hnb659fds-assets-{self.account}-*/*"
                    ]
                ),
                # CodeBuild permissions for CI/CD
                iam.PolicyStatement(
                    sid="CodeBuildAccess",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "codebuild:BatchGetBuilds",
                        "codebuild:StartBuild"
                    ],
                    resources=[
                        f"arn:aws:codebuild:*:{self.account}:project/storefront-*"
                    ]
                )
            ]
        )

        # Attach policy to user
        cdk_policy.attach_to_user(self.ci_user)

        # Create access key for GitHub Actions
        self.access_key = iam.AccessKey(
            self, "FargateApplicationCIAccessKey",
            user=self.ci_user
        )

        # Output the access key details
        CfnOutput(
            self, "AccessKeyId",
            value=self.access_key.access_key_id,
            description="Access Key ID for CI/CD user"
        )

        CfnOutput(
            self, "SecretAccessKey",
            value=self.access_key.secret_access_key.unsafe_unwrap(),
            description="Secret Access Key for CI/CD user (store securely)"
        )
