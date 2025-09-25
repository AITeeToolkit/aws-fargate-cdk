"""
Tag Resolution Utility for AWS Fargate CDK

Resolves image tags with priority: CDK context -> env var -> smart git-based defaults
Supports service-specific versioning based on file changes.
"""

import os
import subprocess
from typing import List, Optional


def _increment_version(version: str) -> str:
    """
    Increment semantic version (patch level).
    
    Args:
        version: Current version (e.g., "v1.2.3")
        
    Returns:
        str: Incremented version (e.g., "v1.2.4")
    """
    try:
        # Remove 'v' prefix if present
        clean_version = version.lstrip('v')
        parts = clean_version.split('.')
        
        if len(parts) >= 3:
            # Increment patch version
            parts[2] = str(int(parts[2]) + 1)
        elif len(parts) == 2:
            # Add patch version
            parts.append('1')
        else:
            # Invalid format, default to v1.0.1
            return "v1.0.1"
            
        return f"v{'.'.join(parts)}"
    except (ValueError, IndexError):
        # Fallback for invalid version format
        return "v1.0.1"


def resolve_tag(context_key: str, env_var: str, app_context, service_files: Optional[List[str]] = None, service_name: str = None) -> str:
    """
    Resolve image tag with intelligent fallback logic.
    
    Args:
        context_key: CDK context key (e.g., "listenerTag")
        env_var: Environment variable name (e.g., "LISTENER_IMAGE_TAG")
        app_context: CDK app context object
        service_files: List of service-specific files to check for changes
        service_name: Service name for tag namespace (e.g., "listener", "dns-worker")
        
    Returns:
        str: Resolved image tag
    """
    # Priority 1: CDK context (highest priority)
    context_tag = app_context.node.try_get_context(context_key)
    if context_tag and context_tag != "skip":
        print(f"🏷️  Using context tag for {context_key}: {context_tag}")
        return context_tag

    # Priority 2: Environment variable
    env_tag = os.environ.get(env_var)
    if env_tag and env_tag != "skip":
        print(f"🏷️  Using environment tag for {context_key}: {env_tag}")
        return env_tag
    
    # If we have "skip" values, we still need to resolve the actual tag for display
    # Continue to git-based resolution even when skip is set
    
    # Priority 3: Smart default based on git branch
    try:
        # Get current git branch
        branch_result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                     capture_output=True, text=True, cwd=os.getcwd())
        if branch_result.returncode == 0:
            branch = branch_result.stdout.strip()
            
            if branch == "main":
                # On main branch, use service-specific tags
                if service_name:
                    # Check for existing service-specific tags
                    service_tags_result = subprocess.run(['git', 'tag', '-l', f'{service_name}-v*', '--sort=-version:refname'], 
                                                       capture_output=True, text=True, cwd=os.getcwd())
                
                    if service_tags_result.returncode == 0 and service_tags_result.stdout.strip():
                        service_tags = [tag for tag in service_tags_result.stdout.strip().split('\n') if tag.strip()]
                        if service_tags:
                            latest_service_tag = service_tags[0]
                            service_version = latest_service_tag.replace(f'{service_name}-', '')
                            
                            # Check if this service is being skipped
                            service_tag_input = os.environ.get(f"{service_name.upper().replace('-', '_')}_IMAGE_TAG")
                            
                            if service_files:
                                # Check if service files changed since last service tag
                                diff_result = subprocess.run(['git', 'diff', '--name-only', latest_service_tag, 'HEAD', '--'] + service_files,
                                                           capture_output=True, text=True, cwd=os.getcwd())
                            
                                if diff_result.stdout.strip():
                                    # Service files changed
                                    if service_tag_input and service_tag_input != "skip":
                                        # Service is being built, increment version
                                        new_version = _increment_version(service_version)
                                        new_tag = f"{service_name}-{new_version}"
                                        print(f"🏷️  Service files changed since {latest_service_tag}, using new version for {context_key}: {new_version}")
                                        return new_version
                                    else:
                                        # Service files changed but build skipped, use existing version
                                        print(f"🏷️  Service files changed since {latest_service_tag}, but build skipped, using existing for {context_key}: {service_version}")
                                        return service_version
                                else:
                                    # Service files unchanged, use existing version
                                    print(f"🏷️  Service unchanged since {latest_service_tag}, using existing for {context_key}: {service_version}")
                                    return service_version
                            else:
                                # No service files specified (e.g., API/Web from external repo)
                                if service_tag_input == "skip":
                                    print(f"🏷️  Build skipped, using existing service tag for {context_key}: {service_version}")
                                else:
                                    print(f"🏷️  Using latest service tag for {context_key}: {service_version}")
                                return service_version
                
                    # No existing service tags, start with v1.0.0
                    initial_version = "v1.0.0"
                    print(f"🏷️  First build for {service_name}, using initial version for {context_key}: {initial_version}")
                    return initial_version
                
                # Fallback to repository-wide semantic release tag (for services without service_name)
                tag_result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                                          capture_output=True, text=True, cwd=os.getcwd())
                if tag_result.returncode == 0:
                    latest_tag = tag_result.stdout.strip()
                    print(f"🏷️  Using repository semantic release tag for {context_key}: {latest_tag}")
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
