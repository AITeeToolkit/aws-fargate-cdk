#!/usr/bin/env python3
import os
import subprocess
from typing import Optional, List


def resolve_tag(context_key: str, env_var: str, app_context,
                service_name: str = None) -> str:
    """
    Resolve a tag with clear priorities:
    1. CDK context
    2. Environment variable
    3. Service-specific tags (listener/dns-worker use prefixed tags, api/web use repo tags)
    4. Fallback to 'latest'
    """
    # Priority 1: Context
    context_tag = app_context.node.try_get_context(context_key)
    if context_tag and context_tag != "skip":
        print(f"🏷️  Using context tag for {context_key}: {context_tag}")
        return context_tag

    # Priority 2: Env var
    env_tag = os.environ.get(env_var)
    if env_tag and env_tag != "skip":
        print(f"🏷️  Using environment tag for {context_key}: {env_tag}")
        return env_tag

    # Priority 3: Service-specific
    try:
        if service_name in ["listener", "dns-worker"]:
            # Look for prefixed tags locally
            result = subprocess.run(
                ["git", "tag", "-l", f"{service_name}-v*"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                tags = [t.strip() for t in result.stdout.splitlines()]
                latest_tag = sorted(tags, reverse=True)[0]
                version = latest_tag.replace(f"{service_name}-", "")
                print(f"🏷️  Using latest {service_name} tag for {context_key}: {version}")
                return version

        if service_name in ["api", "web"]:
            # Use repo-wide semantic-release tag
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                version = result.stdout.strip()
                print(f"🏷️  Using repository tag for {context_key}: {version}")
                return version

    except Exception as e:
        print(f"⚠️  Error resolving tag for {service_name}: {e}")

    # Fallback
    print(f"🏷️  Fallback: using 'latest' for {context_key}")
    return "latest"