from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_iam as iam,
)
from constructs import Construct
from aws_cdk.aws_ec2 import IVpc

class SharedStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: IVpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECS Cluster shared by all services
        self.cluster = ecs.Cluster(
            self, "StorefrontCluster",
            vpc=vpc,
            container_insights=True
        )

        # IAM Role for ECS task execution (pulling from ECR, sending logs)
        self.task_execution_role = iam.Role(
            self, "ECSTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )

        self.task_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
        )