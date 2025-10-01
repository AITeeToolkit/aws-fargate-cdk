from aws_cdk import Duration, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_servicediscovery as servicediscovery
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from cdk_constructs.fargate_service_construct import FargateServiceConstruct


class ListenerServiceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        cluster: ecs.ICluster,
        image_uri: str,
        db_secret: secretsmanager.ISecret,
        environment: str,
        ecs_task_security_group: ec2.ISecurityGroup,
        service_name: str,
        sqs_managed_policy: iam.IManagedPolicy = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment variables for the listener service
        listener_environment = {
            "REPO": "AITeeToolkit/aws-fargate-cdk",
            "SQS_DNS_OPERATIONS_QUEUE_URL": ssm.StringParameter.value_for_string_parameter(
                self, f"/storefront-{environment}/sqs/dns-operations-queue-url"
            ),
        }

        # Mixed secrets: SSM parameters (strings) and Secrets Manager (ECS Secret objects)
        listener_secrets = {
            "GH_TOKEN": f"/storefront-{environment}/github/PAT",  # SSM parameter
            "PGHOST": ecs.Secret.from_secrets_manager(db_secret, "host"),
            "PGUSER": ecs.Secret.from_secrets_manager(db_secret, "username"),
            "PGPASSWORD": ecs.Secret.from_secrets_manager(db_secret, "password"),
            "PGDATABASE": ecs.Secret.from_secrets_manager(db_secret, "dbname"),
            "PGPORT": ecs.Secret.from_secrets_manager(db_secret, "port"),
        }

        # Create the Fargate service using the construct
        self.service = FargateServiceConstruct(
            self,
            "listener-service",
            cluster=cluster,
            vpc=vpc,
            container_image=ecs.ContainerImage.from_registry(image_uri),
            container_port=8080,  # Default port, won't be used since no ALB
            service_name=service_name,
            environment=listener_environment,
            secrets=listener_secrets,
            security_groups=[ecs_task_security_group],
            desired_count=1,
            sqs_managed_policy=sqs_managed_policy,
            cloud_map_options=ecs.CloudMapOptions(
                name=service_name,
                dns_record_type=servicediscovery.DnsRecordType.A,
                dns_ttl=Duration.seconds(10),
            ),
        )
