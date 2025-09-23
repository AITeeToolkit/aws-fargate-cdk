from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_servicediscovery as servicediscovery,
    Duration,
)
from constructs import Construct
from cdk_constructs.fargate_service_construct import FargateServiceConstruct


class WebServiceStack(Stack):
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
        # opensearch_role: iam.IRole = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment variables for web service
        web_environment = {
            "NODE_ENV": "production",
            "PORT": "3000",
            "MULTI_TENANT": "true",
            "TENANT_RESOLUTION": "full_domain",
            "DEFAULT_TENANT": "default",
            "ALLOW_INTERNAL_IPS": "true",
            "TRUST_PROXY": "true",
            "INTERNAL_IP_RANGES": "10.0.0.0/16,172.16.0.0/12,192.168.0.0/16",
            "HEALTH_CHECK_PATH": "/health",
            "SKIP_TENANT_RESOLUTION_FOR_HEALTH": "true",
            "HEALTH_CHECK_BYPASS_TENANT": "true",
            "AWS_REGION": "us-east-1"
        }

        # Secrets (extend this if you want to pass db_secret, etc.)
        web_secrets = {
            "API_URL": f"/storefront-{environment}/api/url",
            "API_BASE_URL": f"/storefront-{environment}/api/base-url", 
            "NEXT_PUBLIC_API_BASE_URL": f"/storefront-{environment}/api/base-url",
            "STRIPE_SECRET_KEY": f"/storefront-{environment}/stripe-secret-key",
            "NEXT_PUBLIC_GOOGLE_MAPS_API_KEY": f"/storefront-{environment}/next-public-google-maps-api-key",
            "GEMINI_API_KEY": f"/storefront-{environment}/gemini-api-key",
            "GROK_API": f"/storefront-{environment}/grok-api",
            "NEXT_PUBLIC_OPENAI_API_KEY": f"/storefront-{environment}/next-public-openai-api-key",
            "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY": f"/storefront-{environment}/next-public-stripe-publishable-key",
            "OPENAI_API_KEY": f"/storefront-{environment}/openai-api-key",
            "OPENROUTER_API": f"/storefront-{environment}/openrouter-api",
            "PRINTIFY_API_KEY": f"/storefront-{environment}/printify-api-key",
            "STRIPE_WEBHOOK_SECRET": f"/storefront-{environment}/stripe-webhook-secret",
            "AWS_ACCESS_KEY_ID": f"/storefront-{environment}/route53/AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY": f"/storefront-{environment}/route53/AWS_SECRET_ACCESS_KEY",
            "POSTGRES_USER": f"/storefront-{environment}/database/username",
            "POSTGRES_PASSWORD": f"/storefront-{environment}/database/password",
            "OPENSEARCH_ENDPOINT": f"/storefront-{environment}/opensearch/endpoint"
        }

        # Define Fargate service (no ALB attachment here)
        fargate_construct = FargateServiceConstruct(
            self,
            "web-service",
            cluster=cluster,
            vpc=vpc,
            container_image=ecs.ContainerImage.from_registry(image_uri),
            container_port=3000,
            environment=web_environment,
            secrets=web_secrets,
            desired_count=1,
            security_groups=[ecs_task_security_group] if ecs_task_security_group else [],
            service_name=service_name,
            cloud_map_options=ecs.CloudMapOptions(
                name=service_name,
                dns_record_type=servicediscovery.DnsRecordType.A,
                dns_ttl=Duration.seconds(10),
            ),
        )

        # Expose ECS service so other stacks can attach it
        self.service = fargate_construct.service