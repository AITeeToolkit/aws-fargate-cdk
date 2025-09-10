from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_certificatemanager as acm,
)
from constructs import Construct

class WebAlbStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        cert: acm.ICertificate,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.alb = elbv2.ApplicationLoadBalancer(
            self, "StorefrontALB",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name="storefront-alb"
        )

        self.listener = self.alb.add_listener(
            "HttpsListener",
            port=443,
            certificates=[cert],
            protocol=elbv2.ApplicationProtocol.HTTPS,
            default_action=elbv2.ListenerAction.fixed_response(
                status_code=404,
                message_body="Not Found",
                content_type="text/plain"
            )
        )

    def add_web_service_target(self, service: elbv2.IApplicationLoadBalancerTarget) -> None:
        """Attach a FargateService to this ALB listener."""
        self.listener.add_targets(
            "WebServiceTargetGroup",
            port=3000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[service],
            priority=1,
            conditions=[elbv2.ListenerCondition.path_patterns(["/*"])]
        )