from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
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
        use_public_access: bool = False,  # Controls `publicly_accessible`
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Optional CDK context override
        context_override = self.node.try_get_context("public_db")
        if context_override is not None:
            use_public_access = str(context_override).lower() == "true"

        # Store credentials in Secrets Manager
        credentials = rds.Credentials.from_generated_secret(
            username="postgres",
            secret_name=f"storefront/{environment}/rds-credentials"
        )

        # Mixed subnet group (public + private_with_egress)
        mixed_subnets = ec2.SubnetSelection(
            subnets=[
                *vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnets,
                *vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS).subnets,
            ]
        )

        mixed_subnet_group = rds.SubnetGroup(
            self, f"StorefrontPostgres{environment.title()}MixedSubnetGroup",
            description="Mixed subnet group (public + private) for flexible RDS access",
            vpc=vpc,
            vpc_subnets=mixed_subnets
        )

        # Create database security group
        self.db_security_group = ec2.SecurityGroup(
            self, f"DatabaseSecurityGroup-{environment}",
            vpc=vpc,
            description=f"Security group for RDS PostgreSQL instance - {environment}",
            allow_all_outbound=False
        )

        # Allow PostgreSQL connections from VPC
        self.db_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(5432),
            description="Allow PostgreSQL access from VPC"
        )

        # Create the RDS DB instance
        self.db_instance = rds.DatabaseInstance(
            self, f"StorefrontPostgres-{environment}",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.of("17.6", "17")
            ),
            vpc=vpc,
            subnet_group=mixed_subnet_group,
            publicly_accessible=use_public_access,
            credentials=credentials,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            backup_retention=Duration.days(7),
            removal_policy=RemovalPolicy.SNAPSHOT,
            delete_automated_backups=True,
            database_name=f"storefront_{environment}",
            security_groups=[self.db_security_group]
        )

        self.secret = self.db_instance.secret

        # Write database connection details to SSM Parameter Store
        # This eliminates CloudFormation export dependencies
        ssm.StringParameter(
            self, f"DatabaseHost-{environment}",
            parameter_name=f"/storefront-{environment}/database/host",
            string_value=self.db_instance.instance_endpoint.hostname,
            description=f"Database hostname for storefront {environment}"
        )

        ssm.StringParameter(
            self, f"DatabasePort-{environment}",
            parameter_name=f"/storefront-{environment}/database/port",
            string_value=str(self.db_instance.instance_endpoint.port),
            description=f"Database port for storefront {environment}"
        )

        # Expose properties for direct CDK references (no CloudFormation exports)
        self.database_host = self.db_instance.instance_endpoint.hostname
        self.database_port = self.db_instance.instance_endpoint.port
        self.database_name = f"storefront_{environment}"
        self.database_username = "postgres"