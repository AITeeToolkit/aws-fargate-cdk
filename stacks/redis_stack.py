from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as elasticache
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class RedisStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        environment: str = "dev",
        max_storage_gb: int = 1,
        max_ecpu: int = 3000,
        snapshot_retention: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Security group for Redis
        self.redis_security_group = ec2.SecurityGroup(
            self,
            "RedisSecurityGroup",
            vpc=vpc,
            description=f"Security group for Redis Serverless - {environment}",
            allow_all_outbound=False,
        )

        # Allow inbound Redis traffic from VPC
        self.redis_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(6379),
            description="Allow Redis traffic from VPC",
        )

        # Create ElastiCache Serverless for Redis
        self.redis_cache = elasticache.CfnServerlessCache(
            self,
            "RedisServerless",
            engine="redis",
            serverless_cache_name=f"storefront-cache-{environment}",
            description=f"Redis Serverless cache for {environment} environment",
            # Use private subnets for security
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
            security_group_ids=[self.redis_security_group.security_group_id],
            # Set usage limits to control costs
            cache_usage_limits=elasticache.CfnServerlessCache.CacheUsageLimitsProperty(
                data_storage=elasticache.CfnServerlessCache.DataStorageProperty(
                    maximum=max_storage_gb, unit="GB"
                ),
                ecpu_per_second=elasticache.CfnServerlessCache.ECPUPerSecondProperty(
                    maximum=max_ecpu
                ),
            ),
            # Optional: Configure snapshot retention
            daily_snapshot_time="03:00",  # 3 AM UTC
            snapshot_retention_limit=snapshot_retention,
        )

        # Store Redis endpoint in SSM Parameter Store
        redis_endpoint = ssm.StringParameter(
            self,
            "RedisEndpoint",
            parameter_name=f"/storefront/{environment}/redis/endpoint",
            string_value=self.redis_cache.attr_endpoint_address,
            description=f"Redis Serverless endpoint for {environment}",
        )

        redis_port = ssm.StringParameter(
            self,
            "RedisPort",
            parameter_name=f"/storefront/{environment}/redis/port",
            string_value=self.redis_cache.attr_endpoint_port,
            description=f"Redis Serverless port for {environment}",
        )

        # Output the Redis endpoint
        CfnOutput(
            self,
            "RedisEndpointOutput",
            value=self.redis_cache.attr_endpoint_address,
            description="Redis Serverless endpoint address",
            export_name=f"{environment}-redis-endpoint",
        )

        CfnOutput(
            self,
            "RedisPortOutput",
            value=self.redis_cache.attr_endpoint_port,
            description="Redis Serverless port",
            export_name=f"{environment}-redis-port",
        )

        # Store security group for other stacks to reference
        self.redis_endpoint = self.redis_cache.attr_endpoint_address
        self.redis_port = self.redis_cache.attr_endpoint_port
