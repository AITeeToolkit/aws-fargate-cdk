from aws_cdk import Stack, aws_ecr as ecr, RemovalPolicy
from constructs import Construct

class ECRStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        repository_names: list[str],
        environment: str = "dev",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.repositories = {}

        for name in repository_names:
            repo_name = f"storefront/{environment}/{name}"
            
            # Try to import existing repository first, create if it doesn't exist
            try:
                # Attempt to import existing repository
                repo = ecr.Repository.from_repository_name(
                    self, f"{name.capitalize()}Repo",
                    repository_name=repo_name
                )
                print(f"Imported existing ECR repository: {repo_name}")
            except:
                # Repository doesn't exist, create it
                repo = ecr.Repository(
                    self, f"{name.capitalize()}Repo",
                    repository_name=repo_name,
                    removal_policy=RemovalPolicy.DESTROY,
                    image_scan_on_push=True,
                    lifecycle_rules=[
                        ecr.LifecycleRule(
                            description="Keep only 10 most recent images",
                            max_image_count=10
                        )
                    ]
                )
                print(f"Created new ECR repository: {repo_name}")
            
            self.repositories[name] = repo