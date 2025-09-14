#!/usr/bin/env python3

import os
import aws_cdk as cdk
from stacks.network_stack import NetworkStack
from stacks.shared_stack import SharedStack
from stacks.cert_stack import CertStack
from stacks.route53_stack import Route53Stack
from stacks.web_alb_stack import WebAlbStack
from stacks.ecr_stack import ECRStack
from stacks.database_stack import DatabaseStack
from stacks.web_service_stack import WebServiceStack
from stacks.api_service_stack import APIServiceStack
from stacks.iam_stack import IAMStack
# from stacks.parameters_stack import ParametersStack

app = cdk.App()

env = cdk.Environment(account="156041439702", region="us-east-1")
env_name = app.node.try_get_context("env") or "dev"
domains = ["040992.xyz"]

# Get the image tag from environment variable (set by CI/CD) or default to 'latest'
image_tag = os.environ.get("CDK_IMAGE_TAG", "latest")

# IAM Stack for CI/CD permissions - deploy this first to bootstrap permissions
# iam_stack = IAMStack(app, "StorefrontIAMStack", env=env)

# Network and ECS Cluster
network_stack = NetworkStack(app, "StorefrontNetworkStack", env=env)
# network_stack.add_dependency(iam_stack)
shared_stack = SharedStack(app, "StorefrontSharedStack", env=env, vpc=network_stack.vpc)

# Reuse the ALB for all domains (single entry point)
first_domain = domains[0]
cert_stack = CertStack(app, f"CertStack-{first_domain.replace('.', '-')}", env=env, domain_name=first_domain)

web_alb_stack = WebAlbStack(
    app, "StorefrontWebAlbStack",
    env=env,
    vpc=network_stack.vpc,
    cert=cert_stack.cert
)

# Use Route53 + ACM per domain, all pointing to same ALB
for domain in domains:
    Route53Stack(
        app, f"Route53Stack-{domain.replace('.', '-')}",
        env=env,
        domain_name=domain,
        alb=web_alb_stack.alb
    )

# App container registries
ecr_stack = ECRStack(
    app, "StorefrontECRStack",
    env=env,
    repository_names=["api", "web"]
)

# RDS instance with Secrets Manager
database_stack = DatabaseStack(
    app, f"StorefrontDatabaseStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    environment=env_name
)

# Parameters Stack - independent of database stack
# parameters_stack = ParametersStack(
#     app, f"StorefrontParametersStack-{env_name}",
#     env=env,
#     environment=env_name,
#     database_stack=None,
#     cluster=shared_stack.cluster,
#     api_service_name="api-service",
# )

# Deploy API service (internal only)
api_service = APIServiceStack(
    app, f"StorefrontAPIServiceStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    cluster=shared_stack.cluster,
    image_uri=f"{ecr_stack.repositories['api'].repository_uri}:{image_tag}",
    db_secret=database_stack.secret,
    environment=env_name,
    ecs_task_security_group=shared_stack.ecs_task_sg,
    service_name="api-service"
)

# Deploy web service (public-facing)
web_service = WebServiceStack(
    app, f"StorefrontWebServiceStack-{env_name}",
    env=env,
    vpc=network_stack.vpc,
    cluster=shared_stack.cluster,
    listener=web_alb_stack.listener,
    image_uri=f"{ecr_stack.repositories['web'].repository_uri}:{image_tag}",
    db_secret=database_stack.secret,
    environment=env_name,
    ecs_task_security_group=shared_stack.ecs_task_sg,
    service_name="web-service"
)

# THEN attach it in WebAlbStack
web_alb_stack.add_web_service_target(web_service.service)

app.synth()