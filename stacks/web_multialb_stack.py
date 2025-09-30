from aws_cdk import Duration, Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_route53 as route53
from constructs import Construct


def chunk_list(data, chunk_size):
    """Yield successive chunk_size-sized chunks from list."""
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


class MultiAlbStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.IVpc,
        domains: list[str],  # just a list of domains now
        alb_security_group: ec2.ISecurityGroup,
        environment: str = "dev",
        **kwargs,
    ):
        """
        domains: ["foo.com", "bar.net", "sub.example.org", ...]
        Each domain's hosted zone will be auto-discovered with from_lookup.
        """
        super().__init__(scope, construct_id, **kwargs)

        self.domain_to_alb: dict[str, elbv2.ApplicationLoadBalancer] = {}
        self.listeners: list[elbv2.ApplicationListener] = []
        self.alb_security_group = alb_security_group

        # Split into ~50 domains per ALB
        for idx, domain_chunk in enumerate(chunk_list(domains, 50), start=1):
            alb = elbv2.ApplicationLoadBalancer(
                self,
                f"Alb{idx}",
                vpc=vpc,
                internet_facing=True,
                security_group=self.alb_security_group,
                load_balancer_name=f"web-alb-{environment}-{idx}",
            )

            listener = alb.add_listener(
                f"HttpsListener{idx}",
                port=443,
                ssl_policy=elbv2.SslPolicy.RECOMMENDED_TLS,
                open=True,
            )
            self.listeners.append(listener)

            # Default catch-all → 403
            listener.add_action(
                f"Default403-{idx}",
                action=elbv2.ListenerAction.fixed_response(
                    status_code=403, message_body="Forbidden"
                ),
            )

            # Group domains by root zone to create wildcard certificates
            zones_map = {}  # root_zone -> [domains]
            for domain in domain_chunk:
                root_zone_name = ".".join(domain.split(".")[-2:])
                if root_zone_name not in zones_map:
                    zones_map[root_zone_name] = []
                zones_map[root_zone_name].append(domain)
                self.domain_to_alb[domain] = alb

            # Create one wildcard cert per root zone
            certs = []
            for root_zone_name, domains in zones_map.items():
                # Look up existing hosted zone
                zone = route53.HostedZone.from_lookup(
                    self, f"Zone-{root_zone_name.replace('.', '-')}-{idx}",
                    domain_name=root_zone_name
                )

                # Create wildcard certificate for this zone
                cert = acm.Certificate(
                    self,
                    f"WildcardCert-{root_zone_name.replace('.', '-')}-{idx}",
                    domain_name=f"*.{root_zone_name}",
                    subject_alternative_names=[root_zone_name],  # Also cover root domain
                    validation=acm.CertificateValidation.from_dns(zone),
                )

                certs.append(elbv2.ListenerCertificate(cert.certificate_arn))

            # Attach all certs for this chunk
            listener.add_certificates(f"Certs-{idx}", certs)

    def attach_service(self, service: ecs.FargateService, port: int = 3000):
        """
        Attach ECS service to all ALBs/listeners.
        For now, creates one rule per listener with all hostnames for that ALB.
        """
        for idx, listener in enumerate(self.listeners, start=1):
            domains_for_this_listener = [
                d
                for d, alb in self.domain_to_alb.items()
                if alb == listener.load_balancer
            ]
            listener.add_targets(
                f"WebTargets-{idx}",
                port=port,
                protocol=elbv2.ApplicationProtocol.HTTP,
                targets=[service],
                conditions=[
                    elbv2.ListenerCondition.host_headers(domains_for_this_listener)
                ],
                priority=1000 + idx,
                health_check=elbv2.HealthCheck(
                    enabled=True,
                    path="/health",
                    healthy_http_codes="200-499",  # Accept any non-5xx response
                    interval=Duration.seconds(30),  # Normal interval (30 seconds)
                    timeout=Duration.seconds(5),  # Normal timeout
                    healthy_threshold_count=2,
                    unhealthy_threshold_count=3,  # Normal retry count
                ),
            )
