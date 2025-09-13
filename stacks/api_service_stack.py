from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy
)
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
        ecs_task_security_group: ec2.ISecurityGroup = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment variables for API service (from CloudFormation template)
        api_environment = {
            "NODE_ENV": "production",
            "PORT": "3001",
            "FORCE_UPDATE": "1"
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
            "REDIS_URL": f"/storefront-{environment}/redis-url",
            "POSTGRES_DB": f"/storefront-{environment}/database/name",
            "DATABASE_URL": f"/storefront-{environment}/database/url"
        }

        # Use the Fargate service construct for consistency
        fargate_construct = FargateServiceConstruct(
            self, "APIService",
            cluster=cluster,
            vpc=vpc,
            container_image=ecs.ContainerImage.from_registry(image_uri),
            listener=None,  # API service is internal, no ALB needed
            container_port=3001,
            environment=api_environment,
            secrets=api_secrets,
            desired_count=2,
            security_groups=[ecs_task_security_group] if ecs_task_security_group else []
        )

        # Expose the service from this stack
        self.service = fargate_construct.service