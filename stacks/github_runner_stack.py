from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from constructs import Construct


class GitHubRunnerStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Security group for GitHub runner
        # No inbound rules needed - SSM Session Manager uses outbound HTTPS only
        runner_sg = ec2.SecurityGroup(
            self,
            "RunnerSecurityGroup",
            vpc=vpc,
            description="GitHub Actions runner security group - shared across all environments",
            allow_all_outbound=True,
        )

        # IAM role for runner
        runner_role = iam.Role(
            self,
            "RunnerRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
            ],
        )

        # Add CDK deployment permissions
        runner_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "cloudformation:*",
                    "s3:*",
                    "ecr:*",
                    "ecs:*",
                    "ec2:*",
                    "elasticloadbalancing:*",
                    "route53:*",
                    "acm:*",
                    "logs:*",
                    "ssm:*",
                    "secretsmanager:*",
                    "iam:*",
                    "rds:*",
                    "sns:*",
                    "sqs:*",
                ],
                resources=["*"],
            )
        )

        # User data to install GitHub Actions runner
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "#!/bin/bash",
            "set -e",
            "",
            "# Update system",
            "yum update -y",
            "",
            "# Install dependencies",
            "yum install -y git curl jq docker",
            "systemctl start docker",
            "systemctl enable docker",
            "usermod -aG docker ec2-user",
            "",
            "# Install Node.js (for CDK)",
            "curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -",
            "yum install -y nodejs",
            "",
            "# Install AWS CDK",
            "npm install -g aws-cdk",
            "",
            "# Install Python and pip",
            "yum install -y python3 python3-pip postgresql-devel gcc",
            "",
            "# Create runner user",
            "useradd -m -s /bin/bash runner",
            "usermod -aG docker runner",
            "",
            "# Download and install GitHub Actions runner",
            "cd /home/runner",
            "mkdir actions-runner && cd actions-runner",
            "",
            "# Get latest runner version",
            "RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | jq -r '.tag_name' | sed 's/v//')",
            "",
            "# Download runner",
            "tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz",
            "",
            "# Set ownership",
            "chown -R runner:runner /home/runner/actions-runner",
            "",
            # Store registration token in SSM (you'll need to manually configure this)
            "",
            "# Install as service (after manual configuration)",
            'echo "After configuration, run: cd /home/runner/actions-runner && sudo ./svc.sh install runner && sudo ./svc.sh start" >> /home/runner/setup-instructions.txt',
        )

        # EC2 instance (in public subnet for internet access - no NAT gateway needed)
        # Security group restricts inbound access, only allows outbound for downloads
        self.instance = ec2.Instance(
            self,
            "GitHubRunner",
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=runner_sg,
            role=runner_role,
            user_data=user_data,
        )
        CfnOutput(
            self,
            "RunnerInstanceId",
            value=self.instance.instance_id,
            description="GitHub Actions runner instance ID",
        )

        CfnOutput(
            self,
            "RunnerConnectCommand",
            value=f"aws ssm start-session --target {self.instance.instance_id}",
            description="Command to connect to runner via SSM",
        )
