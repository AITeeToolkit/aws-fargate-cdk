from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53
from constructs import Construct


class CertificateStack(Stack):
    """
    Per-domain certificate stack that creates a wildcard certificate for a single domain.
    This allows independent lifecycle management and avoids CloudFormation export dependency issues.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domain: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # Extract root zone from domain (e.g., "cidertees.com" from "dev.cidertees.com")
        root_zone_name = ".".join(domain.split(".")[-2:])

        # Look up existing hosted zone
        zone = route53.HostedZone.from_lookup(
            self,
            "Zone",
            domain_name=root_zone_name,
        )

        # Create wildcard certificate for this domain
        # Retain certificates on stack deletion to prevent accidental deletion
        cert = acm.Certificate(
            self,
            "WildcardCert",
            domain_name=f"*.{root_zone_name}",
            subject_alternative_names=[root_zone_name],  # Also cover root domain
            validation=acm.CertificateValidation.from_dns(zone),
        )
        cert.apply_removal_policy(RemovalPolicy.RETAIN)

        # Store certificate ARN for reference
        self.certificate_arn = cert.certificate_arn

        # Export certificate ARN for cross-stack reference
        # Export name is based on domain, allowing consumers to import it
        CfnOutput(
            self,
            "CertArn",
            value=cert.certificate_arn,
            export_name=f"CertArn-{domain.replace('.', '-')}",
            description=f"Wildcard certificate ARN for *.{root_zone_name}",
        )
