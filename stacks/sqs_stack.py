import aws_cdk as cdk
from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as sns_subs
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class SQSStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, *, environment: str = "dev", **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Dead Letter Queue for failed messages (standard)
        self.dlq = sqs.Queue(
            self,
            "StorefrontDLQ",
            queue_name=f"storefront-{environment}-dlq",
            retention_period=Duration.days(14),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # Dead Letter Queue for FIFO queues (must be FIFO)
        self.fifo_dlq = sqs.Queue(
            self,
            "StorefrontFifoDLQ",
            queue_name=f"storefront-{environment}-fifo-dlq.fifo",
            fifo=True,
            retention_period=Duration.days(14),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # Main processing queue
        self.main_queue = sqs.Queue(
            self,
            "StorefrontMainQueue",
            queue_name=f"storefront-{environment}-main-queue",
            visibility_timeout=Duration.minutes(5),
            retention_period=Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=3, queue=self.dlq),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # High priority queue for urgent tasks
        self.priority_queue = sqs.Queue(
            self,
            "StorefrontPriorityQueue",
            queue_name=f"storefront-{environment}-priority-queue",
            visibility_timeout=Duration.minutes(2),
            retention_period=Duration.days(7),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=2, queue=self.dlq),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # Email processing queue
        self.email_queue = sqs.Queue(
            self,
            "StorefrontEmailQueue",
            queue_name=f"storefront-{environment}-email-queue",
            visibility_timeout=Duration.minutes(3),
            retention_period=Duration.days(7),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=3, queue=self.dlq),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # Image processing queue (for product images, thumbnails, etc.)
        self.image_processing_queue = sqs.Queue(
            self,
            "StorefrontImageProcessingQueue",
            queue_name=f"storefront-{environment}-image-processing-queue",
            visibility_timeout=Duration.minutes(10),  # Longer timeout for image processing
            retention_period=Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=2, queue=self.dlq),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # FIFO queue for ordered processing (e.g., order processing)
        self.order_processing_queue = sqs.Queue(
            self,
            "StorefrontOrderProcessingQueue",
            queue_name=f"storefront-{environment}-order-processing-queue.fifo",
            fifo=True,
            content_based_deduplication=True,
            visibility_timeout=Duration.minutes(5),
            retention_period=Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=3, queue=self.fifo_dlq),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # SNS Topic for domain changes (fan-out pattern)
        # FIFO topic to maintain ordering and deduplication
        self.domain_changes_topic = sns.Topic(
            self,
            "DomainChangesTopic",
            topic_name=f"storefront-{environment}-domain-changes.fifo",
            display_name="Domain Changes Notifications",
            fifo=True,
            content_based_deduplication=False,  # We provide explicit deduplication IDs
        )

        # DNS operations queue (FIFO for deduplication)
        self.dns_operations_queue = sqs.Queue(
            self,
            "StorefrontDnsOperationsQueue",
            queue_name=f"storefront-{environment}-dns-operations-queue.fifo",
            fifo=True,
            content_based_deduplication=False,  # We provide explicit deduplication IDs
            visibility_timeout=Duration.minutes(5),
            retention_period=Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=3, queue=self.fifo_dlq),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # Subscribe DNS operations queue to domain changes topic
        self.domain_changes_topic.add_subscription(
            sns_subs.SqsSubscription(
                self.dns_operations_queue,
                raw_message_delivery=True,  # Deliver SNS message body directly to SQS
            )
        )

        # Store queue URLs in SSM Parameter Store for easy access
        ssm.StringParameter(
            self,
            "MainQueueUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/main-queue-url",
            string_value=self.main_queue.queue_url,
            description="Main SQS queue URL for general processing",
        )

        ssm.StringParameter(
            self,
            "PriorityQueueUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/priority-queue-url",
            string_value=self.priority_queue.queue_url,
            description="Priority SQS queue URL for urgent tasks",
        )

        ssm.StringParameter(
            self,
            "EmailQueueUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/email-queue-url",
            string_value=self.email_queue.queue_url,
            description="Email processing SQS queue URL",
        )

        ssm.StringParameter(
            self,
            "ImageProcessingQueueUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/image-processing-queue-url",
            string_value=self.image_processing_queue.queue_url,
            description="Image processing SQS queue URL",
        )

        ssm.StringParameter(
            self,
            "OrderProcessingQueueUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/order-processing-queue-url",
            string_value=self.order_processing_queue.queue_url,
            description="Order processing FIFO SQS queue URL",
        )

        ssm.StringParameter(
            self,
            "DnsOperationsQueueUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/dns-operations-queue-url",
            string_value=self.dns_operations_queue.queue_url,
            description="DNS operations FIFO SQS queue URL",
        )

        ssm.StringParameter(
            self,
            "DomainChangesTopicArnParameter",
            parameter_name=f"/storefront-{environment}/sns/domain-changes-topic-arn",
            string_value=self.domain_changes_topic.topic_arn,
            description="SNS topic ARN for domain change notifications",
        )

        ssm.StringParameter(
            self,
            "DLQUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/dlq-url",
            string_value=self.dlq.queue_url,
            description="Dead Letter Queue URL for failed messages",
        )

        ssm.StringParameter(
            self,
            "FifoDLQUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/fifo-dlq-url",
            string_value=self.fifo_dlq.queue_url,
            description="FIFO Dead Letter Queue URL for failed FIFO messages",
        )

        # Create IAM policy for SQS and SNS access
        self.sqs_policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sqs:SendMessage",
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                        "sqs:GetQueueUrl",
                        "sqs:ChangeMessageVisibility",
                    ],
                    resources=[
                        self.main_queue.queue_arn,
                        self.priority_queue.queue_arn,
                        self.email_queue.queue_arn,
                        self.image_processing_queue.queue_arn,
                        self.order_processing_queue.queue_arn,
                        self.dns_operations_queue.queue_arn,
                        self.dlq.queue_arn,
                        self.fifo_dlq.queue_arn,
                    ],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sns:Publish",
                        "sns:Subscribe",
                        "sns:GetTopicAttributes",
                    ],
                    resources=[
                        self.domain_changes_topic.topic_arn,
                    ],
                ),
            ]
        )

        # Create a managed policy for easy attachment to roles
        self.sqs_managed_policy = iam.ManagedPolicy(
            self,
            "SQSAccessPolicy",
            managed_policy_name=f"StorefrontSQSAccess-{environment}",
            document=self.sqs_policy,
            description="Policy for Storefront services to access SQS queues",
        )

        # Output important values
        cdk.CfnOutput(
            self,
            "MainQueueUrl",
            value=self.main_queue.queue_url,
            description="Main SQS Queue URL",
        )

        cdk.CfnOutput(
            self,
            "PriorityQueueUrl",
            value=self.priority_queue.queue_url,
            description="Priority SQS Queue URL",
        )

        cdk.CfnOutput(
            self,
            "EmailQueueUrl",
            value=self.email_queue.queue_url,
            description="Email Processing SQS Queue URL",
        )

        cdk.CfnOutput(
            self,
            "ImageProcessingQueueUrl",
            value=self.image_processing_queue.queue_url,
            description="Image Processing SQS Queue URL",
        )

        cdk.CfnOutput(
            self,
            "OrderProcessingQueueUrl",
            value=self.order_processing_queue.queue_url,
            description="Order Processing FIFO SQS Queue URL",
        )

        cdk.CfnOutput(
            self,
            "DnsOperationsQueueUrl",
            value=self.dns_operations_queue.queue_url,
            description="DNS Operations FIFO SQS Queue URL",
        )

        cdk.CfnOutput(
            self,
            "DomainChangesTopicArn",
            value=self.domain_changes_topic.topic_arn,
            description="SNS Topic ARN for Domain Changes",
        )
