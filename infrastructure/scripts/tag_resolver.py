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
            # For API/WEB services, fetch from storefront-cdk repository
            if service_name in ['api', 'web']:
                print(f"🔍 Fetching {service_name} tags from storefront-cdk...")
                # Try with GitHub token if available
                github_token = os.environ.get('GITHUB_TOKEN')
                if github_token:
                    repo_url = f'https://{github_token}@github.com/AITeeToolkit/storefront-cdk.git'
                else:
                    repo_url = 'https://github.com/AITeeToolkit/storefront-cdk.git'
                
                result = subprocess.run([
                    'git', 'ls-remote', '--tags', repo_url
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip():
                    # Parse git ls-remote output: "hash\trefs/tags/api-v1.6.1"
                    lines = result.stdout.strip().split('\n')
                    versions = []
                    for line in lines:
                        if f'\trefs/tags/{service_name}-v' in line:
                            # Extract version: "hash\trefs/tags/api-v1.6.1" -> "v1.6.1"
                            tag_part = line.split('\t')[1]  # "refs/tags/api-v1.6.1"
                            version = tag_part.split(f'{service_name}-')[1]  # "v1.6.1"
                            versions.append(version)
                    
                    if versions:
                        # Sort versions and get latest
                        def version_sort_key(v):
                            try:
                                parts = [int(x) for x in v.replace('v', '').split('.')]
                                return tuple(parts)
                            except:
                                return (0, 0, 0)
                        
                        latest_version = sorted(versions, key=version_sort_key, reverse=True)[0]
                        print(f"🏷️ Using latest {service_name} tag: {latest_version}")
                        return latest_version
                    else:
                        print(f"⚠️ No {service_name} service tags found in storefront-cdk")
                else:
                    print(f"⚠️ Failed to fetch tags from storefront-cdk: {result.stderr}")
            else:
                # For listener/dns-worker, use local repository tags
                result = subprocess.run(['git', 'tag', '-l', f'{service_name}-v*'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    tags = [tag.strip() for tag in result.stdout.strip().split('\n') if tag.strip()]
                    if tags:
                        latest_tag = sorted(tags, reverse=True)[0]
                        version = latest_tag.replace(f'{service_name}-', '')
                        print(f"🏷️ Using latest {service_name} tag: {version}")
                        return version
                        
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
