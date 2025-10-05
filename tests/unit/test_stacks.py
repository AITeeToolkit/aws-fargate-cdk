"""
Unit tests for CDK stacks
"""

import aws_cdk as cdk
import pytest
from aws_cdk import assertions

from stacks.api_service_stack import APIServiceStack
from stacks.certificate_stack import CertificateStack
from stacks.control_plane_service_stack import ControlPlaneServiceStack
from stacks.database_stack import DatabaseStack
from stacks.domain_dns_stack import DomainDnsStack
from stacks.ecr_stack import ECRStack
from stacks.go_dns_service_stack import GoDnsServiceStack
from stacks.network_stack import NetworkStack
from stacks.opensearch_stack import OpenSearchStack
from stacks.redis_stack import RedisStack
from stacks.shared_stack import SharedStack
from stacks.sqs_stack import SQSStack
from stacks.web_multialb_stack import MultiAlbStack
from stacks.web_service_stack import WebServiceStack


class TestNetworkStack:
    """Test NetworkStack creation and resources"""

    def test_vpc_creation(self, cdk_app, test_environment):
        """Test VPC is created with correct configuration"""
        stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        template = assertions.Template.from_stack(stack)

        # Verify VPC is created
        template.has_resource_properties(
            "AWS::EC2::VPC",
            {
                "CidrBlock": "10.0.0.0/16",
                "EnableDnsHostnames": True,
                "EnableDnsSupport": True,
            },
        )

        # Verify subnets are created
        template.resource_count_is("AWS::EC2::Subnet", 4)  # 2 public + 2 private

    def test_internet_gateway(self, cdk_app, test_environment):
        """Test Internet Gateway is created"""
        stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        template = assertions.Template.from_stack(stack)

        template.has_resource("AWS::EC2::InternetGateway", {})
        template.has_resource("AWS::EC2::VPCGatewayAttachment", {})


class TestSharedStack:
    """Test SharedStack ECS cluster and security groups"""

    def test_ecs_cluster_creation(self, cdk_app, test_environment):
        """Test ECS cluster is created"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )
        template = assertions.Template.from_stack(shared_stack)

        template.has_resource("AWS::ECS::Cluster", {})

    def test_security_groups(self, cdk_app, test_environment):
        """Test security groups are created with correct rules"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )
        template = assertions.Template.from_stack(shared_stack)

        # Should have ALB, ECS task, and VPC endpoint security groups
        template.resource_count_is("AWS::EC2::SecurityGroup", 3)

        # Verify ALB security group allows HTTPS
        template.has_resource_properties(
            "AWS::EC2::SecurityGroup",
            {
                "GroupDescription": "Security group for Application Load Balancer",
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "CidrIp": "0.0.0.0/0",
                    }
                ],
            },
        )

        # Verify ECS task security group exists
        template.has_resource_properties(
            "AWS::EC2::SecurityGroup",
            {"GroupDescription": "Security group for ECS tasks"},
        )

        # Verify VPC endpoint security group exists
        template.has_resource_properties(
            "AWS::EC2::SecurityGroup",
            {"GroupDescription": "Security group for VPC endpoints"},
        )


class TestDatabaseStack:
    """Test DatabaseStack RDS and secrets"""

    def test_rds_instance_creation(self, cdk_app, test_environment):
        """Test RDS instance is created with correct configuration"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        db_stack = DatabaseStack(
            cdk_app,
            "TestDatabaseStack",
            env=test_environment,
            vpc=network_stack.vpc,
            environment="test",
            multi_az=False,
            instance_class="db.t3.micro",
            deletion_protection=False,
        )
        template = assertions.Template.from_stack(db_stack)

        template.has_resource_properties(
            "AWS::RDS::DBInstance",
            {
                "Engine": "postgres",
                "MultiAZ": False,  # Single AZ for test environment
                "StorageEncrypted": True,
                "DeletionProtection": False,
            },
        )

    def test_secrets_manager(self, cdk_app, test_environment):
        """Test Secrets Manager secret is created"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        db_stack = DatabaseStack(
            cdk_app,
            "TestDatabaseStack",
            env=test_environment,
            vpc=network_stack.vpc,
            environment="test",
            multi_az=False,
            instance_class="db.t3.micro",
            deletion_protection=False,
        )
        template = assertions.Template.from_stack(db_stack)

        template.has_resource("AWS::SecretsManager::Secret", {})

    def test_environment_specific_config(self, cdk_app, test_environment):
        """Test environment-specific database configuration"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)

        # Test production configuration
        prod_db_stack = DatabaseStack(
            cdk_app,
            "ProdDatabaseStack",
            env=test_environment,
            vpc=network_stack.vpc,
            environment="prod",
            multi_az=False,
            instance_class="db.t3.medium",
            deletion_protection=True,
        )
        prod_template = assertions.Template.from_stack(prod_db_stack)

        prod_template.has_resource_properties(
            "AWS::RDS::DBInstance",
            {
                "DeletionProtection": True,
                "MultiAZ": False,  # Updated to reflect single AZ configuration
            },
        )


class TestServiceStacks:
    """Test service stacks (ControlPlane)"""

    def test_control_plane_service_creation(self, cdk_app, test_environment, test_tags):
        """Test ControlPlane service stack creates ECS service"""
        # Create dependencies
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )
        ecr_stack = ECRStack(
            cdk_app,
            "TestECRStack",
            env=test_environment,
            repository_names=["api", "web", "control-plane"],
        )
        db_stack = DatabaseStack(
            cdk_app,
            "TestDatabaseStack",
            env=test_environment,
            vpc=network_stack.vpc,
            environment="test",
            multi_az=False,
            instance_class="db.t3.micro",
            deletion_protection=False,
        )

        # Create ControlPlane service
        control_plane_stack = ControlPlaneServiceStack(
            cdk_app,
            "TestControlPlaneStack",
            env=test_environment,
            vpc=network_stack.vpc,
            cluster=shared_stack.cluster,
            image_uri=f"{ecr_stack.repositories['control-plane'].repository_uri}:{test_tags['control-plane']}",
            db_secret=db_stack.secret,
            environment="test",
            ecs_task_security_group=shared_stack.ecs_task_sg,
            service_name="control-plane-service",
            sqs_managed_policy=None,  # Mock for test
        )

        template = assertions.Template.from_stack(control_plane_stack)

        # Verify ECS service is created
        template.has_resource("AWS::ECS::Service", {})
        template.has_resource("AWS::ECS::TaskDefinition", {})


class TestECRStack:
    """Test ECR repository creation"""

    def test_ecr_repositories_creation(self, cdk_app, test_environment):
        """Test ECR repositories are created for all services"""
        # ECR stack uses boto3 to check existing repos, so we need mocked AWS
        ecr_stack = ECRStack(
            cdk_app,
            "TestECRStack",
            env=test_environment,
            repository_names=["api", "web", "control-plane"],
        )
        template = assertions.Template.from_stack(ecr_stack)

        # ECR stack creates repos only if they don't exist (uses boto3)
        # In test environment with mocked AWS, repos won't exist so they'll be created
        template.resource_count_is("AWS::ECR::Repository", 3)

        # Verify repositories have lifecycle policies
        template.has_resource_properties(
            "AWS::ECR::Repository",
            {
                "LifecyclePolicy": {
                    "LifecyclePolicyText": assertions.Match.string_like_regexp(r".*tagStatus.*")
                }
            },
        )

    def test_ecr_repositories_dict(self, cdk_app, test_environment):
        """Test ECR repositories are accessible via repositories dict"""
        ecr_stack = ECRStack(
            cdk_app,
            "TestECRStack",
            env=test_environment,
            repository_names=["api", "web", "control-plane"],
        )

        # Verify all repositories are accessible
        assert "api" in ecr_stack.repositories
        assert "web" in ecr_stack.repositories
        assert "control-plane" in ecr_stack.repositories


class TestOpenSearchStack:
    """Test OpenSearch domain creation"""

    def test_opensearch_domain_creation(self, cdk_app, test_environment):
        """Test OpenSearch domain is created with correct configuration"""
        opensearch_stack = OpenSearchStack(
            cdk_app, "TestOpenSearchStack", env=test_environment, environment="test"
        )
        template = assertions.Template.from_stack(opensearch_stack)

        # Verify OpenSearch domain is created (uses AWS::OpenSearchService::Domain)
        template.has_resource("AWS::OpenSearchService::Domain", {})

        # Just verify basic properties exist
        template.has_resource_properties(
            "AWS::OpenSearchService::Domain", {"EngineVersion": "OpenSearch_3.1"}
        )

    def test_opensearch_iam_role(self, cdk_app, test_environment):
        """Test OpenSearch IAM role is created"""
        opensearch_stack = OpenSearchStack(
            cdk_app, "TestOpenSearchStack", env=test_environment, environment="test"
        )
        template = assertions.Template.from_stack(opensearch_stack)

        # Verify IAM roles are created (3 total: fargate role + service role + CDK-generated role)
        template.resource_count_is("AWS::IAM::Role", 3)

    def test_opensearch_basic_resources(self, cdk_app, test_environment):
        """Test basic OpenSearch resources are created"""
        opensearch_stack = OpenSearchStack(
            cdk_app, "TestOpenSearchStack", env=test_environment, environment="test"
        )
        template = assertions.Template.from_stack(opensearch_stack)

        # Just verify the domain exists without checking specific properties
        template.resource_count_is("AWS::OpenSearchService::Domain", 1)

        # Verify SSM parameter is created for endpoint
        template.has_resource("AWS::SSM::Parameter", {})


class TestSQSStack:
    """Test SQS queue creation"""

    def test_sqs_queues_creation(self, cdk_app, test_environment):
        """Test SQS queues are created"""
        sqs_stack = SQSStack(cdk_app, "TestSQSStack", env=test_environment, environment="test")
        template = assertions.Template.from_stack(sqs_stack)

        # Should create 4 queues: 3 control plane queues + 1 FIFO DLQ
        # (database_operations, route53_operations, github_workflow, fifo_dlq)
        template.resource_count_is("AWS::SQS::Queue", 4)

        # Verify queue has dead letter queue configuration
        template.has_resource_properties(
            "AWS::SQS::Queue",
            {
                "RedrivePolicy": {
                    "deadLetterTargetArn": assertions.Match.any_value(),
                    "maxReceiveCount": 3,
                }
            },
        )

        # Verify FIFO queues are created (control plane queues use explicit deduplication IDs)
        template.has_resource_properties(
            "AWS::SQS::Queue", {"FifoQueue": True, "ContentBasedDeduplication": False}
        )

    def test_sqs_managed_policy(self, cdk_app, test_environment):
        """Test SQS managed policy is created"""
        sqs_stack = SQSStack(cdk_app, "TestSQSStack", env=test_environment, environment="test")
        template = assertions.Template.from_stack(sqs_stack)

        # Verify managed policy for SQS access
        template.has_resource("AWS::IAM::ManagedPolicy", {})


class TestAPIServiceStack:
    """Test API service stack"""

    def test_api_service_creation(self, cdk_app, test_environment, test_tags):
        """Test API service stack creates ECS service"""
        # Create dependencies
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )
        ecr_stack = ECRStack(
            cdk_app,
            "TestECRStack",
            env=test_environment,
            repository_names=["api", "web", "control-plane"],
        )
        db_stack = DatabaseStack(
            cdk_app,
            "TestDatabaseStack",
            env=test_environment,
            vpc=network_stack.vpc,
            environment="test",
            multi_az=False,
            instance_class="db.t3.micro",
            deletion_protection=False,
        )
        opensearch_stack = OpenSearchStack(
            cdk_app, "TestOpenSearchStack", env=test_environment, environment="test"
        )
        sqs_stack = SQSStack(cdk_app, "TestSQSStack", env=test_environment, environment="test")

        # Create API service
        api_stack = APIServiceStack(
            cdk_app,
            "TestAPIStack",
            env=test_environment,
            vpc=network_stack.vpc,
            cluster=shared_stack.cluster,
            image_uri=f"{ecr_stack.repositories['api'].repository_uri}:{test_tags['api']}",
            db_secret=db_stack.secret,
            environment="test",
            ecs_task_security_group=shared_stack.ecs_task_sg,
            service_name="api-service",
            opensearch_role=opensearch_stack.fargate_opensearch_role,
            sqs_managed_policy=sqs_stack.sqs_managed_policy,
        )

        template = assertions.Template.from_stack(api_stack)

        # Verify ECS service is created
        template.has_resource("AWS::ECS::Service", {})
        template.has_resource("AWS::ECS::TaskDefinition", {})


class TestWebServiceStack:
    """Test Web service stack"""

    def test_web_service_creation(self, cdk_app, test_environment, test_tags):
        """Test Web service stack creates ECS service"""
        # Create dependencies
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )
        ecr_stack = ECRStack(
            cdk_app,
            "TestECRStack",
            env=test_environment,
            repository_names=["api", "web", "control-plane"],
        )
        db_stack = DatabaseStack(
            cdk_app,
            "TestDatabaseStack",
            env=test_environment,
            vpc=network_stack.vpc,
            environment="test",
            multi_az=False,
            instance_class="db.t3.micro",
            deletion_protection=False,
        )
        opensearch_stack = OpenSearchStack(
            cdk_app, "TestOpenSearchStack", env=test_environment, environment="test"
        )

        # Create Web service
        web_stack = WebServiceStack(
            cdk_app,
            "TestWebStack",
            env=test_environment,
            vpc=network_stack.vpc,
            cluster=shared_stack.cluster,
            image_uri=f"{ecr_stack.repositories['web'].repository_uri}:{test_tags['web']}",
            db_secret=db_stack.secret,
            environment="test",
            ecs_task_security_group=shared_stack.ecs_task_sg,
            service_name="web-service",
            opensearch_role=opensearch_stack.fargate_opensearch_role,
        )

        template = assertions.Template.from_stack(web_stack)

        # Verify ECS service is created
        template.has_resource("AWS::ECS::Service", {})
        template.has_resource("AWS::ECS::TaskDefinition", {})


class TestGoDnsServiceStack:
    """Test Go DNS service stack"""

    def test_go_dns_service_creation(self, cdk_app, test_environment, test_tags):
        """Test Go DNS service stack creates ECS service"""
        # Create dependencies
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )
        ecr_stack = ECRStack(
            cdk_app,
            "TestECRStack",
            env=test_environment,
            repository_names=["api", "web", "control-plane", "go-dns"],
        )

        # Create Go DNS service (without ALB)
        go_dns_stack = GoDnsServiceStack(
            cdk_app,
            "TestGoDnsStack",
            env=test_environment,
            vpc=network_stack.vpc,
            cluster=shared_stack.cluster,
            image_uri=f"{ecr_stack.repositories['go-dns'].repository_uri}:latest",
            environment="test",
            ecs_task_security_group=shared_stack.ecs_task_sg,
            service_name="go-dns-service",
        )

        template = assertions.Template.from_stack(go_dns_stack)

        # Verify ECS service is created
        template.has_resource("AWS::ECS::Service", {})
        template.has_resource("AWS::ECS::TaskDefinition", {})


class TestCertificateStack:
    """Test Certificate stack for ACM certificates"""

    def test_certificate_creation(self, cdk_app, test_environment):
        """Test ACM certificate is created for domain"""
        cert_stack = CertificateStack(
            cdk_app,
            "TestCertificateStack",
            env=test_environment,
            domain="test.example.com",
            environment="test",
        )
        template = assertions.Template.from_stack(cert_stack)

        # Verify certificate is created
        template.resource_count_is("AWS::CertificateManager::Certificate", 1)

        # Verify DNS validation
        template.has_resource_properties(
            "AWS::CertificateManager::Certificate",
            {"ValidationMethod": "DNS"},
        )


class TestMultiAlbStack:
    """Test Multi-ALB stack for domain-based load balancing"""

    def test_alb_creation(self, cdk_app, test_environment):
        """Test ALBs are created for domains"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )

        # Create multi-ALB stack with mock certificate ARN (mapped by root zone)
        multi_alb_stack = MultiAlbStack(
            cdk_app,
            "TestMultiAlbStack",
            env=test_environment,
            vpc=network_stack.vpc,
            domains=["test.example.com"],
            alb_security_group=shared_stack.alb_security_group,
            environment="test",
            certificate_arns={
                "example.com": "arn:aws:acm:us-east-1:123456789012:certificate/test-cert-id"
            },
        )
        template = assertions.Template.from_stack(multi_alb_stack)

        # Verify ALB is created
        template.has_resource("AWS::ElasticLoadBalancingV2::LoadBalancer", {})

    def test_https_listener(self, cdk_app, test_environment):
        """Test HTTPS listeners are created"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )

        multi_alb_stack = MultiAlbStack(
            cdk_app,
            "TestMultiAlbStack2",
            env=test_environment,
            vpc=network_stack.vpc,
            domains=["test.example.com"],
            alb_security_group=shared_stack.alb_security_group,
            environment="test",
            certificate_arns={
                "example.com": "arn:aws:acm:us-east-1:123456789012:certificate/test-cert-id"
            },
        )
        template = assertions.Template.from_stack(multi_alb_stack)

        # Verify HTTPS listener
        template.has_resource_properties(
            "AWS::ElasticLoadBalancingV2::Listener",
            {"Port": 443, "Protocol": "HTTPS"},
        )

    def test_listener_certificates(self, cdk_app, test_environment):
        """Test listener has certificates attached"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )

        multi_alb_stack = MultiAlbStack(
            cdk_app,
            "TestMultiAlbStack3",
            env=test_environment,
            vpc=network_stack.vpc,
            domains=["test.example.com"],
            alb_security_group=shared_stack.alb_security_group,
            environment="test",
            certificate_arns={
                "example.com": "arn:aws:acm:us-east-1:123456789012:certificate/test-cert-id"
            },
        )
        template = assertions.Template.from_stack(multi_alb_stack)

        # Verify listener certificate is attached
        template.has_resource_properties(
            "AWS::ElasticLoadBalancingV2::Listener",
            {
                "Certificates": assertions.Match.array_with(
                    [
                        assertions.Match.object_like(
                            {
                                "CertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/test-cert-id"
                            }
                        )
                    ]
                )
            },
        )


class TestRedisStack:
    """Test Redis Serverless stack"""

    def test_redis_creation(self, cdk_app, test_environment):
        """Test Redis Serverless cache is created"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        redis_stack = RedisStack(
            cdk_app,
            "TestRedisStack",
            env=test_environment,
            vpc=network_stack.vpc,
            environment="test",
            max_storage_gb=1,
            max_ecpu=3000,
            snapshot_retention=1,
        )
        template = assertions.Template.from_stack(redis_stack)

        # Verify Redis Serverless cache is created
        template.has_resource("AWS::ElastiCache::ServerlessCache", {})


class TestDomainDnsStack:
    """Test Domain DNS stack for Route53 records"""

    def test_lambda_creation(self, cdk_app, test_environment):
        """Test Lambda function for Route53 record management is created"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )
        multi_alb_stack = MultiAlbStack(
            cdk_app,
            "TestMultiAlbStack4",
            env=test_environment,
            vpc=network_stack.vpc,
            domains=["test.example.com"],
            alb_security_group=shared_stack.alb_security_group,
            environment="test",
            certificate_arns={
                "example.com": "arn:aws:acm:us-east-1:123456789012:certificate/test-cert-id"
            },
        )

        # Create domain DNS stack
        dns_stack = DomainDnsStack(
            cdk_app,
            "TestDomainDnsStack",
            env=test_environment,
            domain_name="test.example.com",
            alb=list(multi_alb_stack.domain_to_alb.values())[0],
            mail_server="mail.example.com",
            dkim_selector="default",
            dkim_public_key="MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDdmsMArxUA48AxvmG2gm26Qr1lbhtt6r59AMhBMK/TgZLNHug0L8uM6nm12SSxY0kxZyp5cLPbtgN832ReoJ0sW6zZfedfPf1Ak1Z6H9Cxd3wB3zI3Gy8c6PsV9Wt0lYEWHALw2ANjf5Ru0otK3slBUz7yb7AgvUEHb1Bt6+aazQIDAQAB",
            spf_servers=["a:mail.example.com"],
            dmarc_rua="reports@example.com",
            dmarc_policy="quarantine",
        )
        template = assertions.Template.from_stack(dns_stack)

        # Verify Lambda function is created
        template.has_resource("AWS::Lambda::Function", {})

    def test_iam_role_for_lambda(self, cdk_app, test_environment):
        """Test IAM role for Lambda has Route53 permissions"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(
            cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc
        )
        multi_alb_stack = MultiAlbStack(
            cdk_app,
            "TestMultiAlbStack5",
            env=test_environment,
            vpc=network_stack.vpc,
            domains=["test.example.com"],
            alb_security_group=shared_stack.alb_security_group,
            environment="test",
            certificate_arns={
                "example.com": "arn:aws:acm:us-east-1:123456789012:certificate/test-cert-id"
            },
        )

        dns_stack = DomainDnsStack(
            cdk_app,
            "TestDomainDnsStack2",
            env=test_environment,
            domain_name="test.example.com",
            alb=list(multi_alb_stack.domain_to_alb.values())[0],
            mail_server="mail.example.com",
            dkim_selector="default",
            dkim_public_key="test-key",
        )
        template = assertions.Template.from_stack(dns_stack)

        # Verify IAM role exists
        template.has_resource("AWS::IAM::Role", {})

        # Verify Route53 permissions in policy
        template.has_resource_properties(
            "AWS::IAM::Policy",
            {
                "PolicyDocument": {
                    "Statement": assertions.Match.array_with(
                        [
                            assertions.Match.object_like(
                                {
                                    "Action": assertions.Match.array_with(
                                        [assertions.Match.string_like_regexp("route53:.*")]
                                    )
                                }
                            )
                        ]
                    )
                }
            },
        )
