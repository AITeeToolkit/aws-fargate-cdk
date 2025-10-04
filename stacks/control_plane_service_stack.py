from aws_cdk import Duration, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from cdk_constructs.fargate_service_construct import FargateServiceConstruct


class ControlPlaneServiceStack(Stack):
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
        db_secret,
        sqs_managed_policy: iam.IManagedPolicy = None,
        desired_count: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment variables for the control plane service (3 worker queues)
        control_plane_environment = {
            "REPO": "AITeeToolkit/aws-fargate-cdk",
            "DATABASE_OPERATIONS_QUEUE_URL": ssm.StringParameter.value_for_string_parameter(
                self, f"/storefront-{environment}/sqs/database-operations-queue-url"
            ),
            "ROUTE53_OPERATIONS_QUEUE_URL": ssm.StringParameter.value_for_string_parameter(
                self, f"/storefront-{environment}/sqs/route53-operations-queue-url"
            ),
            "GITHUB_WORKFLOW_QUEUE_URL": ssm.StringParameter.value_for_string_parameter(
                self, f"/storefront-{environment}/sqs/github-workflow-queue-url"
            ),
            "AWS_DEFAULT_REGION": "us-east-1",
        }

        # Secrets for the control plane service
        control_plane_secrets = {
            "GH_TOKEN": ecs.Secret.from_ssm_parameter(
                ssm.StringParameter.from_string_parameter_name(
                    self, "GHTokenParam", f"/storefront-{environment}/github/PAT"
                )
            ),
            "PGHOST": ecs.Secret.from_secrets_manager(db_secret, "host"),
            "PGUSER": ecs.Secret.from_secrets_manager(db_secret, "username"),
            "PGPASSWORD": ecs.Secret.from_secrets_manager(db_secret, "password"),
            "PGDATABASE": ecs.Secret.from_secrets_manager(db_secret, "dbname"),
            "PGPORT": ecs.Secret.from_secrets_manager(db_secret, "port"),
        }

        # Create the Fargate service using the construct
        self.service = FargateServiceConstruct(
            self,
            "control-plane-service",
            cluster=cluster,
            vpc=vpc,
            container_image=ecs.ContainerImage.from_registry(image_uri),
            container_port=8080,  # Default port, won't be used since no ALB
            service_name=service_name,
            environment=control_plane_environment,
            secrets=control_plane_secrets,
            security_groups=[ecs_task_security_group],
            desired_count=desired_count,
            sqs_managed_policy=sqs_managed_policy,
        )
