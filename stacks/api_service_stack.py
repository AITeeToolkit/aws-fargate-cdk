import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_servicediscovery as servicediscovery
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from cdk_constructs.fargate_service_construct import FargateServiceConstruct


class APIServiceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        cluster: ecs.ICluster,
        image_uri: str,
        db_secret: secretsmanager.ISecret,
        environment: str = "dev",
        service_name: str,
        ecs_task_security_group: ec2.ISecurityGroup = None,
        opensearch_role: iam.IRole = None,
        sqs_managed_policy: iam.IManagedPolicy = None,
        desired_count: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DATABASE_URL from database instance properties
        database_url = f"postgresql://{db_secret.secret_value_from_json('username').unsafe_unwrap()}:{db_secret.secret_value_from_json('password').unsafe_unwrap()}@{db_secret.secret_value_from_json('host').unsafe_unwrap()}:{db_secret.secret_value_from_json('port').unsafe_unwrap()}/{db_secret.secret_value_from_json('dbname').unsafe_unwrap()}?sslmode=no-verify"

        # OpenSearch parameter name (let API service read it directly)
        opensearch_parameter_name = f"/storefront-{environment}/opensearch/endpoint"

        # SQS parameter names (let API service read them directly)
        main_queue_parameter = f"/storefront-{environment}/sqs/main-queue-url"
        priority_queue_parameter = f"/storefront-{environment}/sqs/priority-queue-url"
        email_queue_parameter = f"/storefront-{environment}/sqs/email-queue-url"
        image_processing_queue_parameter = (
            f"/storefront-{environment}/sqs/image-processing-queue-url"
        )
        order_processing_queue_parameter = (
            f"/storefront-{environment}/sqs/order-processing-queue-url"
        )

        # Environment variables for API service
        api_environment = {
            "NODE_ENV": "production",
            "PORT": "3001",
            "FORCE_UPDATE": "1",
            "DATABASE_URL": database_url,
            "HEALTH_CHECK_PATH": "/v1/api/health",
            "ENVIRONMENT": environment,
            "AWS_REGION": "us-east-1",
            "REDIS_ENABLED": "true",
            "OPENSEARCH_PARAMETER_NAME": opensearch_parameter_name,
            "SQS_MAIN_QUEUE_PARAMETER": main_queue_parameter,
            "SQS_PRIORITY_QUEUE_PARAMETER": priority_queue_parameter,
            "SQS_EMAIL_QUEUE_PARAMETER": email_queue_parameter,
            "SQS_IMAGE_PROCESSING_QUEUE_PARAMETER": image_processing_queue_parameter,
            "SQS_ORDER_PROCESSING_QUEUE_PARAMETER": order_processing_queue_parameter,
        }

        # Secrets configuration (from CloudFormation template)
        api_secrets = {
            "OPENAI_API_KEY": f"/storefront-{environment}/openai-api-key",
            "GEMINI_API_KEY": f"/storefront-{environment}/gemini-api-key",
            "GROK_API": f"/storefront-{environment}/grok-api",
            "OPENROUTER_API": f"/storefront-{environment}/openrouter-api",
            "NEXT_PUBLIC_OPENAI_API_KEY": f"/storefront-{environment}/next-public-openai-api-key",
            "STRIPE_SECRET_KEY": f"/storefront-{environment}/stripe-secret-key",
            "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY": f"/storefront-{environment}/next-public-stripe-publishable-key",
            "STRIPE_WEBHOOK_SECRET": f"/storefront-{environment}/stripe-webhook-secret",
            "NEXT_PUBLIC_GOOGLE_MAPS_API_KEY": f"/storefront-{environment}/next-public-google-maps-api-key",
            "PRINTIFY_API_KEY": f"/storefront-{environment}/printify-api-key",
            "POSTGRES_USER": f"/storefront-{environment}/database/username",
            "POSTGRES_PASSWORD": f"/storefront-{environment}/database/password",
            "POSTGRES_HOST": f"/storefront-{environment}/database/host",
            "POSTGRES_PORT": f"/storefront-{environment}/database/port",
            "POSTGRES_DB": f"/storefront-{environment}/database/name",
        }

        # Use the Fargate service construct for consistency
        fargate_construct = FargateServiceConstruct(
            self,
            "api-service",
            cluster=cluster,
            vpc=vpc,
            container_image=ecs.ContainerImage.from_registry(image_uri),
            container_port=3001,
            environment=api_environment,
            secrets=api_secrets,
            desired_count=desired_count,
            security_groups=(
                [ecs_task_security_group] if ecs_task_security_group else []
            ),
            service_name=service_name,
            opensearch_task_role=opensearch_role,  # Pass the OpenSearch role
            sqs_managed_policy=sqs_managed_policy,  # Pass the SQS managed policy
            cloud_map_options=ecs.CloudMapOptions(
                name=service_name,
                dns_record_type=servicediscovery.DnsRecordType.A,
                dns_ttl=cdk.Duration.seconds(10),
            ),
        )

        # Expose the service from this stack
        self.service = fargate_construct.service
