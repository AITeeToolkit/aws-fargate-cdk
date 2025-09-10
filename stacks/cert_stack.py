from aws_cdk import (
    Stack,
    aws_certificatemanager as acm,
    aws_route53 as route53,
)
from constructs import Construct

class CertStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domain_name: str,
        subdomain: str = "dev",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Dynamically look up the hosted zone by root domain
        zone = route53.HostedZone.from_lookup(
            self, "Zone",
            domain_name=domain_name
        )

        # Issue cert with domain and dev subdomain as SAN
        self.cert = acm.Certificate(
            self, "DomainCert",
            domain_name=domain_name,
            subject_alternative_names=[f"{subdomain}.{domain_name}"],
            validation=acm.CertificateValidation.from_dns(zone)
        )