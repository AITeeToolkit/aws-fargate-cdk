import os
import json
import subprocess
import aws_cdk as cdk
from stacks.network_stack import NetworkStack
from stacks.shared_stack import SharedStack
from stacks.route53_stack import Route53Stack
from stacks.ecr_stack import ECRStack
from stacks.database_stack import DatabaseStack
from stacks.web_service_stack import WebServiceStack
from stacks.api_service_stack import APIServiceStack
from stacks.iam_stack import IAMStack
from stacks.web_multialb_stack import MultiAlbStack
from stacks.listener_service_stack import ListenerServiceStack
from stacks.opensearch_stack import OpenSearchStack
# from stacks.parameters_stack import ParametersStack

app = cdk.App()

env = cdk.Environment(account="156041439702", region="us-east-1")
env_name = app.node.try_get_context("env") or "dev"

# Update domains from database before deployment
print("🔄 Updating domains from database...")
result = subprocess.run(["python", "scripts/update_domains.py"], 
                       capture_output=True, text=True, cwd=os.getcwd())
if result.returncode != 0:
    print(f"❌ Error updating domains:")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
    print(f"Return code: {result.returncode}")
    exit(1)
else:
    print(f"✅ Domains updated successfully")
    print(result.stdout.strip())

with open("domains.json") as f:
    domains = json.load(f)["domains"]

# Helper to resolve image tag priority: CDK context -> env var -> "latest"
def resolve_tag(context_key: str, env_var: str) -> str:
    return (
        app.node.try_get_context(context_key)
        or os.environ.get(env_var)
        or "latest"
    )

listener_tag = resolve_tag("listenerTag", "LISTENER_IMAGE_TAG")
api_tag = resolve_tag("apiTag", "API_IMAGE_TAG")
web_tag = resolve_tag("webTag", "WEB_IMAGE_TAG")

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
    repository_names=["api", "web", "listener"]
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

# Parameters stack for SSM parameters
parameters_stack = ParametersStack(
    app, f"ParametersStack-{env_name}",
    env=env,
    environment=env_name,
    cluster=shared_stack.cluster,
    namespace=shared_stack.cluster.default_cloud_map_namespace,
    api_service_name="api-service"  # This should match your service name
)

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
    service_name="listener-service"
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
    opensearch_role=opensearch_stack.fargate_opensearch_role
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