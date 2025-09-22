from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy
)
from aws_cdk import aws_opensearchservice as opensearch
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class OpenSearchStack(Stack):
    """
    OpenSearch stack for AWS Fargate CDK implementation.
    Uses Elasticsearch service with OpenSearch engine.
    Configured for AWS Free Tier usage with CloudWatch integration.
    """

    def __init__(self, scope: Construct, construct_id: str, 
                 environment: str = "dev", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.env_name = environment

        # Create OpenSearch domain with free tier configuration
        self.domain = opensearch.Domain(
            self, f"OpenSearchDomain-{self.env_name}",
            version=opensearch.EngineVersion.OPENSEARCH_2_3,
            
            # Free tier instance configuration
            capacity=opensearch.CapacityConfig(
                data_nodes=1,  # Single node for free tier
                data_node_instance_type="t3.small.search",  # Free tier eligible
                master_nodes=0,  # No dedicated master nodes for free tier
            ),
            
            # EBS configuration (10GB free tier limit)
            ebs=opensearch.EbsOptions(
                enabled=True,
                volume_size=10,  # 10GB free tier limit
                volume_type=ec2.EbsDeviceVolumeType.GP3
            ),
            
            # Public access configuration - no VPC
            # vpc=None,  # Remove VPC configuration for public access
            
            # Zone awareness disabled for single node
            zone_awareness=opensearch.ZoneAwarenessConfig(
                enabled=False
            ),
            
            # Minimal logging to keep costs low
            logging=opensearch.LoggingOptions(
                slow_search_log_enabled=False,
                app_log_enabled=False,
                slow_index_log_enabled=False
            ),
            
            # Domain endpoint options
            enforce_https=True,
            
            # Encryption
            encryption_at_rest=opensearch.EncryptionAtRestOptions(
                enabled=True
            ),
            node_to_node_encryption=True,
            
            # Disable fine-grained access control for simpler access
            # This should enable anonymous access by default
            
            # Automated snapshots
            automated_snapshot_start_hour=2,  # 2 AM UTC
            
            # Removal policy
            removal_policy=RemovalPolicy.DESTROY  # For development
        )

        # Create IAM role for Fargate tasks to access OpenSearch
        self.fargate_opensearch_role = iam.Role(
            self, "FargateOpenSearchRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Role for Fargate tasks to access OpenSearch"
        )

        # Create policy for OpenSearch access
        opensearch_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "es:ESHttpPost",
                "es:ESHttpPut",
                "es:ESHttpGet",
                "es:ESHttpDelete",
                "es:ESHttpHead"
            ],
            resources=[f"{self.domain.domain_arn}/*"]
        )

        self.fargate_opensearch_role.add_to_policy(opensearch_policy)

        # Add access policy to OpenSearch domain for public access
        self.domain.add_access_policies(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[
                    iam.AccountRootPrincipal(),  # Allow your AWS account root (includes all IAM users/roles)
                    iam.ArnPrincipal(self.fargate_opensearch_role.role_arn)  # Allow Fargate role
                ],
                actions=["es:*"],
                resources=[f"{self.domain.domain_arn}/*"]
            )
        )

        self.domain.add_access_policies(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=["es:ESHttpGet", "es:ESHttpPost", "es:ESHttpPut", "es:ESHttpDelete"],
                resources=[f"{self.domain.domain_arn}/*"],
                conditions={
                    "IpAddress": {"aws:SourceIp": ["70.122.3.208/32"]}  # replace with your IP
                }
            )
        )
        
        # Store domain endpoint in SSM for easy access
        ssm.StringParameter(
            self, "OpenSearchEndpointParameter",
            parameter_name=f"/storefront-{self.env_name}/opensearch/endpoint",
            string_value=f"https://{self.domain.domain_endpoint}",
            description="OpenSearch domain endpoint URL"
        )


        # Outputs
        CfnOutput(
            self, "OpenSearchDomainEndpoint",
            value=self.domain.domain_endpoint,
            description="OpenSearch domain endpoint"
        )

        CfnOutput(
            self, "OpenSearchDashboardsURL",
            value=f"https://{self.domain.domain_endpoint}/_dashboards/",
            description="OpenSearch Dashboards URL"
        )

        CfnOutput(
            self, "OpenSearchDomainArn",
            value=self.domain.domain_arn,
            description="OpenSearch domain ARN"
        )

        CfnOutput(
            self, "FargateOpenSearchRoleArn",
            value=self.fargate_opensearch_role.role_arn,
            description="IAM role ARN for Fargate tasks to access OpenSearch"
        )

    @property
    def domain_endpoint(self) -> str:
        """Get the OpenSearch domain endpoint"""
        return self.domain.domain_endpoint

    @property
    def domain_arn(self) -> str:
        """Get the OpenSearch domain ARN"""
        return self.domain.domain_arn
