from aws_cdk import Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53
from constructs import Construct


class CertificateStack(Stack):
    """
    Shared certificate stack that creates wildcard certificates for all domains.
    These certificates are shared across all environments (dev, staging, prod).
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domains: list[str],
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.certificates = {}  # domain -> certificate ARN

        # Group domains by root zone
        zones_map = {}  # root_zone -> [domains]
        for domain in domains:
            root_zone_name = ".".join(domain.split(".")[-2:])
            if root_zone_name not in zones_map:
                zones_map[root_zone_name] = []
            zones_map[root_zone_name].append(domain)

        # Create one wildcard certificate per root zone
        for root_zone_name in zones_map.keys():
            # Look up existing hosted zone
            zone = route53.HostedZone.from_lookup(
                self,
                f"Zone-{root_zone_name.replace('.', '-')}",
                domain_name=root_zone_name,
            )

            # Create wildcard certificate for this zone
            cert = acm.Certificate(
                self,
                f"WildcardCert-{root_zone_name.replace('.', '-')}",
                domain_name=f"*.{root_zone_name}",
                subject_alternative_names=[
                    root_zone_name
                ],  # Also cover root domain
                validation=acm.CertificateValidation.from_dns(zone),
            )

            # Store certificate ARN for all domains under this zone
            for domain in zones_map[root_zone_name]:
                self.certificates[domain] = cert.certificate_arn

            # Export certificate ARN for cross-stack reference
            self.export_value(
                cert.certificate_arn,
                name=f"WildcardCert-{root_zone_name.replace('.', '-')}-Arn",
            )
