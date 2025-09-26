import os
import json
import aws_cdk as cdk
from aws_cdk import App, Environment
from infrastructure.scripts.tag_resolver import resolve_tag
from stacks.domain_dns_stack import DomainDnsStack
from stacks.network_stack import NetworkStack
from stacks.shared_stack import SharedStack
from stacks.ecr_stack import ECRStack
from stacks.database_stack import DatabaseStack
from stacks.web_service_stack import WebServiceStack
from stacks.api_service_stack import APIServiceStack
from stacks.iam_stack import IAMStack
from stacks.web_multialb_stack import MultiAlbStack
from stacks.listener_service_stack import ListenerServiceStack
from stacks.dns_worker_service_stack import DNSWorkerServiceStack
from stacks.opensearch_stack import OpenSearchStack
from stacks.sqs_stack import SQSStack
# from stacks.parameters_stack import ParametersStack

app = cdk.App()

env = cdk.Environment(account="156041439702", region="us-east-1")
env_name = app.node.try_get_context("env") or "dev"

try:
    with open("domains.json", "r") as f:
        domains_data = json.load(f)
        domains = domains_data["domains"]
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    print(f"⚠️ Could not read domains.json: {e}")
    domains = []  # or some default value


listener_tag = resolve_tag("listenerTag", "LISTENER_IMAGE_TAG", app, "listener")
dns_worker_tag = resolve_tag("dnsWorkerTag", "DNS_WORKER_IMAGE_TAG", app, "dns-worker")
api_tag = resolve_tag("apiTag", "API_IMAGE_TAG", app, "api")
web_tag = resolve_tag("webTag", "WEB_IMAGE_TAG", app, "web")

# IAM Stack for CI/CD permissions - deploy this first to bootstrap permissions
# iam_stack = IAMStack(app, "StorefrontIAMStack", env=env)

# Network and ECS Cluster
network_stack = NetworkStack(app, "NetworkStack", env=env)
# network_stack.add_dependency(iam_stack)

shared_stack = SharedStack(app, "SharedStack", env=env, vpc=network_stack.vpc)

multi_alb_stack = MultiAlbStack(
    app, f"MultiAlbStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    domains=domains,
    alb_security_group=shared_stack.alb_security_group
)

# Add mail DNS records automatically
# Suppose MultiAlbStack exposes a dict: { "040992.xyz": alb1, "example.com": alb2, ... }
for domain, alb in multi_alb_stack.domain_to_alb.items():
    DomainDnsStack(
        app, f"DomainDnsStack-{domain.replace('.', '-')}",
        env=env,
        domain_name=domain,
        alb=alb,
        mail_server="mail.teeworkflow.com",
        dkim_selector="default",
        dkim_public_key="MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDdmsMArxUA48AxvmG2gm26Qr1lbhtt6r59AMhBMK/TgZLNHug0L8uM6nm12SSxY0kxZyp5cLPbtgN832ReoJ0sW6zZfedfPf1Ak1Z6H9Cxd3wB3zI3Gy8c6PsV9Wt0lYEWHALw2ANjf5Ru0otK3slBUz7yb7AgvUEHb1Bt6+aazQIDAQAB",
        spf_servers=["a:mail.teeworkflow.com"],
        dmarc_rua=f"reports@{domain}",
        dmarc_policy="quarantine"
    )

# App container registries
ecr_stack = ECRStack(
    app, "StorefrontECRStack",
    env=env,
    repository_names=["api", "web", "listener", "dns-worker"]
)

# RDS instance with Secrets Manager
database_stack = DatabaseStack(
    app, f"DatabaseStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    environment=env_name
)

# OpenSearch domain for logging and search (public access)
opensearch_stack = OpenSearchStack(
    app, f"OpenSearchStack-{env_name}",
    env=env,
    environment=env_name
)

# SQS queues for message processing
sqs_stack = SQSStack(
    app, f"SQSStack-{env_name}",
    env=env,
    environment=env_name
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

# Deploy listener service
listener_service = ListenerServiceStack(
    app, f"ListenerServiceStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    cluster=shared_stack.cluster,
    image_uri=f"{ecr_stack.repositories['listener'].repository_uri}:{listener_tag}",
    db_secret=database_stack.secret,
    environment=env_name,
    ecs_task_security_group=shared_stack.ecs_task_sg,
    service_name="listener-service",
    sqs_managed_policy=sqs_stack.sqs_managed_policy
)

# Deploy DNS worker service
dns_worker_service = DNSWorkerServiceStack(
    app, f"DNSWorkerServiceStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    cluster=shared_stack.cluster,
    image_uri=f"{ecr_stack.repositories['dns-worker'].repository_uri}:{dns_worker_tag}",
    environment=env_name,
    ecs_task_security_group=shared_stack.ecs_task_sg,
    service_name="dns-worker-service",
    db_secret=database_stack.secret,
    sqs_managed_policy=sqs_stack.sqs_managed_policy
)

# Deploy API service (internal only)
api_service = APIServiceStack(
    app, f"APIServiceStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    cluster=shared_stack.cluster,
    image_uri=f"{ecr_stack.repositories['api'].repository_uri}:{api_tag}",
    db_secret=database_stack.secret,
    environment=env_name,
    ecs_task_security_group=shared_stack.ecs_task_sg,
    service_name="api-service",
    opensearch_role=opensearch_stack.fargate_opensearch_role,
    sqs_managed_policy=sqs_stack.sqs_managed_policy
)

# Deploy web service (just the ECS service, no ALB binding)
web_service = WebServiceStack(
    app, f"WebServiceStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    cluster=shared_stack.cluster,
    image_uri=f"{ecr_stack.repositories['web'].repository_uri}:{web_tag}",
    db_secret=database_stack.secret,
    environment=env_name,
    ecs_task_security_group=shared_stack.ecs_task_sg,
    service_name="web-service",
    opensearch_role=opensearch_stack.fargate_opensearch_role
)

multi_alb_stack.attach_service(web_service.service, port=3000)

app.synth()