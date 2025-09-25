#!/usr/bin/env python3
"""
SQS DNS Publisher for AWS Fargate

Publishes DNS operations to SQS for batch processing.
Handles deduplication and batching for efficient DNS operations.
"""

import json
import logging
import os
import time
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class DNSOperationType:
    """DNS operation types."""
    DOMAIN_ACTIVATED = "domain_activated"
    DOMAIN_DEACTIVATED = "domain_deactivated"
    BATCH_PROCESS = "batch_process"


class SQSDNSPublisher:
    """
    SQS DNS Publisher for sending DNS operations to queues.
    """
    
    def __init__(
        self,
        queue_url: str = None,
        region_name: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None
    ):
        """
        Initialize SQS DNS publisher.
        
        Args:
            queue_url: SQS queue URL for DNS operations
            region_name: AWS region
            aws_access_key_id: AWS access key (optional, uses IAM role if not provided)
            aws_secret_access_key: AWS secret key (optional, uses IAM role if not provided)
        """
        self.queue_url = queue_url or os.environ.get('SQS_DNS_OPERATIONS_QUEUE_URL')
        self.region_name = region_name or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        self.aws_access_key_id = aws_access_key_id or os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        if not self.queue_url:
            raise ValueError("SQS_DNS_OPERATIONS_QUEUE_URL must be provided")
        
        self.sqs_client = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Establish connection to AWS SQS.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create SQS client
            session_kwargs = {'region_name': self.region_name}
            
            if self.aws_access_key_id and self.aws_secret_access_key:
                session_kwargs.update({
                    'aws_access_key_id': self.aws_access_key_id,
                    'aws_secret_access_key': self.aws_secret_access_key
                })
            
            self.sqs_client = boto3.client('sqs', **session_kwargs)
            
            self._connected = True
            logger.info(f"Connected to AWS SQS in region {self.region_name}")
            return True
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Configure IAM role or environment variables.")
            self._connected = False
            return False
            
        except Exception as e:
            logger.error(f"Failed to connect to AWS SQS: {e}")
            self._connected = False
            return False
    
    def publish_dns_event(
        self,
        operation_type: str,
        domain_name: str,
        active: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Publish a DNS event to SQS.
        
        Args:
            operation_type: Type of DNS operation
            domain_name: Domain name that changed
            active: 'Y' or 'N' for activation status
            metadata: Additional event metadata
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        if not self._connected:
            if not self.connect():
                logger.error("Cannot publish DNS event: not connected to SQS")
                return False
        
        # Create message payload
        message_data = {
            'operation_type': operation_type,
            'domain_name': domain_name,
            'active': active,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        
        try:
            # Send message to SQS with deduplication
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_data),
                MessageAttributes={
                    'operation_type': {
                        'StringValue': operation_type,
                        'DataType': 'String'
                    },
                    'domain_name': {
                        'StringValue': domain_name,
                        'DataType': 'String'
                    },
                    'active': {
                        'StringValue': active,
                        'DataType': 'String'
                    }
                },
                # Use domain name as deduplication ID to prevent duplicate processing
                MessageDeduplicationId=f"{domain_name}_{active}_{int(time.time() // 30)}",  # 30-second window
                MessageGroupId="dns_operations"  # FIFO queue group
            )
            
            message_id = response.get('MessageId')
            logger.info(f"Published DNS event {operation_type} for {domain_name} "
                       f"(active: {active}, message_id: {message_id})")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Failed to publish DNS event: {error_code} - {e}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error publishing DNS event: {e}")
            return False
    
    def publish_domain_activation(self, domain_name: str) -> bool:
        """
        Publish domain activation event.
        
        Args:
            domain_name: Domain that was activated
            
        Returns:
            bool: True if published successfully
        """
        return self.publish_dns_event(
            operation_type=DNSOperationType.DOMAIN_ACTIVATED,
            domain_name=domain_name,
            active='Y'
        )
    
    def publish_domain_deactivation(self, domain_name: str) -> bool:
        """
        Publish domain deactivation event.
        
        Args:
            domain_name: Domain that was deactivated
            
        Returns:
            bool: True if published successfully
        """
        return self.publish_dns_event(
            operation_type=DNSOperationType.DOMAIN_DEACTIVATED,
            domain_name=domain_name,
            active='N'
        )


# Convenience functions for easy integration
def publish_domain_change(domain_name: str, active: str) -> bool:
    """
    Convenience function to publish domain status change.
    
    Args:
        domain_name: Domain that changed
        active: 'Y' for activated, 'N' for deactivated
        
    Returns:
        bool: True if published successfully
    """
    publisher = SQSDNSPublisher()
    
    if active == 'Y':
        return publisher.publish_domain_activation(domain_name)
    elif active == 'N':
        return publisher.publish_domain_deactivation(domain_name)
    else:
        logger.error(f"Invalid active status: {active}")
        return False


if __name__ == "__main__":
    # Example usage
    publisher = SQSDNSPublisher()
    
    # Test connection
    if publisher.connect():
        # Example: Domain activation
        success = publisher.publish_domain_activation("example.com")
        print(f"Domain activation published: {success}")
    else:
        print("Failed to connect to SQS")
