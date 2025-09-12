from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ec2 as ec2,
)
from constructs import Construct
from aws_cdk.aws_ec2 import IVpc

class SharedStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: IVpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECS Cluster shared by all services
        self.cluster = ecs.Cluster(
            self, "StorefrontCluster",
            vpc=vpc,
            container_insights=True
        )

        # IAM Role for ECS task execution (pulling from ECR, sending logs)
        self.task_execution_role = iam.Role(
            self, "ECSTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )

        self.task_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
        )

        # Add SSM Parameter Store permissions for ECS tasks
        self.task_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameters",
                    "ssm:GetParameter",
                    "ssm:GetParametersByPath"
                ],
                resources=[
                    f"arn:aws:ssm:*:*:parameter/storefront-*"
                ]
            )
        )

        # Create VPC endpoints for SSM Parameter Store access from private subnets
        self.ssm_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "SSMVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True
        )

        # VPC endpoint for SSM Messages (required for Session Manager)
        self.ssm_messages_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "SSMMessagesVpcEndpoint", 
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True
        )

        # ECR VPC endpoints for container image pulling
        self.ecr_api_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "ECRApiVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True
        )

        self.ecr_dkr_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "ECRDkrVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True
        )

        # S3 VPC endpoint for ECR layer downloads (Gateway endpoint - no cost)
        self.s3_vpc_endpoint = ec2.GatewayVpcEndpoint(
            self, "S3VpcEndpoint",
            vpc=vpc,
            service=ec2.GatewayVpcEndpointAwsService.S3
        )

        # CloudWatch Logs VPC endpoint
        self.logs_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "LogsVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True
        )