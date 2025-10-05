import json
import time

from aws_cdk import Duration, Stack
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_route53 as route53
from aws_cdk import custom_resources as cr
from constructs import Construct


class DomainDnsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domain_name: str,
        alb: elbv2.IApplicationLoadBalancer,
        mail_server: str,
        dkim_selector: str,
        dkim_public_key: str,
        spf_servers: list[str] = None,
        dmarc_rua: str = None,
        dmarc_ruf: str = None,
        dmarc_policy: str = "quarantine",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Look up existing hosted zone for the full domain
        # DNS worker creates these zones before CDK deployment
        zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=domain_name)

        # Lambda function for idempotent Route53 record creation
        route53_record_lambda = _lambda.Function(
            self,
            "Route53RecordLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_inline(
                """
import json
import boto3
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
            # Always check and create missing records (idempotent)
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
                logger.info(f"Creating missing {record_type} record for {record_name}")
            else:
                # Verify existing record has correct values
                existing_record = next(
                    (record for record in existing_records
                     if record['Name'] == record_name and record['Type'] == record_type),
                    None
                )

                # Check if values match what we expect
                needs_update = False
                if record_type == 'A' and 'AliasTarget' in props:
                    # For alias records, check alias target
                    expected_dns = props['AliasTarget']['DNSName']
                    if existing_record.get('AliasTarget', {}).get('DNSName') != expected_dns:
                        needs_update = True
                        logger.info(f"Alias target mismatch for {record_name}: expected {expected_dns}")
                else:
                    # For regular records, check resource records
                    existing_values = [rr['Value'] for rr in existing_record.get('ResourceRecords', [])]
                    if set(existing_values) != set(record_values):
                        needs_update = True
                        logger.info(f"Record values mismatch for {record_name}: expected {record_values}, got {existing_values}")

                if needs_update:
                    # Update the record by replacing it
                    change = {
                        'Action': 'UPSERT',
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
                    logger.info(f"Updating {record_type} record for {record_name}")
                else:
                    logger.info(f"Record {record_type} {record_name} exists with correct values, no action needed")

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
        return {
            'statusCode': 200,
            'body': json.dumps({
                'HostedZoneId': hosted_zone_id,
                'RecordName': record_name,
                'RecordType': record_type
            })
        }

    except Exception as e:
        logger.error(f"Error processing {record_name} {record_type}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'Error': str(e)})
        }
"""
            ),
            timeout=Duration.seconds(30),
        )

        # Grant Lambda permission to modify Route53 records
        route53_record_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "route53:ListResourceRecordSets",
                    "route53:ChangeResourceRecordSets",
                ],
                resources=[f"arn:aws:route53:::hostedzone/{zone.hosted_zone_id}"],
            )
        )

        # Helper function to create custom resource for Route53 records
        def create_route53_record(
            id: str,
            record_name: str,
            record_type: str,
            record_values: list[str],
            alias_target=None,
            ttl: int = 300,
        ):
            props = {
                "HostedZoneId": zone.hosted_zone_id,
                "RecordName": record_name,
                "RecordType": record_type,
                "RecordValues": record_values,
                "TTL": str(ttl),
                "ForceUpdate": str(int(time.time())),  # Force update on every deployment
            }
            if alias_target:
                props["AliasTarget"] = alias_target

            # Create custom resource policy that includes Lambda invoke permission
            custom_resource_policy = cr.AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        actions=["lambda:InvokeFunction"],
                        resources=[route53_record_lambda.function_arn],
                    ),
                    iam.PolicyStatement(
                        actions=[
                            "route53:ListResourceRecordSets",
                            "route53:ChangeResourceRecordSets",
                        ],
                        resources=[f"arn:aws:route53:::hostedzone/{zone.hosted_zone_id}"],
                    ),
                ]
            )

            cr.AwsCustomResource(
                self,
                id,
                on_create=cr.AwsSdkCall(
                    service="Lambda",
                    action="invoke",
                    parameters={
                        "FunctionName": route53_record_lambda.function_name,
                        "Payload": json.dumps(
                            {"RequestType": "Create", "ResourceProperties": props}
                        ),
                    },
                    physical_resource_id=cr.PhysicalResourceId.of(f"{record_name}-{record_type}"),
                ),
                on_update=cr.AwsSdkCall(
                    service="Lambda",
                    action="invoke",
                    parameters={
                        "FunctionName": route53_record_lambda.function_name,
                        "Payload": json.dumps(
                            {"RequestType": "Update", "ResourceProperties": props}
                        ),
                    },
                    physical_resource_id=cr.PhysicalResourceId.of(f"{record_name}-{record_type}"),
                ),
                on_delete=cr.AwsSdkCall(
                    service="Lambda",
                    action="invoke",
                    parameters={
                        "FunctionName": route53_record_lambda.function_name,
                        "Payload": json.dumps(
                            {"RequestType": "Delete", "ResourceProperties": props}
                        ),
                    },
                    physical_resource_id=cr.PhysicalResourceId.of(f"{record_name}-{record_type}"),
                ),
                policy=custom_resource_policy,
                install_latest_aws_sdk=False,  # Use Lambda runtime's built-in SDK
            )

        # Domain ALIAS record to ALB (works for both root and subdomains)
        alias_target = {
            "HostedZoneId": alb.load_balancer_canonical_hosted_zone_id,
            "DNSName": alb.load_balancer_dns_name,
            "EvaluateTargetHealth": False,
        }
        create_route53_record("DomainAliasRecord", domain_name, "A", [], alias_target=alias_target)

        # SPF record
        spf_value = " ".join(["v=spf1"] + (spf_servers or []) + ["~all"])
        create_route53_record("SPF", domain_name, "TXT", [spf_value])

        # DKIM record
        create_route53_record(
            "DKIM",
            f"{dkim_selector}._domainkey.{domain_name}",
            "TXT",
            [f"v=DKIM1; k=rsa; p={dkim_public_key.strip()}"],
        )

        # DMARC record
        dmarc_value = f"v=DMARC1; p={dmarc_policy}"
        if dmarc_rua:
            dmarc_value += f"; rua=mailto:{dmarc_rua}"
        if dmarc_ruf:
            dmarc_value += f"; ruf=mailto:{dmarc_ruf}"
        create_route53_record("DMARC", f"_dmarc.{domain_name}", "TXT", [dmarc_value])

        # MX record - create for the domain
        create_route53_record("MX", domain_name, "MX", [f"10 {mail_server}"])

        # Expose zone if needed downstream
        self.hosted_zone = zone
