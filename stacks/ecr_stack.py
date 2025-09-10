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
            repo = ecr.Repository(
                self, f"{name.capitalize()}Repo",
                repository_name=f"storefront/{environment}/{name}",
                removal_policy=RemovalPolicy.RETAIN,
                image_scan_on_push=True,
                lifecycle_rules=[
                    ecr.LifecycleRule(
                        rule_priority=1,
                        tag_status=ecr.TagStatus.ANY,
                        max_image_count=10
                    )
                ]
            )
            self.repositories[name] = repo