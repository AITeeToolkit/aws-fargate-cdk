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

        # Create security group for VPC endpoints
        vpc_endpoint_sg = ec2.SecurityGroup(
            self, "VpcEndpointSecurityGroup",
            vpc=vpc,
            description="Security group for VPC endpoints",
            allow_all_outbound=False
        )
        
        # Allow HTTPS traffic from private subnets to VPC endpoints
        vpc_endpoint_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS from VPC"
        )

        # ECR VPC endpoints for container image pulling (REQUIRED for ECS)
        self.ecr_api_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "ECRApiVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg]
        )

        self.ecr_dkr_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "ECRDkrVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg]
        )
        
        # EC2 VPC endpoint (REQUIRED for ECS tasks to communicate with ECS service)
        self.ec2_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "EC2VpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.EC2,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg]
        )

        # ECS VPC endpoint (REQUIRED for ECS tasks to register with ECS service)
        self.ecs_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "ECSVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECS,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg]
        )

        # S3 VPC endpoint for ECR layer downloads (Gateway endpoint - no cost)
        self.s3_vpc_endpoint = ec2.GatewayVpcEndpoint(
            self, "S3VpcEndpoint",
            vpc=vpc,
            service=ec2.GatewayVpcEndpointAwsService.S3
        )

        # CloudWatch Logs VPC endpoint (for ECS logging)
        self.logs_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "LogsVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg]
        )

        # Create security group for ECS tasks
        self.ecs_task_sg = ec2.SecurityGroup(
            self, "ECSTaskSecurityGroup",
            vpc=vpc,
            description="Security group for ECS tasks",
            allow_all_outbound=True
        )
        
        # Allow ECS tasks to communicate with VPC endpoints
        self.ecs_task_sg.add_egress_rule(
            peer=ec2.Peer.security_group_id(vpc_endpoint_sg.security_group_id),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS to VPC endpoints"
        )