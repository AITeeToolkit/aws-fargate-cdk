"""
Test configuration and fixtures for AWS Fargate CDK tests
"""

import os

import aws_cdk as cdk
import boto3
import pytest
from aws_cdk import App, Environment
from moto import mock_aws


@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    """Mock AWS credentials for testing"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_REGION"] = "us-east-1"  # Some services need this specifically


@pytest.fixture
def cdk_app():
    """Create a CDK app for testing"""
    return cdk.App()


@pytest.fixture
def test_environment():
    """Test environment configuration"""
    return cdk.Environment(account="123456789012", region="us-east-1")


@pytest.fixture(autouse=True)
def mock_aws_services():
    """Mock AWS services for testing"""
    with mock_aws():
        # Create mock ECR client to simulate no existing repositories
        ecr_client = boto3.client("ecr", region_name="us-east-1")
        yield


@pytest.fixture
def test_domains():
    """Test domains configuration"""
    return ["test1.example.com", "test2.example.com"]


@pytest.fixture
def test_tags():
    """Test image tags"""
    return {
        "listener": "v1.0.0-test",
        "dns_worker": "v1.0.0-test",
        "api": "v1.0.0-test",
        "web": "v1.0.0-test",
    }
