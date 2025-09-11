# fargate_service_construct.py

from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_logs as logs,
    aws_ssm as ssm,
    aws_iam as iam,
    RemovalPolicy
)
from constructs import Construct

class FargateServiceConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        cluster: ecs.Cluster,
        vpc: ec2.IVpc,
        container_image: ecs.ContainerImage,
        listener: elbv2.ApplicationListener,
        desired_count: int = 2,
        container_port: int = 3000,
        host_header: str = None,
        path_pattern: str = "/*",
        priority: int = 100,
        environment: dict = {},
        secrets: dict = {},
    ) -> None:
        super().__init__(scope, id)

        log_group = logs.LogGroup(
            self, f"{id}LogGroup",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK
        )

        task_def = ecs.FargateTaskDefinition(
            self, f"{id}TaskDef",
            memory_limit_mib=512,
            cpu=256
        )

        # Add ECR permissions to task role
        task_def.task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnlyAccess")
        )

        # Add SSM permissions for parameter store access
        task_def.task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath"
                ],
                resources=[f"arn:aws:ssm:*:*:parameter/storefront-*"]
            )
        )

        # Convert secrets dict to ECS secrets format
        ecs_secrets = {}
        for name, value_from in secrets.items():
            ecs_secrets[name] = ecs.Secret.from_ssm_parameter(
                ssm.StringParameter.from_string_parameter_name(
                    self, f"{name}Param", value_from
                )
            )

        container = task_def.add_container(
            f"{id}Container",
            image=container_image,
            container_name=id,
            port_mappings=[ecs.PortMapping(container_port=container_port)],
            environment=environment,
            secrets=ecs_secrets,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix=id,
                log_group=log_group
            )
        )

        service = ecs.FargateService(
            self, f"{id}Service",
            cluster=cluster,
            task_definition=task_def,
            desired_count=desired_count,
            assign_public_ip=False,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )

        # Only configure ALB targets if a listener is provided (for public-facing services)
        if listener:
            listener.add_targets(
                f"{id}Rule",
                port=container_port,
                protocol=elbv2.ApplicationProtocol.HTTP,
                targets=[service],
                conditions=[
                    elbv2.ListenerCondition.path_patterns([path_pattern]),
                    *([elbv2.ListenerCondition.host_headers([host_header])] if host_header else [])
                ],
                priority=priority,
                health_check=elbv2.HealthCheck(path="/")
            )

        # Expose the service so it can be referenced externally (e.g. in WebServiceStack)
        self.service = service