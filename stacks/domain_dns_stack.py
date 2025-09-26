from aws_cdk import (
    Stack,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_lambda as _lambda,
    aws_iam as iam,
    custom_resources as cr,
    aws_elasticloadbalancingv2 as elb,
    Duration
)
from constructs import Construct
import json

class DomainDnsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domain_name: str,
        alb: elb.IApplicationLoadBalancer,
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

        # 🔎 Lookup the existing hosted zone (using CDK equivalent of ensure_hosted_zone_and_store)
        zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=domain_name
        )

        # 🛠️ Lambda function for idempotent Route53 record creation
        route53_record_lambda = _lambda.Function(
            self, "Route53RecordLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_inline(
                """
import json
import boto3
import cfnresponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def handler(event, context):
    try:
        route53 = boto3.client('route53')
        request_type = event['RequestType']
        props = event['ResourceProperties']
        hosted_zone_id = props['HostedZoneId']
        record_name = props['RecordName']
        record_type = props['RecordType']
        record_values = props['RecordValues']
        ttl = int(props.get('TTL', 300))

        # Normalize record name to end with a dot
        if not record_name.endswith('.'):
            record_name = record_name + '.'

        # Check if record exists
        response = route53.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=record_name,
            StartRecordType=record_type,
            MaxItems='1'
        )
        existing_records = response['ResourceRecordSets']
        record_exists = any(
            record['Name'] == record_name and record['Type'] == record_type
            for record in existing_records
        )

        # Prepare change batch
        change_batch = {'Changes': []}

        if request_type in ['Create', 'Update']:
            if not record_exists:
                # Create new record
                change = {
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': record_name,
                        'Type': record_type,
                        'TTL': ttl,
                        'ResourceRecords': [
                            {'Value': value} for value in record_values
                        ]
                    }
                }
                if record_type == 'A' and 'AliasTarget' in props:
                    change['ResourceRecordSet']['AliasTarget'] = props['AliasTarget']
                    del change['ResourceRecordSet']['TTL']
                    del change['ResourceRecordSet']['ResourceRecords']
                change_batch['Changes'].append(change)
                logger.info(f"Creating {record_type} record for {record_name}")
            else:
                logger.info(f"Record {record_type} {record_name} already exists, skipping creation")

        elif request_type == 'Delete':
            if record_exists:
                change = {
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': record_name,
                        'Type': record_type,
                        'TTL': ttl,
                        'ResourceRecords': [
                            {'Value': value} for value in record_values
                        ]
                    }
                }
                if record_type == 'A' and 'AliasTarget' in props:
                    change['ResourceRecordSet']['AliasTarget'] = props['AliasTarget']
                    del change['ResourceRecordSet']['TTL']
                    del change['ResourceRecordSet']['ResourceRecords']
                change_batch['Changes'].append(change)
                logger.info(f"Deleting {record_type} record for {record_name}")

        # Apply changes if any
        if change_batch['Changes']:
            route53.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch=change_batch
            )

        # Send success response
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {
            'HostedZoneId': hosted_zone_id,
            'RecordName': record_name,
            'RecordType': record_type
        })

    except Exception as e:
        logger.error(f"Error processing {record_name} {record_type}: {str(e)}")
        cfnresponse.send(event, context, cfnresponse.FAILED, {'Error': str(e)})
"""
            ),
            timeout=Duration.seconds(30),
        )

        # Grant Lambda permission to modify Route53 records
        route53_record_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "route53:ListResourceRecordSets",
                    "route53:ChangeResourceRecordSets"
                ],
                resources=[f"arn:aws:route53:::hostedzone/{zone.hosted_zone_id}"]
            )
        )

        # Helper function to create custom resource for Route53 records
        def create_route53_record(id: str, record_name: str, record_type: str, record_values: list[str], alias_target=None, ttl: int = 300):
            props = {
                "HostedZoneId": zone.hosted_zone_id,
                "RecordName": record_name,
                "RecordType": record_type,
                "RecordValues": record_values,
                "TTL": str(ttl),
            }
            if alias_target:
                props["AliasTarget"] = alias_target
            cr.AwsCustomResource(
                self, id,
                on_create=cr.AwsSdkCall(
                    service="Lambda",
                    action="invoke",
                    parameters={
                        "FunctionName": route53_record_lambda.function_name,
                        "Payload": json.dumps({
                            "RequestType": "Create",
                            "ResourceProperties": props
                        })
                    },
                    physical_resource_id=cr.PhysicalResourceId.of(f"{record_name}-{record_type}")
                ),
                on_update=cr.AwsSdkCall(
                    service="Lambda",
                    action="invoke",
                    parameters={
                        "FunctionName": route53_record_lambda.function_name,
                        "Payload": json.dumps({
                            "RequestType": "Update",
                            "ResourceProperties": props
                        })
                    },
                    physical_resource_id=cr.PhysicalResourceId.of(f"{record_name}-{record_type}")
                ),
                on_delete=cr.AwsSdkCall(
                    service="Lambda",
                    action="invoke",
                    parameters={
                        "FunctionName": route53_record_lambda.function_name,
                        "Payload": json.dumps({
                            "RequestType": "Delete",
                            "ResourceProperties": props
                        })
                    },
                    physical_resource_id=cr.PhysicalResourceId.of(f"{record_name}-{record_type}")
                ),
                policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                    resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
                )
            )

        # 🌐 Root domain ALIAS record to ALB
        alias_target = {
            "HostedZoneId": alb.load_balancer_canonical_hosted_zone_id,
            "DNSName": alb.load_balancer_dns_name,
            "EvaluateTargetHealth": False
        }
        create_route53_record(
            "RootAliasRecord",
            domain_name,
            "A",
            [],
            alias_target=alias_target
        )

        # 🌐 Dev subdomain ALIAS record to ALB
        create_route53_record(
            "DevAliasRecord",
            f"dev.{domain_name}",
            "A",
            [],
            alias_target=alias_target
        )

        # 📜 SPF record
        spf_value = " ".join(["v=spf1"] + (spf_servers or []) + ["~all"])
        create_route53_record(
            "SPF",
            domain_name,
            "TXT",
            [spf_value]
        )

        # 🔑 DKIM record
        create_route53_record(
            "DKIM",
            f"{dkim_selector}._domainkey.{domain_name}",
            "TXT",
            [f"v=DKIM1; k=rsa; p={dkim_public_key.strip()}"]
        )

        # 📬 DMARC record
        dmarc_value = f"v=DMARC1; p={dmarc_policy}"
        if dmarc_rua:
            dmarc_value += f"; rua=mailto:{dmarc_rua}"
        if dmarc_ruf:
            dmarc_value += f"; ruf=mailto:{dmarc_ruf}"
        create_route53_record(
            "DMARC",
            f"_dmarc.{domain_name}",
            "TXT",
            [dmarc_value]
        )

        # ✉️ MX record
        create_route53_record(
            "MX",
            domain_name,
            "MX",
            [f"10 {mail_server}"]
        )

        # 👇 Expose zone if needed downstream
        self.hosted_zone = zone
