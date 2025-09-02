#!/usr/bin/env python3
"""
Test the Ask API with proper authentication
DataVault Financial Services - Compliance Q&A System
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('code_samples/.env')

def ask_compliance_question(question):
    """
    Query DataVault's Nuclia knowledge box programmatically
    """
    # Get credentials from environment
    api_key = os.getenv('NUCLIA_API_KEY')
    kb_id = "xxx"  # InvestmentInsights KB UID
    zone = "aws-us-east-2-1"
    
    # Nuclia Ask API endpoint
    url = f"https://{zone}.nuclia.cloud/api/v1/kb/{kb_id}/ask"
    
    headers = {
        "X-NUCLIA-SERVICEACCOUNT": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": question,
        "features": ["semantic", "keyword"],
        "max_tokens": 1000
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Question: {question}")
        print("-" * 50)
        
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            return {
                "answer": result.get("text", ""),
                "sources": result.get("citations", []),
                "relations": result.get("relations", [])
            }
        else:
            print(f"Error response: {response.text}")
            return {"error": f"API returned {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Test the actual API call
if __name__ == "__main__":
    print("Testing Nuclia Ask API with real credentials...")
    print("=" * 60)
    
    # Sarah's urgent compliance question
    compliance_answer = ask_compliance_question(
        "What are the current economic conditions and market risks we should monitor?"
    )
    
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    
    if "error" not in compliance_answer:
        print("✅ SUCCESS!")
        print(f"\nAI Answer ({len(compliance_answer['answer'])} chars):")
        print("-" * 30)
        print(compliance_answer["answer"])
        print(f"\n📚 Sources found: {len(compliance_answer['sources'])}")
        
        if compliance_answer['sources']:
            print("\nSource citations:")
            for i, source in enumerate(compliance_answer['sources'][:3], 1):
                print(f"  {i}. {source.get('title', 'Unknown')} (page {source.get('page', 'N/A')})")
                
    else:
        print(f"❌ Error: {compliance_answer['error']}")