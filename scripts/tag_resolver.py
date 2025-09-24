"""
Tag Resolution Utility for AWS Fargate CDK

Resolves image tags with priority: CDK context -> env var -> smart git-based defaults
Supports service-specific versioning based on file changes.
"""

import os
import subprocess
from typing import List, Optional


def resolve_tag(context_key: str, env_var: str, app_context, service_files: Optional[List[str]] = None) -> str:
    """
    Resolve image tag with intelligent fallback logic.
    
    Args:
        context_key: CDK context key (e.g., "listenerTag")
        env_var: Environment variable name (e.g., "LISTENER_IMAGE_TAG")
        app_context: CDK app context object
        service_files: List of service-specific files to check for changes
        
    Returns:
        str: Resolved image tag
    """
    # Priority 1: CDK context (from pipeline)
    context_tag = app_context.node.try_get_context(context_key)
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
        # Get current git branch
        branch_result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                     capture_output=True, text=True, cwd=os.getcwd())
        if branch_result.returncode == 0:
            branch = branch_result.stdout.strip()
            
            if branch == "main":
                # On main branch, check if service files have changed since last tag
                if service_files:
                    # Get latest tag
                    tag_result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                                              capture_output=True, text=True, cwd=os.getcwd())
                    if tag_result.returncode == 0:
                        latest_tag = tag_result.stdout.strip()
                        
                        # Check if service files changed since last tag
                        diff_result = subprocess.run(['git', 'diff', '--name-only', latest_tag, 'HEAD', '--'] + service_files,
                                                   capture_output=True, text=True, cwd=os.getcwd())
                        
                        if diff_result.stdout.strip():
                            # Service files changed, use latest tag
                            print(f"🏷️  Service files changed since {latest_tag}, using for {context_key}: {latest_tag}")
                            return latest_tag
                        else:
                            # Service files unchanged, use last commit that touched these files + tag
                            commit_result = subprocess.run(['git', 'log', '-1', '--format=%h', '--'] + service_files,
                                                         capture_output=True, text=True, cwd=os.getcwd())
                            if commit_result.returncode == 0:
                                commit_sha = commit_result.stdout.strip()
                                service_tag = f"{latest_tag}-{commit_sha}"
                                print(f"🏷️  Service unchanged since {latest_tag}, using cached for {context_key}: {service_tag}")
                                return service_tag
                
                # Fallback to latest semantic release tag
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
