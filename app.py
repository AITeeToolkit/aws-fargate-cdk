#!/usr/bin/env python3
import json
import os

import aws_cdk as cdk

from scripts.tag_resolver import resolve_tag
from stacks.api_service_stack import APIServiceStack
from stacks.certificate_stack import CertificateStack
from stacks.control_plane_service_stack import ControlPlaneServiceStack
from stacks.database_stack import DatabaseStack
from stacks.domain_dns_stack import DomainDnsStack
from stacks.ecr_stack import ECRStack

# Listener service removed - external systems publish directly to SNS
from stacks.network_stack import NetworkStack
from stacks.opensearch_stack import OpenSearchStack
from stacks.redis_stack import RedisStack
from stacks.shared_stack import SharedStack
from stacks.sqs_stack import SQSStack
from stacks.web_multialb_stack import MultiAlbStack
from stacks.web_service_stack import WebServiceStack

# from stacks.github_runner_stack import GitHubRunnerStack


# from stacks.parameters_stack import ParametersStack


app = cdk.App()

env = cdk.Environment(account="156041439702", region="us-east-1")

# Get environment from context or deploy all environments
env_name = app.node.try_get_context("env") or "dev"
deploy_all = app.node.try_get_context("deploy-all") or False

if deploy_all:
    environments_to_deploy = ["dev", "staging", "prod"]
    print("🚀 Deploying ALL environments: dev, staging, prod")
else:
    environments_to_deploy = [env_name]
    print(f"🚀 Deploying to {env_name} environment")

# Environment-specific configuration
env_config = {
    "dev": {
        "db_multi_az": False,
        "db_instance_class": "db.t3.micro",
        "db_publicly_accessible": True,  # Allow direct access for development
        "ecs_desired_count": 1,
        "enable_deletion_protection": False,
        "redis_max_storage_gb": 1,  # 1 GB minimum (CloudFormation only supports GB)
        "redis_max_ecpu": 3000,
        "redis_snapshot_retention": 1,
    },
    "staging": {
        "db_multi_az": False,
        "db_instance_class": "db.t3.micro",
        "db_publicly_accessible": True,  # Private for staging
        "ecs_desired_count": 1,
        "enable_deletion_protection": False,
        "redis_max_storage_gb": 1,  # 1 GB minimum (CloudFormation only supports GB)
        "redis_max_ecpu": 5000,
        "redis_snapshot_retention": 7,
    },
    "prod": {
        "db_multi_az": False,  # Multi-AZ for production
        "db_instance_class": "db.t3.micro",
        "db_publicly_accessible": True,  # Private for production
        "ecs_desired_count": 1,
        "enable_deletion_protection": True,
        "redis_max_storage_gb": 1,  # 1 GB minimum (CloudFormation only supports GB)
        "redis_max_ecpu": 10000,
        "redis_snapshot_retention": 7,
    },
}


# Function to load domains for a specific environment from database
def load_domains_for_env(environment: str):
    """Load domains directly from database for this environment"""
    # Get database connection parameters from SSM Parameter Store
    import boto3
    import psycopg2

    ssm = boto3.client("ssm", region_name="us-east-1")

    try:
        # Read database connection parameters from SSM
        db_host = ssm.get_parameter(Name=f"/storefront-{environment}/database/host")["Parameter"][
            "Value"
        ]
        db_name = ssm.get_parameter(Name=f"/storefront-{environment}/database/name")["Parameter"][
            "Value"
        ]
        db_user = ssm.get_parameter(Name=f"/storefront-{environment}/database/username")[
            "Parameter"
        ]["Value"]
        db_password = ssm.get_parameter(
            Name=f"/storefront-{environment}/database/password", WithDecryption=True
        )["Parameter"]["Value"]

        # Connect to database
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=10,
        )

        cursor = conn.cursor()
        # Only load active domains (active_status = 'Y')
        cursor.execute("SELECT full_url FROM domains WHERE active_status = 'Y'")

        active_domains = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        print(f"  📊 Loaded {len(active_domains)} active domains from database")
        return active_domains, active_domains

    except Exception as e:
        print(f"⚠️  Failed to read domains from database for {environment}: {e}")
        print(f"   Continuing with empty domain list for local development")
        return [], []


# Listener service removed - no longer needed
control_plane_tag = resolve_tag("controlPlaneTag", "CONTROL_PLANE_IMAGE_TAG", app, "control-plane")
api_tag = resolve_tag("apiTag", "API_IMAGE_TAG", app, "api")
web_tag = resolve_tag("webTag", "WEB_IMAGE_TAG", app, "web")

# Shared resources (VPC, ALB, ECS cluster) - only create once
# IAM Stack for CI/CD permissions - deploy this first to bootstrap permissions
# iam_stack = IAMStack(app, "StorefrontIAMStack", env=env)

# Network and ECS Cluster
network_stack = NetworkStack(app, "NetworkStack", env=env)
# network_stack.add_dependency(iam_stack)

# GitHub Actions self-hosted runner (shared across all environments for database access)
# github_runner_stack = GitHubRunnerStack(
#     app,
#     "GitHubRunnerStack",
#     vpc=network_stack.vpc,
#     env=env,
# )

shared_stack = SharedStack(app, "SharedStack", env=env, vpc=network_stack.vpc)

# App container registries - only create one time
ecr_stack = ECRStack(
    app,
    "StorefrontECRStack",
    env=env,
    repository_names=["api", "web", "control-plane"],
)

# Deploy stacks for each environment
for current_env in environments_to_deploy:
    current_config = env_config.get(current_env, env_config["dev"])
    print(f"🛠️ Creating stacks for {current_env} environment with config: {current_config}")

    # Load domains for this specific environment
    cert_domains, active_domains = load_domains_for_env(current_env)

    print(
        f"  📋 Domains for {current_env}: {active_domains[:3]}..."
        if len(active_domains) > 3
        else f"  📋 Domains for {current_env}: {active_domains}"
    )

    # Create per-domain certificate stacks for this environment
    # Only create for domains that have hosted zones (Control Plane worker creates these first)
    # Each environment gets its own certificate (no wildcards)
    certificate_arns = {}

    # Check which domains have hosted zones
    import boto3

    route53 = boto3.client("route53", region_name="us-east-1")

    for domain in cert_domains:
        # Check if hosted zone exists for this domain
        try:
            zones = route53.list_hosted_zones_by_name(DNSName=domain, MaxItems="1")
            zone_exists = False
            if zones.get("HostedZones"):
                zone = zones["HostedZones"][0]
                # Exact match (not subdomain)
                if zone["Name"].rstrip(".") == domain:
                    zone_exists = True

            if not zone_exists:
                print(
                    f"  ⏭️  Skipping {domain} - hosted zone not found (Control Plane will create it)"
                )
                continue

        except Exception as e:
            print(f"  ⚠️  Error checking zone for {domain}: {e}")
            continue

        # Zone exists, create certificate stack
        stack_name = f"CertificateStack-{current_env}-{domain.replace('.', '-')}"
        cert_stack = CertificateStack(
            app,
            stack_name,
            env=env,
            domain=domain,
            environment=current_env,
        )
        # Store ARN for active domains only
        if domain in active_domains:
            certificate_arns[domain] = cert_stack.certificate_arn
        print(f"  📜 Created certificate stack for {domain} in {current_env}")

    multi_alb_stack = MultiAlbStack(
        app,
        f"MultiAlbStack-{current_env}",
        env=env,
        vpc=network_stack.vpc,
        domains=active_domains,
        alb_security_group=shared_stack.alb_security_group,
        environment=current_env,
        certificate_arns=certificate_arns,
    )

    # Add mail DNS records automatically for this environment
    for domain, alb in multi_alb_stack.domain_to_alb.items():
        # Create DNS stack - from_lookup() will handle zone existence check
        print(f"  📧 Creating DNS stack for {domain} in {current_env}")
        DomainDnsStack(
            app,
            f"DomainDnsStack-{current_env}-{domain.replace('.', '-')}",
            env=env,
            domain_name=domain,
            alb=alb,
            mail_server="mail.teeworkflow.com",
            dkim_selector="default",
            dkim_public_key="MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDdmsMArxUA48AxvmG2gm26Qr1lbhtt6r59AMhBMK/TgZLNHug0L8uM6nm12SSxY0kxZyp5cLPbtgN832ReoJ0sW6zZfedfPf1Ak1Z6H9Cxd3wB3zI3Gy8c6PsV9Wt0lYEWHALw2ANjf5Ru0otK3slBUz7yb7AgvUEHb1Bt6+aazQIDAQAB",
            spf_servers=["a:mail.teeworkflow.com"],
            dmarc_rua=f"reports@{domain}",
            dmarc_policy="quarantine",
        )
        print(f"  📧 Created DNS stack for {domain} in {current_env}")

    # RDS instance with Secrets Manager for this environment
    database_stack = DatabaseStack(
        app,
        f"DatabaseStack-{current_env}",
        env=env,
        vpc=network_stack.vpc,
        environment=current_env,
        multi_az=current_config["db_multi_az"],
        instance_class=current_config["db_instance_class"],
        deletion_protection=current_config["enable_deletion_protection"],
        publicly_accessible=current_config["db_publicly_accessible"],
    )

    # OpenSearch domain for logging and search for this environment
    opensearch_stack = OpenSearchStack(
        app,
        f"OpenSearchStack-{current_env}",
        env=env,
        environment=current_env,
    )

    # SQS queues for message processing for this environment
    sqs_stack = SQSStack(app, f"SQSStack-{current_env}", env=env, environment=current_env)

    # Redis Serverless for caching for this environment
    redis_stack = RedisStack(
        app,
        f"RedisStack-{current_env}",
        env=env,
        vpc=network_stack.vpc,
        environment=current_env,
        max_storage_gb=current_config["redis_max_storage_gb"],
        max_ecpu=current_config["redis_max_ecpu"],
        snapshot_retention=current_config["redis_snapshot_retention"],
    )

    # Parameters stack for SSM parameters
    # parameters_stack = ParametersStack(
    #     app, f"ParametersStack-{env_name}",
    #     env=env,
    #     environment=env_name,
    #     cluster=shared_stack.cluster,
    #     namespace=shared_stack.cluster.default_cloud_map_namespace,
    #     api_service_name="api-service"  # This should match your service name
    # )

    # Listener service removed - external systems publish directly to SNS topic
    # SNS topic → SQS queues → Control plane workers handle everything

    # Deploy control plane service for this environment
    control_plane_service = ControlPlaneServiceStack(
        app,
        f"ControlPlaneServiceStack-{current_env}",
        env=env,
        vpc=network_stack.vpc,
        cluster=shared_stack.cluster,
        image_uri=f"{ecr_stack.repositories['control-plane'].repository_uri}:{control_plane_tag}",
        environment=current_env,
        ecs_task_security_group=shared_stack.ecs_task_sg,
        service_name=f"control-plane-service-{current_env}",
        db_secret=database_stack.secret,
        sqs_managed_policy=sqs_stack.sqs_managed_policy,
        desired_count=current_config["ecs_desired_count"],
    )

    # Deploy API service (internal only) for this environment
    api_service = APIServiceStack(
        app,
        f"APIServiceStack-{current_env}",
        env=env,
        vpc=network_stack.vpc,
        cluster=shared_stack.cluster,
        image_uri=f"{ecr_stack.repositories['api'].repository_uri}:{api_tag}",
        db_secret=database_stack.secret,
        environment=current_env,
        ecs_task_security_group=shared_stack.ecs_task_sg,
        service_name=f"api-service-{current_env}",
        opensearch_role=opensearch_stack.fargate_opensearch_role,
        desired_count=current_config["ecs_desired_count"],
    )

    # Deploy web service for this environment
    web_service = WebServiceStack(
        app,
        f"WebServiceStack-{current_env}",
        env=env,
        vpc=network_stack.vpc,
        cluster=shared_stack.cluster,
        image_uri=f"{ecr_stack.repositories['web'].repository_uri}:{web_tag}",
        db_secret=database_stack.secret,
        environment=current_env,
        ecs_task_security_group=shared_stack.ecs_task_sg,
        service_name=f"web-service-{current_env}",
        opensearch_role=opensearch_stack.fargate_opensearch_role,
        desired_count=current_config["ecs_desired_count"],
    )

    # Attach web service to ALB with host-based routing
    multi_alb_stack.attach_service(
        service=web_service.service,
        port=3000,
    )

app.synth()
