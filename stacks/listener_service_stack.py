from aws_cdk import (
    Stack,
    Duration,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
)
from constructs import Construct
from cdk_constructs.fargate_service_construct import FargateServiceConstruct


class ListenerServiceStack(Stack):
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
        service_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment variables for the listener service
        listener_environment = {
            "REPO": "AITeeToolkit/aws-fargate-cdk",
        }

        # SSM Parameter names for secrets (FargateServiceConstruct expects parameter names)
        listener_secrets = {
            "GH_TOKEN": f"/storefront-{environment}/github/PAT",
        }

        # Create IAM role for the listener service task
        task_role = iam.Role(
            self, "ListenerTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="IAM role for listener service ECS task"
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

        # Create task definition directly since we need Secrets Manager support
        task_definition = ecs.FargateTaskDefinition(
            self, "ListenerTaskDefinition",
            family=f"{service_name}-task",
            memory_limit_mib=512,
            cpu=256,
            task_role=task_role,
        )

        # Add container to task definition
        container = task_definition.add_container(
            "ListenerContainer",
            image=ecs.ContainerImage.from_registry(image_uri),
            environment=listener_environment,
            secrets={
                "GH_TOKEN": ecs.Secret.from_ssm_parameter(
                    ssm.StringParameter.from_string_parameter_name(
                        self, "GitHubTokenParam",
                        string_parameter_name=f"/storefront-{environment}/github/PAT"
                    )
                ),
                "PGHOST": ecs.Secret.from_secrets_manager(db_secret, "host"),
                "PGUSER": ecs.Secret.from_secrets_manager(db_secret, "username"),
                "PGPASSWORD": ecs.Secret.from_secrets_manager(db_secret, "password"),
                "PGDATABASE": ecs.Secret.from_secrets_manager(db_secret, "dbname"),
                "PGPORT": ecs.Secret.from_secrets_manager(db_secret, "port"),
            },
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="listener",
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
        )

        # Create the Fargate service
        self.service = ecs.FargateService(
            self, "listener-service",
            cluster=cluster,
            task_definition=task_definition,
            service_name=service_name,
            desired_count=1,
            security_groups=[ecs_task_security_group],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            enable_execute_command=True,
        )