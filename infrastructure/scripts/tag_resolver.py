def resolve_tag(context_key: str, env_var: str, app_context, service_name: str = None, external_repo: str = None) -> str:
    """
    Resolve a tag with clear priorities:
    1. CDK context
    2. Environment variable
    3. Service-specific tag (local or external repo)
    4. Fallback to latest repo tag
    """
    # Priority 1: CDK context
    context_tag = app_context.node.try_get_context(context_key)
    if context_tag and context_tag != "skip":
        print(f"🏷️  Using context tag for {context_key}: {context_tag}")
        return context_tag

    # Priority 2: Env var
    env_tag = os.environ.get(env_var)
    if env_tag and env_tag != "skip":
        print(f"🏷️  Using environment tag for {context_key}: {env_tag}")
        return env_tag

    # Priority 3: Service tags
    if service_name:
        try:
            if external_repo:
                # 🔗 Fetch from remote repo (API/WEB case)
                result = subprocess.run(
                    ['git', 'ls-remote', '--tags', external_repo],
                    capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    tags = [line.split('/')[-1] for line in result.stdout.splitlines()]
                    service_tags = [tag for tag in tags if tag.startswith(f'{service_name}-v')]
                else:
                    service_tags = []
            else:
                # Local repo (listener/dns-worker)
                result = subprocess.run(['git', 'tag', '-l', f'{service_name}-v*'], capture_output=True, text=True)
                service_tags = result.stdout.strip().splitlines() if result.returncode == 0 else []

            if service_tags:
                latest_tag = sorted(service_tags, reverse=True)[0]
                version = latest_tag.replace(f'{service_name}-', '')
                print(f"🏷️  Using latest service tag for {context_key}: {version}")
                return version

        except Exception as e:
            print(f"⚠️  Error resolving tags for {service_name}: {e}")

    # Priority 4: Repo fallback
    try:
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else "latest"
    except Exception:
        return "latest"