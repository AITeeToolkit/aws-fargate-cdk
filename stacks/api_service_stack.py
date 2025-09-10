from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_logs as logs,
    RemovalPolicy
)
from constructs import Construct

class APIServiceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        cluster: ecs.ICluster,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Log group for internal API logs
        log_group = logs.LogGroup(
            self, "APIServiceLogGroup",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK
        )

        # Task definition
        task_def = ecs.FargateTaskDefinition(
            self, "APIServiceTaskDef",
            memory_limit_mib=512,
            cpu=256
        )

        task_def.add_container(
            "APIContainer",
            image=ecs.ContainerImage.from_registry("public.ecr.aws/nginx/nginx"),
            container_name="api",
            port_mappings=[ecs.PortMapping(container_port=3000)],
            environment={
                "ENV": "production",
                "API_KEY": "dummy-key"
            },
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="api",
                log_group=log_group
            )
        )

        # Fargate service (no public IP, no ALB)
        ecs.FargateService(
            self, "APIService",
            cluster=cluster,
            task_definition=task_def,
            desired_count=2,
            assign_public_ip=False,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )