from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_servicediscovery as servicediscovery
from aws_cdk.aws_ec2 import IVpc
from constructs import Construct


class SharedStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: IVpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECS Cluster shared by all services
        self.cluster = ecs.Cluster(
            self,
            "StorefrontCluster",
            vpc=vpc,
            container_insights=True,
            cluster_name="storefront-cluster",
            default_cloud_map_namespace=ecs.CloudMapNamespaceOptions(name="storefront.local"),
        )

        # IAM Role for ECS task execution (pulling from ECR, sending logs)
        self.task_execution_role = iam.Role(
            self,
            "ECSTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        self.task_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AmazonECSTaskExecutionRolePolicy"
            )
        )

        # Add SSM Parameter Store permissions for ECS tasks
        self.task_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameters",
                    "ssm:GetParameter",
                    "ssm:GetParametersByPath",
                ],
                resources=[f"arn:aws:ssm:*:*:parameter/storefront-*"],
            )
        )

        # Create security group for ALB
        self.alb_security_group = ec2.SecurityGroup(
            self,
            "AlbSecurityGroup",
            vpc=vpc,
            description="Security group for Application Load Balancer",
            allow_all_outbound=True,
        )

        # Allow HTTPS traffic from internet to ALB
        self.alb_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS from internet",
        )

        # Create security group for ECS tasks (allow all outbound)
        self.ecs_task_sg = ec2.SecurityGroup(
            self,
            "ECSTaskSecurityGroup",
            vpc=vpc,
            description="Security group for ECS tasks",
            allow_all_outbound=True,
        )

        # Allow inbound traffic from ALB on container ports
        self.ecs_task_sg.add_ingress_rule(
            peer=self.alb_security_group,
            connection=ec2.Port.tcp(3000),
            description="Allow HTTP traffic from ALB to web service",
        )

        self.ecs_task_sg.add_ingress_rule(
            peer=self.alb_security_group,
            connection=ec2.Port.tcp(3001),
            description="Allow HTTP traffic from ALB to API service",
        )

        # Allow ECS tasks to communicate with each other (service-to-service)
        self.ecs_task_sg.add_ingress_rule(
            peer=self.ecs_task_sg,
            connection=ec2.Port.all_traffic(),
            description="Allow ECS tasks to communicate with each other",
        )

        # Allow direct access to ECS tasks from specific IPs (for debugging)
        allowed_ips = self.node.try_get_context("allowed_ips")
        if allowed_ips and isinstance(allowed_ips, str):
            import json

            allowed_ips = json.loads(allowed_ips)
        elif not allowed_ips:
            allowed_ips = []

        # Handle both list and dict formats
        if isinstance(allowed_ips, dict):
            ip_items = allowed_ips.items()
        else:
            ip_items = [(ip, ip) for ip in allowed_ips]

        for ip, description in ip_items:
            # Web service port
            self.ecs_task_sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(ip),
                connection=ec2.Port.tcp(3000),
                description=f"Web service: {description}",
            )
            # API service port
            self.ecs_task_sg.add_ingress_rule(
                peer=ec2.Peer.ipv4(ip),
                connection=ec2.Port.tcp(3001),
                description=f"API service: {description}",
            )

        # Create security group for VPC endpoints
        vpc_endpoint_sg = ec2.SecurityGroup(
            self,
            "VpcEndpointSecurityGroup",
            vpc=vpc,
            description="Security group for VPC endpoints",
            allow_all_outbound=False,
        )

        # Allow HTTPS traffic from private subnets to VPC endpoints
        vpc_endpoint_sg.add_ingress_rule(
            peer=self.ecs_task_sg,
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS from ECS tasks",
        )

        # Allow ECS tasks to communicate with VPC endpoints
        self.ecs_task_sg.add_egress_rule(
            peer=vpc_endpoint_sg,
            connection=ec2.Port.tcp(443),
            description="HTTPS to VPC endpoints for AWS services",
        )

        # Allow responses back to ECS tasks
        self.ecs_task_sg.add_ingress_rule(
            peer=vpc_endpoint_sg,
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS from VPC endpoints",
        )

        # Allow VPC endpoints to respond back to ECS tasks
        vpc_endpoint_sg.add_egress_rule(
            peer=self.ecs_task_sg,
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS responses to ECS tasks",
        )

        self.ssm_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self,
            "SSMVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SSM,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg],
        )

        self.ssm_messages_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self,
            "SSMMessagesVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg],
        )

        self.ec2_messages_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self,
            "EC2MessagesVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg],
        )

        # Keep ECR and CloudWatch Logs endpoints (required)
        self.ecr_api_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self,
            "ECRApiVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg],
        )

        self.ecr_dkr_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self,
            "ECRDkrVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg],
        )

        self.logs_vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self,
            "LogsVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            private_dns_enabled=True,
            security_groups=[vpc_endpoint_sg],
        )

        # Gateway endpoint for S3 is correct
        self.s3_vpc_endpoint = ec2.GatewayVpcEndpoint(
            self,
            "S3VpcEndpoint",
            vpc=vpc,
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)],
        )
