from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from constructs import Construct

from cdk_constructs.fargate_service_construct import FargateServiceConstruct


class GoDnsServiceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        cluster: ecs.ICluster,
        image_uri: str,
        environment: str,
        ecs_task_security_group: ec2.ISecurityGroup = None,
        service_name: str = "go-dns-service",
        desired_count: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment variables for the go-dns service
        go_dns_environment = {
            "PORT": "8080",
            "ENVIRONMENT": environment,
        }

        # Create the Fargate service using the construct (no ALB attachment)
        construct_params = {
            "cluster": cluster,
            "vpc": vpc,
            "container_image": ecs.ContainerImage.from_registry(image_uri),
            "container_port": 8080,
            "service_name": service_name,
            "environment": go_dns_environment,
            "desired_count": desired_count,
        }

        # Add security groups if provided
        if ecs_task_security_group:
            construct_params["security_groups"] = [ecs_task_security_group]

        self.service = FargateServiceConstruct(self, "go-dns-service", **construct_params)
