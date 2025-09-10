from aws_cdk import Stack, aws_codebuild as codebuild, aws_iam as iam
from constructs import Construct

class CICDStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        buildspecs = {
            "BuildAppProject": "buildspecs/build-app.yaml",
            "DeployAppProject": "buildspecs/deploy-app.yaml",
            "DeployInfraProject": "buildspecs/deploy-infra.yaml",
        }

        for name, path in buildspecs.items():
            project = codebuild.Project(
                self, name,
                project_name=name,
                source=codebuild.Source.git_hub(
                    owner="AITeeToolkit",
                    repo="storefront",
                    webhook=False,
                    clone_depth=1,
                ),
                environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                    privileged=True  # For Docker
                ),
                build_spec=codebuild.BuildSpec.from_source_filename(path)
            )

            # Attach default admin-like policy (you may restrict this later)
            project.add_to_role_policy(iam.PolicyStatement(
                actions=["*"],
                resources=["*"]
            ))