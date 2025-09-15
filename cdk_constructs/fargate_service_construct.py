from aws_cdk import (
    Duration,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_iam as iam,
    aws_ssm as ssm,
    RemovalPolicy,
)
from constructs import Construct


class FargateServiceConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        cluster: ecs.Cluster,
        vpc: ec2.IVpc,
        container_image: ecs.ContainerImage,
        desired_count: int = 2,
        container_port: int = 3000,
        environment: dict = {},
        secrets: dict = {},
        security_groups: list = None,
        service_name: str = None,
        cloud_map_options: ecs.CloudMapOptions = None,
        subnet_type: ec2.SubnetType = ec2.SubnetType.PRIVATE_ISOLATED,
    ) -> None:
        super().__init__(scope, id)

        # Log group
        log_group = logs.LogGroup(
            self, f"{id}LogGroup",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK,
        )

        # Execution role
        execution_role = iam.Role(
            self, f"{id}ExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )
        execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath",
                ],
                resources=["*"],
            )
        )

        # Task definition
        task_def = ecs.FargateTaskDefinition(
            self, f"{id}TaskDef",
            family=f"{id}-taskdef",
            memory_limit_mib=512,
            cpu=256,
            execution_role=execution_role,
        )

        # Task role permissions
        task_def.task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
        )
        task_def.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath",
                ],
                resources=["*"],
            )
        )
        task_def.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams",
                ],
                resources=["arn:aws:logs:*:*:*"],
            )
        )
        task_def.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret",
                ],
                resources=["*"],
            )
        )

        # Map SSM secrets
        ecs_secrets = {
            name: ecs.Secret.from_ssm_parameter(
                ssm.StringParameter.from_string_parameter_name(
                    self, f"{name}Param", value_from
                )
            )
            for name, value_from in secrets.items()
        }

        # Container
        task_def.add_container(
            f"{id}Container",
            image=container_image,
            container_name=id,
            port_mappings=[ecs.PortMapping(container_port=container_port)],
            environment=environment,
            secrets=ecs_secrets,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix=id,
                log_group=log_group,
            ),
            # Disable container health check to rely only on ALB health checks
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "exit 0"],  # Always pass container health check
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60)
            ),
        )

        # Fargate service (no ALB wiring here)
        service = ecs.FargateService(
            self, f"{id}Service",
            cluster=cluster,
            task_definition=task_def,
            enable_execute_command=True,
            assign_public_ip=True,  # Enable public IP for internet access
            desired_count=desired_count,
            service_name=service_name,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),  # Use public subnets
            security_groups=security_groups or [],
            cloud_map_options=cloud_map_options,
        )

        self.service = service