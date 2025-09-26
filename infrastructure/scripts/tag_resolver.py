def resolve_tag(context_key: str, env_var: str, app_context,
                service_files: Optional[List[str]] = None,
                service_name: str = None,
                external_repo: str = None) -> str:
    """
    Resolve a tag with clear priorities:
    1. CDK context
    2. Environment variable
    3. Service-specific tags (local or external repo)
    4. Fallback to latest repo tag
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
    if service_name:
        try:
            service_tags = []
            if external_repo:
                # fetch remote tags
                result = subprocess.run(
                    ["git", "ls-remote", "--tags", external_repo],
                    capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    tags = [line.split("/")[-1] for line in result.stdout.splitlines()]
                    service_tags = [tag for tag in tags if tag.startswith(f"{service_name}-v")]
            else:
                # local tags
                result = subprocess.run(["git", "tag", "-l", f"{service_name}-v*"], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    service_tags = [tag.strip() for tag in result.stdout.splitlines()]

            if service_tags:
                latest_tag = sorted(service_tags, reverse=True)[0]
                version = latest_tag.replace(f"{service_name}-", "")
                print(f"🏷️  Using latest service tag for {context_key}: {version}")
                return version
        except Exception as e:
            print(f"⚠️  Error resolving tags for {service_name}: {e}")

    # Priority 4: fallback
    try:
        result = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            fallback = result.stdout.strip()
        else:
            fallback = "latest"
    except Exception:
        fallback = "latest"
    print(f"🏷️  No service tags found, using repository tag for {context_key}: {fallback}")
    return fallback