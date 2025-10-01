#!/usr/bin/env python3
import json
import os

import aws_cdk as cdk

from scripts.tag_resolver import resolve_tag
from stacks.api_service_stack import APIServiceStack
from stacks.certificate_stack import CertificateStack
from stacks.database_stack import DatabaseStack
from stacks.dns_worker_service_stack import DNSWorkerServiceStack
from stacks.domain_dns_stack import DomainDnsStack
from stacks.ecr_stack import ECRStack
from stacks.listener_service_stack import ListenerServiceStack
from stacks.network_stack import NetworkStack
from stacks.opensearch_stack import OpenSearchStack
from stacks.shared_stack import SharedStack
from stacks.sqs_stack import SQSStack
from stacks.web_multialb_stack import MultiAlbStack
from stacks.web_service_stack import WebServiceStack

# from stacks.parameters_stack import ParametersStack


app = cdk.App()

env = cdk.Environment(account="156041439702", region="us-east-1")

# Get environment from context or deploy all environments
env_name = app.node.try_get_context("env") or os.getenv("ENVIRONMENT", "dev")
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
        "ecs_desired_count": 1,
        "enable_deletion_protection": False,
    },
    "staging": {
        "db_multi_az": False,
        "db_instance_class": "db.t3.micro",
        "ecs_desired_count": 1,
        "enable_deletion_protection": False,
    },
    "prod": {
        "db_multi_az": False,  # Multi-AZ for production
        "db_instance_class": "db.t3.micro",
        "ecs_desired_count": 1,
        "enable_deletion_protection": True,
    },
}

# Load base domains from domains.json
try:
    with open("domains.json", "r") as f:
        domains_data = json.load(f)
        base_domains = domains_data["domains"]
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    print(f"⚠️ Could not read domains.json: {e}")
    base_domains = []


# Function to add environment prefix to domains
def get_env_domains(base_domains: list[str], environment: str) -> list[str]:
    """
    Add environment prefix to domains:
    - dev: dev.domain.com
    - staging: staging.domain.com
    - prod: domain.com (no prefix)
    """
    if environment == "prod":
        return base_domains  # No prefix for prod
    else:
        return [f"{environment}.{domain}" for domain in base_domains]


listener_tag = resolve_tag("listenerTag", "LISTENER_IMAGE_TAG", app, "listener")
dns_worker_tag = resolve_tag("dnsWorkerTag", "DNS_WORKER_IMAGE_TAG", app, "dns-worker")
api_tag = resolve_tag("apiTag", "API_IMAGE_TAG", app, "api")
web_tag = resolve_tag("webTag", "WEB_IMAGE_TAG", app, "web")

# Shared resources (VPC, ALB, ECS cluster) - only create once
# IAM Stack for CI/CD permissions - deploy this first to bootstrap permissions
# iam_stack = IAMStack(app, "StorefrontIAMStack", env=env)

# Network and ECS Cluster
network_stack = NetworkStack(app, "NetworkStack", env=env)
# network_stack.add_dependency(iam_stack)

shared_stack = SharedStack(app, "SharedStack", env=env, vpc=network_stack.vpc)

# App container registries - only create one time
ecr_stack = ECRStack(
    app,
    "StorefrontECRStack",
    env=env,
    repository_names=["api", "web", "listener", "dns-worker"],
)

# Create shared wildcard certificates (one per root domain, shared across all environments)
certificate_stack = CertificateStack(
    app,
    "SharedCertificateStack",
    env=env,
    domains=base_domains,
)

# Deploy stacks for each environment
for current_env in environments_to_deploy:
    current_config = env_config.get(current_env, env_config["dev"])
    print(
        f"🛠️ Creating stacks for {current_env} environment with config: {current_config}"
    )

    # Get environment-specific domains (dev.domain.com, staging.domain.com, or domain.com for prod)
    env_domains = get_env_domains(base_domains, current_env)
    print(
        f"  📋 Domains for {current_env}: {env_domains[:3]}..."
        if len(env_domains) > 3
        else f"  📋 Domains for {current_env}: {env_domains}"
    )

    # Multi-ALB stack for this environment (using shared certificates)
    multi_alb_stack = MultiAlbStack(
        app,
        f"MultiAlbStack-{current_env}",
        env=env,
        vpc=network_stack.vpc,
        domains=env_domains,
        alb_security_group=shared_stack.alb_security_group,
        environment=current_env,
        certificate_arns=certificate_stack.certificates,
    )

    # Add mail DNS records automatically for this environment
    for domain, alb in multi_alb_stack.domain_to_alb.items():
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
    )

    # OpenSearch domain for logging and search for this environment
    opensearch_stack = OpenSearchStack(
        app,
        f"OpenSearchStack-{current_env}",
        env=env,
        environment=current_env,
    )

    # SQS queues for message processing for this environment
    sqs_stack = SQSStack(
        app, f"SQSStack-{current_env}", env=env, environment=current_env
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

    # Deploy listener service for this environment
    listener_service = ListenerServiceStack(
        app,
        f"ListenerServiceStack-{current_env}",
        env=env,
        vpc=network_stack.vpc,
        cluster=shared_stack.cluster,
        image_uri=f"{ecr_stack.repositories['listener'].repository_uri}:{listener_tag}",
        db_secret=database_stack.secret,
        environment=current_env,
        ecs_task_security_group=shared_stack.ecs_task_sg,
        service_name=f"listener-service-{current_env}",
        sqs_managed_policy=sqs_stack.sqs_managed_policy,
    )

    # Deploy DNS worker service for this environment
    dns_worker_service = DNSWorkerServiceStack(
        app,
        f"DNSWorkerServiceStack-{current_env}",
        env=env,
        vpc=network_stack.vpc,
        cluster=shared_stack.cluster,
        image_uri=f"{ecr_stack.repositories['dns-worker'].repository_uri}:{dns_worker_tag}",
        environment=current_env,
        ecs_task_security_group=shared_stack.ecs_task_sg,
        service_name=f"dns-worker-service-{current_env}",
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
