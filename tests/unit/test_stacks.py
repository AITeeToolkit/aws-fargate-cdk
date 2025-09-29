"""
Unit tests for CDK stacks
"""
import pytest
import aws_cdk as cdk
from aws_cdk import assertions
from stacks.network_stack import NetworkStack
from stacks.shared_stack import SharedStack
from stacks.database_stack import DatabaseStack
from stacks.listener_service_stack import ListenerServiceStack
from stacks.dns_worker_service_stack import DNSWorkerServiceStack
from stacks.ecr_stack import ECRStack
from stacks.opensearch_stack import OpenSearchStack
from stacks.sqs_stack import SQSStack
from stacks.api_service_stack import APIServiceStack
from stacks.web_service_stack import WebServiceStack


class TestNetworkStack:
    """Test NetworkStack creation and resources"""
    
    def test_vpc_creation(self, cdk_app, test_environment):
        """Test VPC is created with correct configuration"""
        stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        template = assertions.Template.from_stack(stack)
        
        # Verify VPC is created
        template.has_resource_properties("AWS::EC2::VPC", {
            "CidrBlock": "10.0.0.0/16",
            "EnableDnsHostnames": True,
            "EnableDnsSupport": True
        })
        
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
        shared_stack = SharedStack(cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc)
        template = assertions.Template.from_stack(shared_stack)
        
        template.has_resource("AWS::ECS::Cluster", {})
        
    def test_security_groups(self, cdk_app, test_environment):
        """Test security groups are created with correct rules"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc)
        template = assertions.Template.from_stack(shared_stack)
        
        # Should have ALB, ECS task, and VPC endpoint security groups
        template.resource_count_is("AWS::EC2::SecurityGroup", 3)
        
        # Verify ALB security group allows HTTPS
        template.has_resource_properties("AWS::EC2::SecurityGroup", {
            "GroupDescription": "Security group for Application Load Balancer",
            "SecurityGroupIngress": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 443,
                    "ToPort": 443,
                    "CidrIp": "0.0.0.0/0"
                }
            ]
        })
        
        # Verify ECS task security group exists
        template.has_resource_properties("AWS::EC2::SecurityGroup", {
            "GroupDescription": "Security group for ECS tasks"
        })
        
        # Verify VPC endpoint security group exists
        template.has_resource_properties("AWS::EC2::SecurityGroup", {
            "GroupDescription": "Security group for VPC endpoints"
        })


class TestDatabaseStack:
    """Test DatabaseStack RDS and secrets"""
    
    def test_rds_instance_creation(self, cdk_app, test_environment):
        """Test RDS instance is created with correct configuration"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        db_stack = DatabaseStack(cdk_app, "TestDatabaseStack", env=test_environment, 
                                vpc=network_stack.vpc, environment="test",
                                multi_az=False, instance_class="db.t3.micro",
                                deletion_protection=False)
        template = assertions.Template.from_stack(db_stack)
        
        template.has_resource_properties("AWS::RDS::DBInstance", {
            "Engine": "postgres",
            "MultiAZ": False,  # Single AZ for test environment
            "StorageEncrypted": True,
            "DeletionProtection": False
        })
        
    def test_secrets_manager(self, cdk_app, test_environment):
        """Test Secrets Manager secret is created"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        db_stack = DatabaseStack(cdk_app, "TestDatabaseStack", env=test_environment,
                                vpc=network_stack.vpc, environment="test",
                                multi_az=False, instance_class="db.t3.micro",
                                deletion_protection=False)
        template = assertions.Template.from_stack(db_stack)
        
        template.has_resource("AWS::SecretsManager::Secret", {})
        
    def test_environment_specific_config(self, cdk_app, test_environment):
        """Test environment-specific database configuration"""
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        
        # Test production configuration
        prod_db_stack = DatabaseStack(cdk_app, "ProdDatabaseStack", env=test_environment,
                                     vpc=network_stack.vpc, environment="prod",
                                     multi_az=False, instance_class="db.t3.medium",
                                     deletion_protection=True)
        prod_template = assertions.Template.from_stack(prod_db_stack)
        
        prod_template.has_resource_properties("AWS::RDS::DBInstance", {
            "DeletionProtection": True,
            "MultiAZ": False  # Updated to reflect single AZ configuration
        })


class TestServiceStacks:
    """Test service stacks (Listener and DNS Worker)"""
    
    def test_listener_service_creation(self, cdk_app, test_environment, test_tags):
        """Test Listener service stack creates ECS service"""
        # Create dependencies
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc)
        ecr_stack = ECRStack(cdk_app, "TestECRStack", env=test_environment, 
                            repository_names=["api", "web", "listener", "dns-worker"])
        db_stack = DatabaseStack(cdk_app, "TestDatabaseStack", env=test_environment,
                                vpc=network_stack.vpc, environment="test",
                                multi_az=False, instance_class="db.t3.micro",
                                deletion_protection=False)
        
        # Create listener service
        listener_stack = ListenerServiceStack(
            cdk_app, "TestListenerStack",
            env=test_environment,
            vpc=network_stack.vpc,
            cluster=shared_stack.cluster,
            image_uri=f"{ecr_stack.repositories['listener'].repository_uri}:{test_tags['listener']}",
            db_secret=db_stack.secret,
            environment="test",
            ecs_task_security_group=shared_stack.ecs_task_sg,
            service_name="listener-service",
            sqs_managed_policy=None  # Mock for test
        )
        
        template = assertions.Template.from_stack(listener_stack)
        
        # Verify ECS service is created
        template.has_resource("AWS::ECS::Service", {})
        template.has_resource("AWS::ECS::TaskDefinition", {})
        
    def test_dns_worker_service_creation(self, cdk_app, test_environment, test_tags):
        """Test DNS Worker service stack creates ECS service"""
        # Create dependencies
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc)
        ecr_stack = ECRStack(cdk_app, "TestECRStack", env=test_environment,
                            repository_names=["api", "web", "listener", "dns-worker"])
        db_stack = DatabaseStack(cdk_app, "TestDatabaseStack", env=test_environment,
                                vpc=network_stack.vpc, environment="test",
                                multi_az=False, instance_class="db.t3.micro",
                                deletion_protection=False)
        
        # Create DNS worker service  
        dns_worker_stack = DNSWorkerServiceStack(
            cdk_app, "TestDNSWorkerStack",
            env=test_environment,
            vpc=network_stack.vpc,
            cluster=shared_stack.cluster,
            image_uri=f"{ecr_stack.repositories['dns-worker'].repository_uri}:{test_tags['dns_worker']}",
            environment="test",
            ecs_task_security_group=shared_stack.ecs_task_sg,
            service_name="dns-worker-service",
            db_secret=db_stack.secret,
            sqs_managed_policy=None  # Mock for test
        )
        
        template = assertions.Template.from_stack(dns_worker_stack)
        
        # Verify ECS service is created
        template.has_resource("AWS::ECS::Service", {})
        template.has_resource("AWS::ECS::TaskDefinition", {})


class TestECRStack:
    """Test ECR repository creation"""
    
    def test_ecr_repositories_creation(self, cdk_app, test_environment, mock_aws_services):
        """Test ECR repositories are created for all services"""
        # ECR stack uses boto3 to check existing repos, so we need mocked AWS
        ecr_stack = ECRStack(
            cdk_app, "TestECRStack",
            env=test_environment,
            repository_names=["api", "web", "listener", "dns-worker"]
        )
        template = assertions.Template.from_stack(ecr_stack)
        
        # ECR stack creates repos only if they don't exist (uses boto3)
        # In test environment with mocked AWS, repos won't exist so they'll be created
        template.resource_count_is("AWS::ECR::Repository", 4)
        
        # Verify repositories have lifecycle policies
        template.has_resource_properties("AWS::ECR::Repository", {
            "LifecyclePolicy": {
                "LifecyclePolicyText": assertions.Match.string_like_regexp(r".*tagStatus.*")
            }
        })
        
    def test_ecr_repositories_dict(self, cdk_app, test_environment, mock_aws_services):
        """Test ECR repositories are accessible via repositories dict"""
        ecr_stack = ECRStack(
            cdk_app, "TestECRStack",
            env=test_environment,
            repository_names=["api", "web", "listener", "dns-worker"]
        )
        
        # Verify all repositories are accessible
        assert "api" in ecr_stack.repositories
        assert "web" in ecr_stack.repositories
        assert "listener" in ecr_stack.repositories
        assert "dns-worker" in ecr_stack.repositories


class TestOpenSearchStack:
    """Test OpenSearch domain creation"""
    
    def test_opensearch_domain_creation(self, cdk_app, test_environment):
        """Test OpenSearch domain is created with correct configuration"""
        opensearch_stack = OpenSearchStack(
            cdk_app, "TestOpenSearchStack",
            env=test_environment,
            environment="test"
        )
        template = assertions.Template.from_stack(opensearch_stack)
        
        # Verify OpenSearch domain is created (uses AWS::OpenSearchService::Domain)
        template.has_resource("AWS::OpenSearchService::Domain", {})
        
        # Just verify basic properties exist
        template.has_resource_properties("AWS::OpenSearchService::Domain", {
            "EngineVersion": "OpenSearch_2.3"
        })
        
    def test_opensearch_iam_role(self, cdk_app, test_environment):
        """Test OpenSearch IAM role is created"""
        opensearch_stack = OpenSearchStack(
            cdk_app, "TestOpenSearchStack",
            env=test_environment,
            environment="test"
        )
        template = assertions.Template.from_stack(opensearch_stack)
        
        # Verify IAM roles are created (3 total: fargate role + service role + CDK-generated role)
        template.resource_count_is("AWS::IAM::Role", 3)
        
    def test_opensearch_basic_resources(self, cdk_app, test_environment):
        """Test basic OpenSearch resources are created"""
        opensearch_stack = OpenSearchStack(
            cdk_app, "TestOpenSearchStack",
            env=test_environment,
            environment="test"
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
        sqs_stack = SQSStack(
            cdk_app, "TestSQSStack",
            env=test_environment,
            environment="test"
        )
        template = assertions.Template.from_stack(sqs_stack)
        
        # Should create 8 queues: 6 main queues + 2 DLQs
        # (main, priority, email, image_processing, order_processing, dns_operations, dlq, fifo_dlq)
        template.resource_count_is("AWS::SQS::Queue", 8)
        
        # Verify queue has dead letter queue configuration
        template.has_resource_properties("AWS::SQS::Queue", {
            "RedrivePolicy": {
                "deadLetterTargetArn": assertions.Match.any_value(),
                "maxReceiveCount": 3
            }
        })
        
        # Verify FIFO queues are created
        template.has_resource_properties("AWS::SQS::Queue", {
            "FifoQueue": True,
            "ContentBasedDeduplication": True
        })
        
    def test_sqs_managed_policy(self, cdk_app, test_environment):
        """Test SQS managed policy is created"""
        sqs_stack = SQSStack(
            cdk_app, "TestSQSStack",
            env=test_environment,
            environment="test"
        )
        template = assertions.Template.from_stack(sqs_stack)
        
        # Verify managed policy for SQS access
        template.has_resource("AWS::IAM::ManagedPolicy", {})


class TestAPIServiceStack:
    """Test API service stack"""
    
    def test_api_service_creation(self, cdk_app, test_environment, test_tags):
        """Test API service stack creates ECS service"""
        # Create dependencies
        network_stack = NetworkStack(cdk_app, "TestNetworkStack", env=test_environment)
        shared_stack = SharedStack(cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc)
        ecr_stack = ECRStack(cdk_app, "TestECRStack", env=test_environment,
                            repository_names=["api", "web", "listener", "dns-worker"])
        db_stack = DatabaseStack(cdk_app, "TestDatabaseStack", env=test_environment,
                                vpc=network_stack.vpc, environment="test",
                                multi_az=False, instance_class="db.t3.micro",
                                deletion_protection=False)
        opensearch_stack = OpenSearchStack(cdk_app, "TestOpenSearchStack", env=test_environment, environment="test")
        sqs_stack = SQSStack(cdk_app, "TestSQSStack", env=test_environment, environment="test")
        
        # Create API service
        api_stack = APIServiceStack(
            cdk_app, "TestAPIStack",
            env=test_environment,
            vpc=network_stack.vpc,
            cluster=shared_stack.cluster,
            image_uri=f"{ecr_stack.repositories['api'].repository_uri}:{test_tags['api']}",
            db_secret=db_stack.secret,
            environment="test",
            ecs_task_security_group=shared_stack.ecs_task_sg,
            service_name="api-service",
            opensearch_role=opensearch_stack.fargate_opensearch_role,
            sqs_managed_policy=sqs_stack.sqs_managed_policy
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
        shared_stack = SharedStack(cdk_app, "TestSharedStack", env=test_environment, vpc=network_stack.vpc)
        ecr_stack = ECRStack(cdk_app, "TestECRStack", env=test_environment,
                            repository_names=["api", "web", "listener", "dns-worker"])
        db_stack = DatabaseStack(cdk_app, "TestDatabaseStack", env=test_environment,
                                vpc=network_stack.vpc, environment="test",
                                multi_az=False, instance_class="db.t3.micro",
                                deletion_protection=False)
        opensearch_stack = OpenSearchStack(cdk_app, "TestOpenSearchStack", env=test_environment, environment="test")
        
        # Create Web service
        web_stack = WebServiceStack(
            cdk_app, "TestWebStack",
            env=test_environment,
            vpc=network_stack.vpc,
            cluster=shared_stack.cluster,
            image_uri=f"{ecr_stack.repositories['web'].repository_uri}:{test_tags['web']}",
            db_secret=db_stack.secret,
            environment="test",
            ecs_task_security_group=shared_stack.ecs_task_sg,
            service_name="web-service",
            opensearch_role=opensearch_stack.fargate_opensearch_role
        )
        
        template = assertions.Template.from_stack(web_stack)
        
        # Verify ECS service is created
        template.has_resource("AWS::ECS::Service", {})
        template.has_resource("AWS::ECS::TaskDefinition", {})
