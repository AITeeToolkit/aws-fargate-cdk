#!/usr/bin/env python3
"""
OpenSearch to OpenSearch Backup Script
Copies indices from one OpenSearch domain to another using scroll and bulk APIs
"""

import argparse
import json
import sys
from typing import List, Dict, Any
import boto3
from requests_aws4auth import AWS4Auth
import requests
from urllib.parse import urlparse

# Colors for output
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_status(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def print_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")

def print_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")

def get_aws_auth(region: str = 'us-east-1'):
    """Get AWS authentication for OpenSearch requests"""
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'es',
        session_token=credentials.token
    )

def clean_endpoint(endpoint: str) -> str:
    """Remove https:// prefix if present"""
    if endpoint.startswith('https://'):
        return endpoint.replace('https://', '')
    elif endpoint.startswith('http://'):
        return endpoint.replace('http://', '')
    return endpoint

def list_indices(endpoint: str, auth: AWS4Auth, exclude_system: bool = True) -> List[str]:
    """List all indices from OpenSearch domain"""
    endpoint = clean_endpoint(endpoint)
    url = f"https://{endpoint}/_cat/indices?format=json"
    
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    
    indices = response.json()
    
    if exclude_system:
        # Exclude system indices (starting with .)
        return [idx['index'] for idx in indices if not idx['index'].startswith('.')]
    
    return [idx['index'] for idx in indices]

def get_index_mapping(endpoint: str, index: str, auth: AWS4Auth) -> Dict[str, Any]:
    """Get mapping for an index"""
    endpoint = clean_endpoint(endpoint)
    url = f"https://{endpoint}/{index}/_mapping"
    
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    
    return response.json()

def create_index_with_mapping(endpoint: str, index: str, mapping: Dict[str, Any], auth: AWS4Auth):
    """Create index with mapping on target"""
    endpoint = clean_endpoint(endpoint)
    url = f"https://{endpoint}/{index}"
    
    # Check if index already exists
    response = requests.head(url, auth=auth)
    if response.status_code == 200:
        print_warning(f"Index {index} already exists on target, skipping creation")
        return
    
    # Extract mapping from source response
    if index in mapping:
        index_config = {
            "mappings": mapping[index].get("mappings", {}),
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }
        }
    else:
        index_config = {}
    
    response = requests.put(url, auth=auth, json=index_config)
    response.raise_for_status()
    print_success(f"Created index: {index}")

def backup_index(source_endpoint: str, target_endpoint: str, index: str, 
                 source_auth: AWS4Auth, target_auth: AWS4Auth, batch_size: int = 1000):
    """Backup a single index using scroll and bulk APIs"""
    source_endpoint = clean_endpoint(source_endpoint)
    target_endpoint = clean_endpoint(target_endpoint)
    
    print_status(f"Backing up index: {index}")
    
    # Get mapping from source
    mapping = get_index_mapping(source_endpoint, index, source_auth)
    
    # Create index on target with same mapping
    create_index_with_mapping(target_endpoint, index, mapping, target_auth)
    
    # Initialize scroll
    scroll_url = f"https://{source_endpoint}/{index}/_search?scroll=5m"
    scroll_body = {
        "size": batch_size,
        "query": {"match_all": {}}
    }
    
    response = requests.post(scroll_url, auth=source_auth, json=scroll_body)
    response.raise_for_status()
    scroll_data = response.json()
    
    scroll_id = scroll_data.get('_scroll_id')
    total_hits = scroll_data.get('hits', {}).get('total', {}).get('value', 0)
    
    print_status(f"Total documents to backup: {total_hits}")
    
    processed = 0
    
    while True:
        hits = scroll_data.get('hits', {}).get('hits', [])
        
        if not hits:
            break
        
        # Prepare bulk insert
        bulk_data = []
        for hit in hits:
            # Index action
            bulk_data.append(json.dumps({
                "index": {
                    "_index": index,
                    "_id": hit['_id']
                }
            }))
            # Document source
            bulk_data.append(json.dumps(hit['_source']))
        
        # Insert into target
        bulk_url = f"https://{target_endpoint}/_bulk"
        bulk_body = '\n'.join(bulk_data) + '\n'
        
        headers = {'Content-Type': 'application/x-ndjson'}
        response = requests.post(bulk_url, auth=target_auth, data=bulk_body, headers=headers)
        response.raise_for_status()
        
        bulk_response = response.json()
        if bulk_response.get('errors'):
            print_warning(f"Some documents failed to index")
            for item in bulk_response.get('items', []):
                if 'error' in item.get('index', {}):
                    print_error(f"Error: {item['index']['error']}")
        
        processed += len(hits)
        print_status(f"Processed: {processed}/{total_hits} documents")
        
        # Get next batch
        scroll_continue_url = f"https://{source_endpoint}/_search/scroll"
        scroll_continue_body = {
            "scroll": "5m",
            "scroll_id": scroll_id
        }
        
        response = requests.post(scroll_continue_url, auth=source_auth, json=scroll_continue_body)
        response.raise_for_status()
        scroll_data = response.json()
        scroll_id = scroll_data.get('_scroll_id')
    
    # Clear scroll
    clear_scroll_url = f"https://{source_endpoint}/_search/scroll"
    clear_scroll_body = {"scroll_id": scroll_id}
    requests.delete(clear_scroll_url, auth=source_auth, json=clear_scroll_body)
    
    print_success(f"Completed backup of index: {index} ({processed} documents)")

def main():
    parser = argparse.ArgumentParser(description='Backup OpenSearch indices from one domain to another')
    parser.add_argument('--source', required=True, help='Source OpenSearch endpoint')
    parser.add_argument('--target', required=True, help='Target OpenSearch endpoint')
    parser.add_argument('--indices', default='*', help='Comma-separated list of indices or * for all')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for scroll')
    
    args = parser.parse_args()
    
    print_status("=== OpenSearch to OpenSearch Backup Script ===")
    print_status(f"Source: {args.source}")
    print_status(f"Target: {args.target}")
    print_status(f"Region: {args.region}")
    
    try:
        # Get AWS authentication
        source_auth = get_aws_auth(args.region)
        target_auth = get_aws_auth(args.region)
        
        # Get list of indices
        if args.indices == '*':
            print_status("Getting list of all indices from source...")
            indices = list_indices(args.source, source_auth)
            print_status(f"Found {len(indices)} indices: {', '.join(indices)}")
        else:
            indices = [idx.strip() for idx in args.indices.split(',')]
            print_status(f"Backing up specified indices: {', '.join(indices)}")
        
        # Backup each index
        for index in indices:
            try:
                backup_index(args.source, args.target, index, source_auth, target_auth, args.batch_size)
            except Exception as e:
                print_error(f"Failed to backup index {index}: {str(e)}")
                continue
        
        print_success("=== Backup completed successfully ===")
        
    except Exception as e:
        print_error(f"Backup failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
