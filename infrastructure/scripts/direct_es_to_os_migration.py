#!/usr/bin/env python3

"""
Direct Elasticsearch to OpenSearch Migration Script
Uses bulk API to export from Elasticsearch snapshots and import to OpenSearch
"""

import boto3
import json
import requests
import os
import sys
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import tempfile
import gzip
from datetime import datetime
import urllib3

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_opensearch_endpoint():
    """Get OpenSearch endpoint from SSM"""
    try:
        ssm = boto3.client('ssm')
        response = ssm.get_parameter(Name='/storefront-dev/opensearch/endpoint')
        return response['Parameter']['Value'].replace('https://', '')
    except Exception as e:
        print(f"❌ Could not get OpenSearch endpoint: {e}")
        return None

def get_elasticsearch_data_from_k8s():
    """
    Get data directly from Kubernetes Elasticsearch cluster via port forwarding
    """
    print("🔍 Attempting to connect to port-forwarded Elasticsearch cluster...")
    
    # Use localhost with HTTPS since Elasticsearch requires SSL
    es_endpoint = "https://localhost:9200"
    
    # Test the connection (disable SSL verification for self-signed certs)
    # Use basic auth with Elasticsearch credentials
    auth = ('elastic', 'BODILY-total-spat')
    try:
        response = requests.get(f"{es_endpoint}/_cluster/health", timeout=5, verify=False, auth=auth)
        if response.status_code == 200:
            cluster_info = response.json()
            print(f"✅ Connected to Elasticsearch cluster: {cluster_info.get('cluster_name', 'unknown')}")
            print(f"📊 Cluster status: {cluster_info.get('status', 'unknown')}")
            return es_endpoint
        else:
            print(f"⚠️ Elasticsearch not responding: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Could not connect to localhost:9200: {e}")
        print("💡 Make sure port forwarding is active: kubectl port-forward -n elasticsearch svc/elasticsearch-master 9200:9200")
        return None

def export_elasticsearch_data(es_endpoint):
    """Export all data from Elasticsearch using bulk API"""
    print(f"📤 Exporting data from Elasticsearch: {es_endpoint}")
    
    # Use the same auth credentials
    auth = ('elastic', 'BODILY-total-spat')
    
    try:
        # Get all indices
        response = requests.get(f"{es_endpoint}/_cat/indices?format=json", verify=False, auth=auth)
        if response.status_code != 200:
            print(f"❌ Could not list indices: {response.text}")
            return None
            
        indices = response.json()
        print(f"📋 Found {len(indices)} indices")
        
        # Filter out system indices
        data_indices = [idx for idx in indices if not idx['index'].startswith('.')]
        print(f"📊 Data indices to migrate: {[idx['index'] for idx in data_indices]}")
        
        # Export each index
        exported_data = []
        for index_info in data_indices:
            index_name = index_info['index']
            print(f"📤 Exporting index: {index_name}")
            
            # Get index mapping
            mapping_response = requests.get(f"{es_endpoint}/{index_name}/_mapping", verify=False, auth=auth)
            if mapping_response.status_code == 200:
                mapping = mapping_response.json()
                exported_data.append({
                    'action': 'create_index',
                    'index': index_name,
                    'mapping': mapping
                })
            
            # Export documents using scroll API
            scroll_response = requests.post(f"{es_endpoint}/{index_name}/_search?scroll=5m", 
                                          json={"size": 1000, "query": {"match_all": {}}}, verify=False, auth=auth)
            
            if scroll_response.status_code != 200:
                print(f"⚠️ Could not start scroll for {index_name}: {scroll_response.text}")
                continue
                
            scroll_data = scroll_response.json()
            scroll_id = scroll_data.get('_scroll_id')
            hits = scroll_data.get('hits', {}).get('hits', [])
            
            doc_count = 0
            while hits:
                for hit in hits:
                    exported_data.append({
                        'action': 'index',
                        'index': hit['_index'],
                        'id': hit['_id'],
                        'source': hit['_source']
                    })
                    doc_count += 1
                
                # Get next batch
                scroll_response = requests.post(f"{es_endpoint}/_search/scroll",
                                              json={"scroll": "5m", "scroll_id": scroll_id}, verify=False, auth=auth)
                if scroll_response.status_code != 200:
                    break
                    
                scroll_data = scroll_response.json()
                hits = scroll_data.get('hits', {}).get('hits', [])
            
            print(f"✅ Exported {doc_count} documents from {index_name}")
        
        return exported_data
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return None

def import_to_opensearch(opensearch_endpoint, data):
    """Import data to OpenSearch using bulk API with SigV4 auth"""
    print(f"📥 Importing data to OpenSearch: {opensearch_endpoint}")
    
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        
        # Create indices first
        indices_created = set()
        for item in data:
            if item['action'] == 'create_index' and item['index'] not in indices_created:
                index_name = item['index']
                
                # Create index with mapping
                create_url = f"https://{opensearch_endpoint}/{index_name}"
                create_request = AWSRequest(method='PUT', url=create_url, 
                                          data=json.dumps(item['mapping']))
                create_request.headers['Content-Type'] = 'application/json'
                SigV4Auth(credentials, 'es', 'us-east-1').add_auth(create_request)
                
                response = requests.put(create_url, 
                                      data=create_request.body,
                                      headers=dict(create_request.headers))
                
                if response.status_code in [200, 201]:
                    print(f"✅ Created index: {index_name}")
                    indices_created.add(item['index'])
                else:
                    print(f"⚠️ Could not create index {index_name}: {response.text}")
        
        # Bulk import documents
        bulk_data = []
        doc_count = 0
        
        for item in data:
            if item['action'] == 'index':
                # Add to bulk request
                bulk_data.append(json.dumps({
                    "index": {
                        "_index": item['index'],
                        "_id": item['id']
                    }
                }))
                bulk_data.append(json.dumps(item['source']))
                doc_count += 1
                
                # Send bulk request every 100 documents
                if len(bulk_data) >= 200:  # 100 docs * 2 lines each
                    send_bulk_request(opensearch_endpoint, bulk_data, credentials)
                    bulk_data = []
        
        # Send remaining documents
        if bulk_data:
            send_bulk_request(opensearch_endpoint, bulk_data, credentials)
        
        print(f"✅ Imported {doc_count} documents to OpenSearch")
        return True
        
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        return False

def send_bulk_request(opensearch_endpoint, bulk_data, credentials):
    """Send a bulk request to OpenSearch"""
    bulk_body = '\n'.join(bulk_data) + '\n'
    
    bulk_url = f"https://{opensearch_endpoint}/_bulk"
    bulk_request = AWSRequest(method='POST', url=bulk_url, data=bulk_body)
    bulk_request.headers['Content-Type'] = 'application/x-ndjson'
    SigV4Auth(credentials, 'es', 'us-east-1').add_auth(bulk_request)
    
    response = requests.post(bulk_url,
                           data=bulk_request.body,
                           headers=dict(bulk_request.headers))
    
    if response.status_code != 200:
        print(f"⚠️ Bulk request failed: {response.text}")
    else:
        result = response.json()
        if result.get('errors'):
            print(f"⚠️ Some bulk operations failed: {result}")
        else:
            print(f"✅ Bulk request successful ({len(bulk_data)//2} documents)")

def main():
    print("🚀 Direct Elasticsearch to OpenSearch Migration")
    print("=" * 50)
    
    # Get OpenSearch endpoint
    opensearch_endpoint = get_opensearch_endpoint()
    if not opensearch_endpoint:
        sys.exit(1)
    
    print(f"📡 OpenSearch endpoint: {opensearch_endpoint}")
    
    # Try to get data from Kubernetes Elasticsearch
    es_endpoint = get_elasticsearch_data_from_k8s()
    if not es_endpoint:
        print("❌ Could not connect to Elasticsearch cluster")
        print("💡 Make sure kubectl is configured and Elasticsearch is running")
        sys.exit(1)
    
    # Export data from Elasticsearch
    print("\n📤 Step 1: Export data from Elasticsearch")
    exported_data = export_elasticsearch_data(es_endpoint)
    if not exported_data:
        print("❌ Failed to export data from Elasticsearch")
        sys.exit(1)
    
    print(f"✅ Exported {len(exported_data)} items")
    
    # Import data to OpenSearch
    print("\n📥 Step 2: Import data to OpenSearch")
    success = import_to_opensearch(opensearch_endpoint, exported_data)
    if not success:
        print("❌ Failed to import data to OpenSearch")
        sys.exit(1)
    
    print("\n🎉 Migration completed successfully!")
    print(f"🌐 OpenSearch Dashboards: https://{opensearch_endpoint}/_dashboards/")
    print("💡 Check the original index names for your data")

if __name__ == "__main__":
    main()
