from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53
from constructs import Construct


class CertificateStack(Stack):
    """
    Per-domain certificate stack that creates an exact domain certificate.
    This allows independent lifecycle management per environment and avoids CloudFormation export dependency issues.
    No wildcards - each environment gets its own certificate for its specific domain.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domain: str,
        environment: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # Look up existing hosted zone for the full domain
        # DNS worker creates these zones before CDK deployment
        zone = route53.HostedZone.from_lookup(
            self,
            "Zone",
            domain_name=domain,
        )

        # Create exact domain certificate (no wildcard)
        # Each environment gets its own certificate for its specific domain
        # Retain certificates on stack deletion to prevent accidental deletion
        cert = acm.Certificate(
            self,
            "DomainCert",
            domain_name=domain,  # Exact domain, no wildcard
            validation=acm.CertificateValidation.from_dns(zone),
        )
        cert.apply_removal_policy(RemovalPolicy.RETAIN)

        # Store certificate ARN for reference
        self.certificate_arn = cert.certificate_arn

        # Export certificate ARN for cross-stack reference
        # Export name includes environment to distinguish between dev/staging/prod
        CfnOutput(
            self,
            "CertArn",
            value=cert.certificate_arn,
            export_name=f"CertArn-{environment}-{domain.replace('.', '-')}",
            description=f"Certificate ARN for {domain} in {environment}",
        )
