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
    4. Fallback to v1.0.0
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
            # Get all tags for this service
            result = subprocess.run(['git', 'tag', '--list'], capture_output=True, text=True)
            if result.returncode == 0:
                all_tags = result.stdout.strip().split('\n')
                service_tags = [tag for tag in all_tags if tag.startswith(f'{service_name}-v')]
                
                if service_tags:
                    # Sort by version (simple string sort works for semantic versions)
                    latest_tag = sorted(service_tags, reverse=True)[0]
                    version = latest_tag.replace(f'{service_name}-', '')
                    
                    # Show appropriate message based on skip status
                    if env_tag == "skip":
                        print(f"🏷️  Build skipped, using existing service tag for {context_key}: {version}")
                    else:
                        print(f"🏷️  Using latest service tag for {context_key}: {version}")
                    return version
        except Exception as e:
            print(f"⚠️  Error finding service tags: {e}")
    
    # Priority 4: Fallback
    fallback = "v1.0.0"
    if env_tag == "skip":
        print(f"🏷️  Build skipped, no existing tags found for {context_key}: {fallback}")
    else:
        print(f"🏷️  No existing tags, using initial version for {context_key}: {fallback}")
    return fallback
