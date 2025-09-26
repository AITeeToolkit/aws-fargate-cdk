from aws_cdk import (
    Stack,
    aws_route53 as route53,
    aws_route53_targets as targets,
)
from aws_cdk.aws_elasticloadbalancingv2 import IApplicationLoadBalancer
from constructs import Construct

class DomainDnsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domain_name: str,
        alb: IApplicationLoadBalancer,
        mail_server: str,
        dkim_selector: str,
        dkim_public_key: str,
        spf_servers: list[str] = None,
        dmarc_rua: str = None,
        dmarc_ruf: str = None,
        dmarc_policy: str = "quarantine",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 🔎 Lookup the existing hosted zone
        zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=domain_name
        )

        # 🌐 Root domain ALIAS record to ALB
        route53.ARecord(
            self, "RootAliasRecord",
            zone=zone,
            record_name=domain_name,
            target=route53.RecordTarget.from_alias(
                targets.LoadBalancerTarget(alb)
            )
        )

        # 🌐 Dev subdomain ALIAS record to ALB
        route53.ARecord(
            self, "DevAliasRecord",
            zone=zone,
            record_name=f"dev.{domain_name}",
            target=route53.RecordTarget.from_alias(
                targets.LoadBalancerTarget(alb)
            )
        )

        # 📜 SPF record
        spf_value = " ".join(["v=spf1"] + (spf_servers or []) + ["~all"])
        route53.TxtRecord(self, "SPF",
            zone=zone,
            record_name=domain_name,
            values=[spf_value]
        )

        # 🔑 DKIM record
        route53.TxtRecord(self, "DKIM",
            zone=zone,
            record_name=f"{dkim_selector}._domainkey.{domain_name}",
            values=[f"v=DKIM1; k=rsa; p={dkim_public_key.strip()}"]
        )

        # 📬 DMARC record
        dmarc_value = f"v=DMARC1; p={dmarc_policy}"
        if dmarc_rua:
            dmarc_value += f"; rua=mailto:{dmarc_rua}"
        if dmarc_ruf:
            dmarc_value += f"; ruf=mailto:{dmarc_ruf}"

        route53.TxtRecord(self, "DMARC",
            zone=zone,
            record_name=f"_dmarc.{domain_name}",
            values=[dmarc_value]
        )

        # ✉️ MX record
        route53.MxRecord(self, "MX",
            zone=zone,
            record_name=domain_name,
            values=[
                route53.MxRecordValue(priority=10, host_name=mail_server)
            ]
        )

        # 👇 Expose zone if needed downstream
        self.hosted_zone = zone