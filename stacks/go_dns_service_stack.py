from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as targets
from constructs import Construct

from cdk_constructs.fargate_service_construct import FargateServiceConstruct


class GoDnsServiceStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        cluster: ecs.ICluster,
        image_uri: str,
        environment: str,
        ecs_task_security_group: ec2.ISecurityGroup = None,
        service_name: str = "go-dns-service",
        desired_count: int = 1,
        domain: str = None,
        alb: elbv2.IApplicationLoadBalancer = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment variables for the go-dns service
        go_dns_environment = {
            "PORT": "8080",
            "ENVIRONMENT": environment,
        }

        # Create the Fargate service using the construct (no ALB attachment)
        construct_params = {
            "cluster": cluster,
            "vpc": vpc,
            "container_image": ecs.ContainerImage.from_registry(image_uri),
            "container_port": 8080,
            "service_name": service_name,
            "environment": go_dns_environment,
            "desired_count": desired_count,
        }

        # Add security groups if provided
        if ecs_task_security_group:
            construct_params["security_groups"] = [ecs_task_security_group]

        self.service = FargateServiceConstruct(self, "go-dns-service", **construct_params)

        # Create Route53 A record if domain and ALB are provided
        if domain and alb:
            # Extract root domain from subdomain
            domain_parts = domain.split(".")
            root_domain = ".".join(domain_parts[-2:])

            # Look up hosted zone
            zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=root_domain)

            # Create A record pointing to ALB
            route53.ARecord(
                self,
                "ARecord",
                zone=zone,
                record_name=domain,
                target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(alb)),
            )
