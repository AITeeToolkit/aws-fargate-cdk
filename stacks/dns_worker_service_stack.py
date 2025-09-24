from aws_cdk import (
    Stack,
    Duration,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_iam as iam,
)
from constructs import Construct
from cdk_constructs.fargate_service_construct import FargateServiceConstruct


class DNSWorkerServiceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        cluster: ecs.ICluster,
        image_uri: str,
        environment: str,
        ecs_task_security_group: ec2.ISecurityGroup,
        service_name: str,
        sqs_managed_policy: iam.IManagedPolicy = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment variables for the DNS worker service
        dns_worker_environment = {
            "REPO": "AITeeToolkit/aws-fargate-cdk",
            "SQS_DNS_OPERATIONS_QUEUE_URL": ssm.StringParameter.value_for_string_parameter(self, f"/storefront-{environment}/sqs/dns-operations-queue-url"),
            "AWS_DEFAULT_REGION": "us-east-1",
        }

        # Secrets for the DNS worker service
        dns_worker_secrets = {
            "GH_TOKEN": f"/storefront-{environment}/github/PAT",  # SSM parameter
            "AWS_ACCESS_KEY_ID": f"/storefront-{environment}/route53/AWS_ACCESS_KEY_ID",  # SSM parameter
            "AWS_SECRET_ACCESS_KEY": f"/storefront-{environment}/route53/AWS_SECRET_ACCESS_KEY",  # SSM parameter
        }

        # Create the Fargate service using the construct
        self.service = FargateServiceConstruct(
            self, "dns-worker-service",
            cluster=cluster,
            vpc=vpc,
            container_image=ecs.ContainerImage.from_registry(image_uri),
            container_port=8080,  # Default port, won't be used since no ALB
            service_name=service_name,
            environment=dns_worker_environment,
            secrets=dns_worker_secrets,
            security_groups=[ecs_task_security_group],
            desired_count=1,
            sqs_managed_policy=sqs_managed_policy,
        )
