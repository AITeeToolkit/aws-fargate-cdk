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
            # Import existing ECR repository instead of creating new one
            repo = ecr.Repository.from_repository_name(
                self, f"{name.capitalize()}Repo",
                repository_name=f"storefront/{environment}/{name}"
            )
            self.repositories[name] = repo