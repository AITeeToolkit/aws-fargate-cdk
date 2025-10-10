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

        # Database operations queue - handles domain table updates
        self.database_operations_queue = sqs.Queue(
            self,
            "DatabaseOperationsQueue",
            queue_name=f"storefront-{environment}-database-operations-queue.fifo",
            fifo=True,
            content_based_deduplication=False,
            visibility_timeout=Duration.minutes(2),
            retention_period=Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=3, queue=self.fifo_dlq),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # Route53 operations queue - handles DNS zone and record management
        self.route53_operations_queue = sqs.Queue(
            self,
            "Route53OperationsQueue",
            queue_name=f"storefront-{environment}-route53-operations-queue.fifo",
            fifo=True,
            content_based_deduplication=False,
            visibility_timeout=Duration.minutes(5),
            retention_period=Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=3, queue=self.fifo_dlq),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # GitHub workflow queue - handles workflow triggers
        self.github_workflow_queue = sqs.Queue(
            self,
            "GitHubWorkflowQueue",
            queue_name=f"storefront-{environment}-github-workflow-queue.fifo",
            fifo=True,
            content_based_deduplication=False,
            visibility_timeout=Duration.minutes(3),
            retention_period=Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=3, queue=self.fifo_dlq),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # Email queue - handles email sending via postfix-api
        self.email_queue = sqs.Queue(
            self,
            "EmailQueue",
            queue_name=f"storefront-{environment}-email-queue",
            fifo=False,  # Standard queue for email processing
            visibility_timeout=Duration.minutes(5),
            retention_period=Duration.days(14),
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" else RemovalPolicy.RETAIN
            ),
        )

        # Subscribe all queues to domain changes topic (fan-out pattern)
        self.domain_changes_topic.add_subscription(
            sns_subs.SqsSubscription(
                self.database_operations_queue,
                raw_message_delivery=True,
            )
        )
        self.domain_changes_topic.add_subscription(
            sns_subs.SqsSubscription(
                self.route53_operations_queue,
                raw_message_delivery=True,
            )
        )
        self.domain_changes_topic.add_subscription(
            sns_subs.SqsSubscription(
                self.github_workflow_queue,
                raw_message_delivery=True,
            )
        )

        # Store control plane queue URLs in SSM Parameter Store
        ssm.StringParameter(
            self,
            "DatabaseOperationsQueueUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/database-operations-queue-url",
            string_value=self.database_operations_queue.queue_url,
            description="Database operations FIFO SQS queue URL",
        )

        ssm.StringParameter(
            self,
            "Route53OperationsQueueUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/route53-operations-queue-url",
            string_value=self.route53_operations_queue.queue_url,
            description="Route53 operations FIFO SQS queue URL",
        )

        ssm.StringParameter(
            self,
            "GitHubWorkflowQueueUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/github-workflow-queue-url",
            string_value=self.github_workflow_queue.queue_url,
            description="GitHub workflow trigger FIFO SQS queue URL",
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
            "FifoDLQUrlParameter",
            parameter_name=f"/storefront-{environment}/sqs/fifo-dlq-url",
            string_value=self.fifo_dlq.queue_url,
            description="FIFO Dead Letter Queue URL for failed FIFO messages",
        )

        ssm.StringParameter(
            self,
            "EmailQueueUrlParameter",
            parameter_name="/postfix-api/sqs-email-queue-url",
            string_value=self.email_queue.queue_url,
            description="Email queue URL for postfix-api",
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
                        self.database_operations_queue.queue_arn,
                        self.route53_operations_queue.queue_arn,
                        self.github_workflow_queue.queue_arn,
                        self.email_queue.queue_arn,
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

        # Output control plane queue URLs
        cdk.CfnOutput(
            self,
            "DatabaseOperationsQueueUrl",
            value=self.database_operations_queue.queue_url,
            description="Database Operations FIFO SQS Queue URL",
        )

        cdk.CfnOutput(
            self,
            "Route53OperationsQueueUrl",
            value=self.route53_operations_queue.queue_url,
            description="Route53 Operations FIFO SQS Queue URL",
        )

        cdk.CfnOutput(
            self,
            "GitHubWorkflowQueueUrl",
            value=self.github_workflow_queue.queue_url,
            description="GitHub Workflow FIFO SQS Queue URL",
        )

        cdk.CfnOutput(
            self,
            "DomainChangesTopicArn",
            value=self.domain_changes_topic.topic_arn,
            description="SNS Topic ARN for Domain Changes",
        )

        cdk.CfnOutput(
            self,
            "EmailQueueUrl",
            value=self.email_queue.queue_url,
            description="Email Queue URL for postfix-api",
        )
