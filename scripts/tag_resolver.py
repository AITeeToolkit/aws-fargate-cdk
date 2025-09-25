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
            # Try multiple approaches to find service tags
            service_tags = []
            
            # Method 1: Direct pattern search
            result = subprocess.run(['git', 'tag', '-l', f'{service_name}-v*'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                service_tags = [tag.strip() for tag in result.stdout.strip().split('\n') if tag.strip()]
            
            # Method 2: If no results, try listing all and filtering
            if not service_tags:
                result = subprocess.run(['git', 'tag', '--list'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    all_tags = [tag.strip() for tag in result.stdout.strip().split('\n') if tag.strip()]
                    service_tags = [tag for tag in all_tags if tag.startswith(f'{service_name}-v')]
            
            if service_tags:
                # Sort by version (reverse to get latest first)
                latest_tag = sorted(service_tags, reverse=True)[0]
                version = latest_tag.replace(f'{service_name}-', '')
                
                # Show appropriate message based on skip status
                if env_tag == "skip":
                    print(f"🏷️  Build skipped, using existing service tag for {context_key}: {version}")
                else:
                    print(f"🏷️  Using latest service tag for {context_key}: {version}")
                return version
                
        except Exception as e:
            print(f"⚠️  Error finding service tags for {service_name}: {e}")
    
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
