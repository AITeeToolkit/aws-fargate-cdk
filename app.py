#!/usr/bin/env python3

import os
import json
import aws_cdk as cdk
from stacks.network_stack import NetworkStack
from stacks.shared_stack import SharedStack
from stacks.route53_stack import Route53Stack
from stacks.ecr_stack import ECRStack
from stacks.database_stack import DatabaseStack
from stacks.web_service_stack import WebServiceStack
from stacks.api_service_stack import APIServiceStack
from stacks.domain_updater_stack import DomainUpdaterStack
from stacks.iam_stack import IAMStack
from stacks.web_multialb_stack import MultiAlbStack
# from stacks.parameters_stack import ParametersStack

app = cdk.App()

env = cdk.Environment(account="156041439702", region="us-east-1")
env_name = app.node.try_get_context("env") or "dev"

with open("domains.json") as f:
    domains = json.load(f)["domains"]

# Get the image tag from environment variable (set by CI/CD) or default to 'latest'
image_tag = os.environ.get("CDK_IMAGE_TAG", "latest")

# IAM Stack for CI/CD permissions - deploy this first to bootstrap permissions
# iam_stack = IAMStack(app, "StorefrontIAMStack", env=env)

# Network and ECS Cluster
network_stack = NetworkStack(app, "NetworkStack", env=env)
# network_stack.add_dependency(iam_stack)

shared_stack = SharedStack(app, "SharedStack", env=env, vpc=network_stack.vpc)

multi_alb_stack = MultiAlbStack(
    app, "MultiAlbStack",
    env=env,
    vpc=network_stack.vpc,
    domains=domains,
    alb_security_group=shared_stack.alb_security_group
)

# Suppose MultiAlbStack exposes a dict: { "040992.xyz": alb1, "example.com": alb2, ... }
for domain, alb in multi_alb_stack.domain_to_alb.items():
    Route53Stack(
        app, f"Route53Stack-{domain.replace('.', '-')}",
        env=env,
        domain_name=domain,
        alb=alb
    )

# App container registries
ecr_stack = ECRStack(
    app, "StorefrontECRStack",
    env=env,
    repository_names=["api", "web", "listener", "domain-updater"]
)

# RDS instance with Secrets Manager
database_stack = DatabaseStack(
    app, f"DatabaseStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    environment=env_name
)

# Parameters Stack - independent of database stack
# parameters_stack = ParametersStack(
#     app, f"ParametersStack-{env_name}",
#     env=env,
#     environment=env_name,
#     cluster=shared_stack.cluster,
#     api_service_name="api-service",
#     namespace=shared_stack.cluster.default_cloud_map_namespace
# )

# Deploy API service (internal only)
api_service = APIServiceStack(
    app, f"APIServiceStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    cluster=shared_stack.cluster,
    image_uri=f"{ecr_stack.repositories['api'].repository_uri}:{image_tag}",
    db_secret=database_stack.secret,
    environment=env_name,
    ecs_task_security_group=shared_stack.ecs_task_sg,
    service_name="api-service"
)


# Deploy web service (just the ECS service, no ALB binding)
web_service = WebServiceStack(
    app, f"WebServiceStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    cluster=shared_stack.cluster,
    image_uri=f"{ecr_stack.repositories['web'].repository_uri}:{image_tag}",
    db_secret=database_stack.secret,
    environment=env_name,
    ecs_task_security_group=shared_stack.ecs_task_sg,
    service_name="web-service"
)

# Domain updater task (runs on-demand via GitHub Actions)
domain_updater = DomainUpdaterStack(
    app, f"DomainUpdaterStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    cluster=shared_stack.cluster,
    image_uri=f"{ecr_stack.repositories['domain-updater'].repository_uri}:{image_tag}",
    db_secret=database_stack.secret,
    environment=env_name,
    ecs_task_security_group=shared_stack.ecs_task_sg,
    service_name="domain-updater"
)

multi_alb_stack.attach_service(web_service.service, port=3000)

app.synth()