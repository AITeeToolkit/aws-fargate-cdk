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
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # RDS credentials stored in Secrets Manager
        credentials = rds.Credentials.from_generated_secret(
            username="dbadmin",
            secret_name=f"storefront/{environment}/rds-credentials"
        )

        # Create public subnet group only (private one already exists from previous deployment)
        public_subnet_group = rds.SubnetGroup(
            self, f"StorefrontPostgres{environment.title()}PublicSubnetGroup",
            description=f"Subnet group for StorefrontPostgres-{environment} database (public)",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )
        
        # Choose which subnet group to use (change this line to switch)
        # For private: use vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        # For public: use subnet_group=public_subnet_group
        use_public_subnets = True

        # Create a PostgreSQL database instance
        self.db_instance = rds.DatabaseInstance(
            self, f"StorefrontPostgres-{environment}",
            engine = rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.of("17.6", "17")
            ),
            vpc=vpc,
            credentials=credentials,
            subnet_group=public_subnet_group if use_public_subnets else None,
            vpc_subnets=None if use_public_subnets else ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
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
            publicly_accessible=True,
            # publicly_accessible=True,
            database_name=f"storefront_{environment}"
        )

        self.secret = self.db_instance.secret