import os
import json
import subprocess
from aws_cdk import App, Environment
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

try:
    with open("domains.json", "r") as f:
        domains_data = json.load(f)
        domains = domains_data["domains"]
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    print(f"⚠️ Could not read domains.json: {e}")
    domains = []  # or some default value

# Helper to resolve image tag priority: CDK context -> env var -> smart default
def resolve_tag(context_key: str, env_var: str) -> str:
    # Priority 1: CDK context (from pipeline)
    context_tag = app.node.try_get_context(context_key)
    if context_tag and context_tag != "skip":
        print(f"🏷️  Using context tag for {context_key}: {context_tag}")
        return context_tag
    
    # Priority 2: Environment variable (from pipeline)
    env_tag = os.environ.get(env_var)
    if env_tag and env_tag != "skip":
        print(f"🏷️  Using env tag for {env_var}: {env_tag}")
        return env_tag
    
    # Priority 3: Smart default based on git branch
    try:
        import subprocess
        # Get current git branch
        branch_result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                     capture_output=True, text=True, cwd=os.getcwd())
        if branch_result.returncode == 0:
            branch = branch_result.stdout.strip()
            
            if branch == "main":
                # On main branch, try to get latest semantic release tag
                tag_result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                                          capture_output=True, text=True, cwd=os.getcwd())
                if tag_result.returncode == 0:
                    latest_tag = tag_result.stdout.strip()
                    print(f"🏷️  Using semantic release tag for {context_key}: {latest_tag}")
                    return latest_tag
                else:
                    print(f"🏷️  No semantic release tag found, using latest for {context_key}")
                    return "latest"
            else:
                # On feature branch, use branch-sha format
                sha_result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                          capture_output=True, text=True, cwd=os.getcwd())
                if sha_result.returncode == 0:
                    short_sha = sha_result.stdout.strip()
                    # Clean branch name (replace non-alphanumeric with hyphens)
                    clean_branch = ''.join(c if c.isalnum() else '-' for c in branch).lower()
                    branch_tag = f"{clean_branch}-{short_sha}"
                    print(f"🏷️  Using branch tag for {context_key}: {branch_tag}")
                    return branch_tag
    except Exception as e:
        print(f"⚠️  Could not determine git context: {e}")
    
    # Fallback to latest
    print(f"🏷️  Using fallback tag for {context_key}: latest")
    return "latest"

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