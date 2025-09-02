#!/usr/bin/env python3
"""Test script to verify Nuclia API connection and explore response structure"""

import os
from dotenv import load_dotenv
from nuclia import sdk
import json

# Load environment variables
load_dotenv()

# Configuration
NUCLIA_API_KEY = os.environ.get('NUCLIA_API_KEY')
NUCLIA_ZONE = os.environ.get('NUCLIA_ZONE', 'aws-us-east-2-1')
KB_ID = os.environ.get('NUCLIA_KB_ID', '45bd361a-7e42-487a-9ff9-c003e7a93560')

print("Testing Nuclia API Connection")
print("=" * 50)
print(f"Zone: {NUCLIA_ZONE}")
print(f"KB ID: {KB_ID}")
print(f"API Key: {'Configured' if NUCLIA_API_KEY and NUCLIA_API_KEY != 'YOUR_API_KEY_HERE' else 'Not configured'}")
print()

# Initialize
kb_url = f"https://{NUCLIA_ZONE}.nuclia.cloud/api/v1/kb/{KB_ID}"
sdk.NucliaAuth().kb(url=kb_url, token=NUCLIA_API_KEY)
search_client = sdk.NucliaSearch()

# Simple search
query = "financial"
print(f"Searching for: '{query}'")
print("-" * 30)

try:
    response = search_client.find(
        query=query,
        filters=None
    )
    
    print(f"Response type: {type(response)}")
    
    # Explore response structure
    if response:
        # Check response attributes
        print(f"Response attributes: {[a for a in dir(response) if not a.startswith('_')][:15]}")
        
        if hasattr(response, 'resources'):
            print(f"Has resources: {response.resources is not None}")
            if response.resources:
                print(f"Resources type: {type(response.resources)}")
                print(f"Number of resources: {len(response.resources)}")
                
                # Show first few resources
                for idx, (rid, resource) in enumerate(response.resources.items()):
                    if idx >= 3:
                        break
                    print(f"\nResource {idx + 1} ID: {rid}")
                    print(f"  Resource type: {type(resource)}")
                    if hasattr(resource, 'title'):
                        print(f"  Title: {resource.title}")
                    if hasattr(resource, 'summary'):
                        print(f"  Summary: {resource.summary[:100]}...")
        
        if hasattr(response, 'paragraphs'):
            print(f"\nHas paragraphs: {response.paragraphs is not None}")
            if response.paragraphs:
                print(f"Number of paragraphs: {len(response.paragraphs)}")
                for idx, (pid, para) in enumerate(response.paragraphs.items()):
                    if idx >= 2:
                        break
                    print(f"  Paragraph {idx + 1}: {para.get('text', '')[:100]}...")
        
        print(f"\nTotal results found: {count}")
    else:
        print("No results found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()