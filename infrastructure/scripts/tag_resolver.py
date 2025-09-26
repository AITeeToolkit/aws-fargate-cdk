#!/usr/bin/env python3
"""
Simple tag resolver - no complex logic, just clear priorities
"""
import os
import subprocess
from typing import Optional, List


def resolve_tag(context_key: str, env_var: str, app_context, service_files: Optional[List[str]] = None, service_name: str = None) -> str:
    """
    Simple tag resolution with clear priorities:
    1. CDK context (from deployment)
    2. Environment variable (from deployment) 
    3. Latest service tag (from git)
    4. Fallback to latest repository tag
    """
    
    # Priority 1: CDK context (deployment)
    context_tag = app_context.node.try_get_context(context_key)
    if context_tag and context_tag != "skip":
        print(f"🏷️  Using context tag for {context_key}: {context_tag}")
        return context_tag

    # Priority 2: Environment variable (deployment)
    env_tag = os.environ.get(env_var)
    if env_tag and env_tag != "skip":
        print(f"🏷️  Using environment tag for {context_key}: {env_tag}")
        return env_tag
    
    # Priority 3: Find latest service tag
    if service_name:
        try:
            # For listener/dns-worker, use local repository tags
            if service_name in ['listener', 'dns-worker']:
                result = subprocess.run(['git', 'tag', '-l', f'{service_name}-v*'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    tags = [tag.strip() for tag in result.stdout.strip().split('\n') if tag.strip()]
                    if tags:
                        latest_tag = sorted(tags, reverse=True)[0]
                        version = latest_tag.replace(f'{service_name}-', '')
                        print(f"🏷️ Using latest {service_name} tag: {version}")
                        return version
            else:
                # For API/WEB services, we can't reliably fetch from private repo
                # The workflow should pass these via CDK context, so this shouldn't be reached
                print(f"⚠️ API/WEB tags should be provided via CDK context, not fetched here")
                        
        except Exception as e:
            print(f"⚠️ Error finding service tags for {service_name}: {e}")
    
    # Priority 4: Fallback to latest repository tag
    try:
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            fallback = result.stdout.strip()
        else:
            fallback = "latest"
    except Exception:
        fallback = "latest"
    
    if env_tag == "skip":
        print(f"🏷️  Build skipped, no service tags found, using repository tag for {context_key}: {fallback}")
    else:
        print(f"🏷️  No service tags found, using repository tag for {context_key}: {fallback}")
    return fallback
