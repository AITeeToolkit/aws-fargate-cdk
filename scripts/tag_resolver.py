#!/usr/bin/env python3
import os
import subprocess


def resolve_tag(context_key: str, env_var: str, app_context, service_name: str = None) -> str:
    """
    Resolve a tag with clear priorities:
    1. CDK context (from --context)
    2. Environment variable
    3. Git tags (service-specific: control-plane-v*, api-v*, web-v*, go-dns-v*)
    4. Fallback to 'latest'
    """
    # Priority 1: CDK context
    context_tag = app_context.node.try_get_context(context_key)
    if context_tag and context_tag != "skip":
        print(f"🏷️  Using context tag for {context_key}: {context_tag}")
        return context_tag

    # Priority 2: Environment variable
    env_tag = os.environ.get(env_var)
    if env_tag and env_tag != "skip":
        print(f"🏷️  Using environment tag for {context_key}: {env_tag}")
        return env_tag

    # Priority 3: Git tags (only print if used)
    try:
        if service_name == "control-plane":
            # control-plane: use local git tags from this repo
            prefix = f"{service_name}-v*"
            result = subprocess.run(["git", "tag", "-l", prefix], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                tags = [t.strip() for t in result.stdout.splitlines()]
                latest_tag = sorted(
                    tags,
                    key=lambda s: [int(p) for p in s.split("-v")[-1].split(".")],
                    reverse=True,
                )[0]
                version = latest_tag.replace(f"{service_name}-", "")
                print(f"🏷️  Using local git tag for {context_key}: {version}")
                return version
        elif service_name == "go-dns":
            # go-dns: fetch from go-dns repository
            print(f"🔍 Fetching latest {service_name} tag from go-dns repository...")
            result = subprocess.run(
                [
                    "git",
                    "ls-remote",
                    "--tags",
                    "https://github.com/AITeeToolkit/go-dns.git",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Parse remote tags and find the latest for this service
                remote_tags = []
                for line in result.stdout.strip().split("\n"):
                    if f"{service_name}-v" in line:
                        tag = line.split("/")[-1]  # Extract tag name from refs/tags/go-dns-v1.0.0
                        remote_tags.append(tag)

                if remote_tags:
                    latest_tag = sorted(
                        remote_tags,
                        key=lambda s: [int(p) for p in s.split("-v")[-1].split(".")],
                        reverse=True,
                    )[0]
                    version = latest_tag.replace(f"{service_name}-", "")
                    print(f"🏷️  Using remote git tag for {context_key}: {version}")
                    return version
        elif service_name in ["api", "web"]:
            # Remote services: fetch from storefront-cdk repository
            print(f"🔍 Fetching latest {service_name} tag from storefront-cdk repository...")
            result = subprocess.run(
                [
                    "git",
                    "ls-remote",
                    "--tags",
                    "https://github.com/AITeeToolkit/storefront-cdk.git",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Parse remote tags and find the latest for this service
                remote_tags = []
                for line in result.stdout.strip().split("\n"):
                    if f"{service_name}-v" in line:
                        tag = line.split("/")[-1]  # Extract tag name from refs/tags/api-v1.6.1
                        remote_tags.append(tag)

                if remote_tags:
                    latest_tag = sorted(
                        remote_tags,
                        key=lambda s: [int(p) for p in s.split("-v")[-1].split(".")],
                        reverse=True,
                    )[0]
                    version = latest_tag.replace(f"{service_name}-", "")
                    print(f"🏷️  Using remote git tag for {context_key}: {version}")
                    return version

    except Exception as e:
        print(f"⚠️  Error resolving tag for {service_name}: {e}")

    # Priority 4: Fallback
    print(f"🏷️  Fallback: using 'latest' for {context_key}")
    return "latest"
