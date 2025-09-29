from aws_cdk import Stack
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_route53 as route53
from aws_cdk.aws_route53_targets import LoadBalancerTarget
from constructs import Construct


class Route53Stack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domain_name: str,
        alb: elbv2.IApplicationLoadBalancer,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Look up existing hosted zone
        zone = route53.HostedZone.from_lookup(
            self, "HostedZone", domain_name=domain_name
        )

        # Root domain ALIAS record to ALB
        route53.ARecord(
            self,
            "RootAliasRecord",
            zone=zone,
            record_name=domain_name,
            target=route53.RecordTarget.from_alias(LoadBalancerTarget(alb)),
        )

        # Subdomain (e.g., dev) ALIAS record to ALB
        route53.ARecord(
            self,
            "DevAliasRecord",
            zone=zone,
            record_name=f"dev.{domain_name}",
            target=route53.RecordTarget.from_alias(LoadBalancerTarget(alb)),
        )
