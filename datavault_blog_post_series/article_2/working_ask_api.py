#!/usr/bin/env python3
"""
Working Nuclia Ask API Implementation
DataVault Financial Services - Compliance Q&A System
Author: David Kim
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
    Returns comprehensive answers with source citations
    """
    # Get credentials from environment
    api_key = os.getenv('NUCLIA_API_KEY')
    kb_id = "45bd361a-7e42-487a-9ff9-c003e7a93560"  # InvestmentInsights KB UID
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
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            # Parse NDJSON streaming response
            answer_text = ""
            sources = []
            
            for line in response.text.strip().split('\n'):
                if line:
                    data = json.loads(line)
                    
                    # Collect answer text
                    if data.get("item", {}).get("type") == "answer":
                        answer_text += data["item"]["text"]
                    
                    # Collect sources when available
                    elif data.get("item", {}).get("type") == "retrieval":
                        resources = data["item"]["results"]["resources"]
                        for resource_id, resource in resources.items():
                            sources.append({
                                "title": resource["title"],
                                "id": resource_id,
                                "paragraphs": len(resource.get("fields", {}).get("/f/file", {}).get("paragraphs", {}))
                            })
            
            return {
                "answer": answer_text.strip(),
                "sources": sources,
                "success": True
            }
        else:
            return {"error": f"API returned {response.status_code}", "success": False}
            
    except Exception as e:
        return {"error": str(e), "success": False}

# Example usage for DataVault compliance team
if __name__ == "__main__":
    print("DataVault Compliance Q&A System")
    print("=" * 50)
    
    # Sarah's urgent compliance question
    result = ask_compliance_question(
        "What are the current economic conditions and market risks we should monitor?"
    )
    
    if result["success"]:
        print("✅ Query successful!")
        print(f"\nAnswer ({len(result['answer'])} characters):")
        print("-" * 30)
        print(result["answer"][:500] + "..." if len(result["answer"]) > 500 else result["answer"])
        
        print(f"\n📚 Sources analyzed: {len(result['sources'])}")
        for i, source in enumerate(result['sources'][:3], 1):
            print(f"  {i}. {source['title']} ({source['paragraphs']} paragraphs)")
            
        print(f"\n✨ Total response length: {len(result['answer'])} characters")
        print("Ready for compliance audit trail!")
        
    else:
        print(f"❌ Error: {result['error']}")