#!/usr/bin/env python3
"""
Domain management helper functions for the listener service
"""
import logging
import boto3
import time
import psycopg2


def ensure_hosted_zone_and_store(conn, domain_name, region_name="us-east-1"):
    """
    Ensures hosted zone exists for domain and stores info in database.
    Returns hosted_zone_id (int PK) and aws_hosted_zone_id (string).
    
    Args:
        conn: Database connection object
        domain_name (str): Domain name to ensure hosted zone for
        region_name (str): AWS region
        
    Returns:
        tuple: (hosted_zone_id, aws_hosted_zone_id) or (None, None) if failed
    """
    route53_client = boto3.client("route53", region_name=region_name)
    
    try:
        # Check if hosted zone already exists in AWS
        response = route53_client.list_hosted_zones_by_name(DNSName=domain_name)
        hosted_zones = response.get("HostedZones", [])
        
        # Check if zone exists for this exact domain
        existing_zone = next((zone for zone in hosted_zones if zone["Name"] == f"{domain_name}."), None)
        
        if existing_zone:
            aws_zone_id = existing_zone['Id']
            logging.info(f"🔍 Hosted zone already exists for {domain_name}: {aws_zone_id}")
        else:
            # Create hosted zone if it doesn't exist
            caller_reference = f"{domain_name}-{int(time.time())}"
            response = route53_client.create_hosted_zone(
                Name=domain_name,
                CallerReference=caller_reference,
                HostedZoneConfig={
                    "Comment": f"Auto-created by listener for {domain_name}",
                    "PrivateZone": False
                }
            )
            
            aws_zone_id = response["HostedZone"]["Id"]
            logging.info(f"✅ Created hosted zone for {domain_name}: {aws_zone_id}")
        
        # Store/update hosted zone info in database
        hosted_zone_id = store_hosted_zone_info(conn, domain_name, aws_zone_id)
        
        if hosted_zone_id:
            return hosted_zone_id, aws_zone_id
        else:
            return None, None
            
    except Exception as e:
        logging.error(f"❌ Failed to ensure hosted zone for {domain_name}: {e}")
        return None, None


def store_hosted_zone_info(conn, domain_name, aws_zone_id):
    """
    Store hosted zone information in database and return the integer PK.
    
    Args:
        conn: Database connection object
        domain_name (str): Domain name
        aws_zone_id (str): AWS hosted zone ID
        
    Returns:
        int: hosted_zone_id (integer PK) or None if failed
    """
    try:
        cur = conn.cursor()
        
        # Insert or update hosted zone info
        cur.execute(
            """
            INSERT INTO hosted_zone_ids (domain_name, aws_hosted_zone_id, description)
            VALUES (%s, %s, %s)
            ON CONFLICT (domain_name) DO UPDATE
            SET aws_hosted_zone_id = EXCLUDED.aws_hosted_zone_id,
                description = EXCLUDED.description
            RETURNING hosted_zone_id;
            """,
            (domain_name, aws_zone_id, "Created by listener automation")
        )
        
        hosted_zone_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        
        logging.info(f"✅ Stored hosted zone info for {domain_name}: {aws_zone_id} (ID: {hosted_zone_id})")
        return hosted_zone_id
        
    except Exception as e:
        logging.error(f"❌ Error storing hosted zone info for {domain_name}: {e}")
        conn.rollback()
        return None



def update_domain_with_tenant(conn, domain_name, hosted_zone_id, zone_id):
    """
    Updates the domains table with tenant information from purchased_domains.
    
    Args:
        conn: Database connection object
        domain_name (str): The domain name to update
        hosted_zone_id (int): The hosted zone ID (integer PK)
        zone_id (str): The AWS hosted zone ID (for logging)
        
    Returns:
        int or None: tenant_id if found, None otherwise
    """
    try:
        with conn.cursor() as cursor:
            # Get tenant_id from purchased_domains table
            cursor.execute(
                "SELECT tenant_id FROM purchased_domains WHERE full_url = %s",
                (domain_name,)
            )
            tenant_result = cursor.fetchone()
            
            if tenant_result:
                tenant_id = tenant_result[0]
                logging.info(f"POSTGRES: Found tenant_id {tenant_id} for domain {domain_name} in purchased_domains table.")
            else:
                tenant_id = None
                logging.warning(f"POSTGRES: No tenant_id found for domain {domain_name} in purchased_domains table.")
            
            # Update or insert into domains table
            cursor.execute(
                """
                INSERT INTO domains (full_url, hosted_zone_id, tenant_id, active_status, activation_date)
                VALUES (%s, %s, %s, 'Y', CURRENT_DATE)
                ON CONFLICT (full_url) DO UPDATE
                SET hosted_zone_id = EXCLUDED.hosted_zone_id, 
                    tenant_id = EXCLUDED.tenant_id, 
                    active_status = 'Y', 
                    activation_date = CURRENT_DATE;
                """,
                (domain_name, hosted_zone_id, tenant_id),
            )
            logging.info(f"POSTGRES: Updated domains table for domain {domain_name} with hosted zone ID {zone_id} and tenant_id {tenant_id}.")
            
        conn.commit()
        return tenant_id
        
    except Exception as e:
        logging.error(f"POSTGRES: Error updating domain {domain_name} with tenant info: {e}")
        conn.rollback()
        raise


def get_tenant_for_domain(conn, domain_name):
    """
    Retrieves the tenant_id for a given domain from purchased_domains table.
    
    Args:
        conn: Database connection object
        domain_name (str): The domain name to lookup
        
    Returns:
        int or None: The tenant_id if found, None otherwise
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT tenant_id FROM purchased_domains WHERE full_url = %s",
                (domain_name,)
            )
            result = cursor.fetchone()
            
            if result:
                tenant_id = result[0]
                logging.info(f"POSTGRES: Found tenant_id {tenant_id} for domain {domain_name}.")
                return tenant_id
            else:
                logging.warning(f"POSTGRES: No tenant_id found for domain {domain_name}.")
                return None
                
    except Exception as e:
        logging.error(f"POSTGRES: Error retrieving tenant for domain {domain_name}: {e}")
        return None


def delete_hosted_zone_and_records(conn, domain_name, region_name="us-east-1"):
    """
    Deletes all DNS records (A, MX, TXT, CNAME) for the domain and then deletes the hosted zone.
    Also updates the database to mark domain inactive.
    """
    import boto3
    route53_client = boto3.client("route53", region_name=region_name)

    try:
        # Find the hosted zone
        response = route53_client.list_hosted_zones_by_name(DNSName=domain_name)
        hosted_zones = response.get("HostedZones", [])
        zone = next((z for z in hosted_zones if z["Name"] == f"{domain_name}."), None)

        if not zone:
            logging.warning(f"⚠️ No hosted zone found for {domain_name}, nothing to delete.")
            return False

        zone_id = zone["Id"].split("/")[-1]  # Clean zone ID

        # Get all record sets
        record_sets = route53_client.list_resource_record_sets(HostedZoneId=zone_id)

        changes = []
        for record in record_sets["ResourceRecordSets"]:
            record_type = record["Type"]
            record_name = record["Name"]

            if record_type in ["A", "MX", "TXT", "CNAME"]:
                logging.info(f"🗑️ Scheduling deletion for {record_type} record {record_name}")
                changes.append({
                    "Action": "DELETE",
                    "ResourceRecordSet": record
                })

        # Batch delete records (skip SOA/NS, they are required for the zone)
        if changes:
            route53_client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch={"Changes": changes}
            )
            logging.info(f"✅ Deleted {len(changes)} records from zone {zone_id} ({domain_name})")

        # Delete the hosted zone itself
        route53_client.delete_hosted_zone(Id=zone_id)
        logging.info(f"✅ Deleted hosted zone {zone_id} for {domain_name}")

        # Update DB to set inactive
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE domains SET active_status = 'N', deactivation_date = CURRENT_DATE WHERE full_url = %s",
                (domain_name,)
            )
            conn.commit()

        return True

    except Exception as e:
        logging.error(f"❌ Error deleting hosted zone for {domain_name}: {e}")
        conn.rollback()
        return False