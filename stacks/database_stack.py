from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class DatabaseStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        environment: str = "dev",
        use_public_subnets: bool = False,  # set to True to make DB public
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Optionally allow override from context
        context_override = self.node.try_get_context("public_db")
        if context_override is not None:
            use_public_subnets = str(context_override).lower() == "true"

        # Store RDS credentials in Secrets Manager
        credentials = rds.Credentials.from_generated_secret(
            username="dbadmin",
            secret_name=f"storefront/{environment}/rds-credentials"
        )

        # Define subnet groups
        private_subnet_group = rds.SubnetGroup(
            self, f"StorefrontPostgres{environment.title()}PrivateSubnetGroup",
            description="Private subnet group for RDS",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )

        public_subnet_group = rds.SubnetGroup(
            self, f"StorefrontPostgres{environment.title()}PublicSubnetGroup",
            description="Public subnet group for RDS",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )

        # Choose subnet group based on toggle switch
        selected_subnet_group = public_subnet_group if use_public_subnets else private_subnet_group

        # Create the RDS PostgreSQL instance
        self.db_instance = rds.DatabaseInstance(
            self, f"StorefrontPostgres-{environment}",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.of("17.6", "17")  # update as needed
            ),
            vpc=vpc,
            subnet_group=selected_subnet_group,
            publicly_accessible=use_public_subnets,
            credentials=credentials,
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            backup_retention=Duration.days(7),
            removal_policy=RemovalPolicy.SNAPSHOT,
            delete_automated_backups=True,
            database_name=f"storefront_{environment}"
        )

        # Expose the secret for downstream use
        self.secret = self.db_instance.secret