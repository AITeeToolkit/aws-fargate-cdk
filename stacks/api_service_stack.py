from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_servicediscovery as servicediscovery,
    aws_ssm as ssm
)
import aws_cdk as cdk
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
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DATABASE_URL from database instance properties
        database_url = f"postgresql://{db_secret.secret_value_from_json('username').unsafe_unwrap()}:{db_secret.secret_value_from_json('password').unsafe_unwrap()}@{db_secret.secret_value_from_json('host').unsafe_unwrap()}:{db_secret.secret_value_from_json('port').unsafe_unwrap()}/{db_secret.secret_value_from_json('dbname').unsafe_unwrap()}?sslmode=no-verify"

        # Get OpenSearch endpoint from SSM Parameter
        opensearch_endpoint = ssm.StringParameter.value_for_string_parameter(
            self, f"/storefront-{environment}/opensearch/endpoint"
        )

        # Environment variables for API service (from CloudFormation template)
        api_environment = {
            "NODE_ENV": "production",
            "PORT": "3001",
            "FORCE_UPDATE": "1",
            "DATABASE_URL": database_url,
            "HEALTH_CHECK_PATH": "/v1/api/health",
            "AWS_REGION": "us-east-1",
            "OPENSEARCH_ENDPOINT": opensearch_endpoint
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
            "REDIS_URL": f"/storefront-{environment}/redis-url"
        }

        # Use the Fargate service construct for consistency
        fargate_construct = FargateServiceConstruct(
            self, "api-service",
            cluster=cluster,
            vpc=vpc,
            container_image=ecs.ContainerImage.from_registry(image_uri),
            container_port=3001,
            environment=api_environment,
            secrets=api_secrets,
            desired_count=1,
            security_groups=[ecs_task_security_group] if ecs_task_security_group else [],
            service_name=service_name,
            opensearch_task_role=opensearch_role,  # Pass the OpenSearch role
            cloud_map_options=ecs.CloudMapOptions(
                name=service_name,
                dns_record_type=servicediscovery.DnsRecordType.A,
                dns_ttl=cdk.Duration.seconds(10)
            )
        )

        # Expose the service from this stack
        self.service = fargate_construct.service