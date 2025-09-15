from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
)
from constructs import Construct


class DomainUpdaterStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        cluster: ecs.ICluster,
        image_uri: str,
        db_secret: secretsmanager.ISecret,
        environment: str,
        ecs_task_security_group: ec2.ISecurityGroup,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM role for the domain updater task
        task_role = iam.Role(
            self, "DomainUpdaterTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="IAM role for domain updater ECS task"
        )

        # Add permissions for Secrets Manager (RDS credentials)
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret"
                ],
                resources=[db_secret.secret_arn]
            )
        )

        # Add permissions for SSM Parameter Store (GitHub token)
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath"
                ],
                resources=[
                    f"arn:aws:ssm:*:*:parameter/storefront-{environment}/*"
                ]
            )
        )

        # Create task execution role
        execution_role = iam.Role(
            self, "DomainUpdaterExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
        )

        # Create log group
        log_group = logs.LogGroup(
            self, "DomainUpdaterLogGroup",
            log_group_name=f"/ecs/domain-updater-{environment}",
            retention=logs.RetentionDays.ONE_WEEK
        )

        # Create task definition
        self.task_definition = ecs.FargateTaskDefinition(
            self, "DomainUpdaterTaskDefinition",
            family=f"domain-updater-{environment}",
            cpu=256,
            memory_limit_mib=512,
            task_role=task_role,
            execution_role=execution_role
        )

        # Add container to task definition
        container = self.task_definition.add_container(
            "DomainUpdaterContainer",
            image=ecs.ContainerImage.from_registry(image_uri),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="domain-updater",
                log_group=log_group
            ),
            environment={
                "REPO": "AITeeToolkit/aws-fargate-cdk",
                "ENVIRONMENT": environment,
            },
            secrets={
                "GH_TOKEN": ecs.Secret.from_ssm_parameter(
                    ssm.StringParameter.from_string_parameter_name(
                        self, "GitHubTokenParam",
                        string_parameter_name=f"/storefront-{environment}/github-token"
                    )
                ),
                "DB_SECRET_NAME": ecs.Secret.from_parameter_store(db_secret.secret_name),
            }
        )

        # Output the task definition ARN for use in GitHub Actions
        self.task_definition_arn = self.task_definition.task_definition_arn
