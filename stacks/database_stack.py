from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class DatabaseStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        environment: str = "dev",
        use_public_access: bool = True,  # Default: private
        multi_az: bool = False,
        instance_class: str = "db.t3.micro",
        deletion_protection: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Optional CDK context override (e.g. --context public_db=true)
        context_override = self.node.try_get_context("public_db")
        if context_override is not None:
            use_public_access = str(context_override).lower() == "true"

        # Store credentials in Secrets Manager
        credentials = rds.Credentials.from_generated_secret(
            username="postgres", secret_name=f"storefront/{environment}/rds-credentials"
        )

        # Public subnet group only (supports toggle without DB replacement)
        public_subnet_group = rds.SubnetGroup(
            self,
            f"StorefrontPostgres{environment.title()}PublicSubnetGroup",
            description="RDS subnet group (public only, allows safe toggle)",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        # Security group for DB
        self.db_security_group = ec2.SecurityGroup(
            self,
            f"DatabaseSecurityGroup-{environment}",
            vpc=vpc,
            description=f"RDS PostgreSQL security group - {environment}",
            allow_all_outbound=True,
        )

        # Allow internal VPC access
        self.db_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(5432),
            description="Allow internal VPC PostgreSQL access",
        )

        # Optional: Allow your IP if testing publicly
        self.db_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("70.122.3.208/32"),
            connection=ec2.Port.tcp(5432),
            description="Allow public IP PostgreSQL access",
        )

        # Parse instance class
        instance_class_parts = instance_class.split(".")
        if len(instance_class_parts) != 3:
            raise ValueError(f"Invalid instance class format: {instance_class}")

        db_class = getattr(ec2.InstanceClass, instance_class_parts[1].upper())
        db_size = getattr(ec2.InstanceSize, instance_class_parts[2].upper())

        # RDS instance
        self.db_instance = rds.DatabaseInstance(
            self,
            f"DB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.of("17.6", "17")
            ),
            instance_identifier=f"{environment}-db",
            vpc=vpc,
            subnet_group=public_subnet_group,
            publicly_accessible=use_public_access,
            credentials=credentials,
            instance_type=ec2.InstanceType.of(db_class, db_size),
            multi_az=multi_az,
            allocated_storage=20,
            max_allocated_storage=100,
            backup_retention=Duration.days(7 if environment != "prod" else 30),
            removal_policy=(
                RemovalPolicy.SNAPSHOT if deletion_protection else RemovalPolicy.DESTROY
            ),
            deletion_protection=deletion_protection,
            delete_automated_backups=not deletion_protection,
            database_name="postgres",
            security_groups=[self.db_security_group],
            storage_encrypted=True,
        )
        
        # Override CloudFormation to allow replacement of custom-named resource
        cfn_db = self.db_instance.node.default_child
        cfn_db.add_override("UpdateReplacePolicy", "Snapshot")
        cfn_db.add_override("DeletionPolicy", "Snapshot" if deletion_protection else "Delete")

        self.secret = self.db_instance.secret

        # Store DB connection details in SSM Parameter Store
        ssm.StringParameter(
            self,
            f"DatabaseHost-{environment}",
            parameter_name=f"/storefront-{environment}/database/host",
            string_value=self.db_instance.instance_endpoint.hostname,
            description=f"Database host - {self.db_instance.instance_identifier}",
        )

        ssm.StringParameter(
            self,
            f"DatabasePort-{environment}",
            parameter_name=f"/storefront-{environment}/database/port",
            string_value=str(self.db_instance.instance_endpoint.port),
            description=f"Database port - {self.db_instance.instance_identifier}",
        )

        ssm.StringParameter(
            self,
            f"DatabasePassword-{environment}",
            parameter_name=f"/storefront-{environment}/database/password",
            string_value=self.db_instance.secret.secret_value_from_json(
                "password"
            ).unsafe_unwrap(),
            description=f"Database password - {self.db_instance.instance_identifier}",
        )

        # Store master username in Parameter Store
        ssm.StringParameter(
            self,
            f"DatabaseUsername-{environment}",
            parameter_name=f"/storefront-{environment}/database/username",
            string_value=self.db_instance.secret.secret_value_from_json(
                "username"
            ).unsafe_unwrap(),
            description=f"Database username - {self.db_instance.instance_identifier}",
        )

        # Store database name in Parameter Store
        ssm.StringParameter(
            self,
            f"DatabaseName-{environment}",
            parameter_name=f"/storefront-{environment}/database/name",
            string_value=self.db_instance.secret.secret_value_from_json(
                "dbname"
            ).unsafe_unwrap(),
            description=f"Database name - {self.db_instance.instance_identifier}",
        )

        # Expose for other stacks (if needed)
        self.database_host = self.db_instance.instance_endpoint.hostname
        self.database_port = self.db_instance.instance_endpoint.port
        self.database_name = "postgres"
        self.database_username = "postgres"
