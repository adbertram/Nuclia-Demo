import requests
import json
import os

# Load environment variables
def load_env():
    env_vars = {}
    try:
        with open('code_samples/.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print("Error: .env file not found")
        return None
    return env_vars

def ask_compliance_question(question):
    """
    Query DataVault's Nuclia knowledge box programmatically
    """
    env_vars = load_env()
    if not env_vars:
        return {"error": "Could not load environment variables"}
    
    kb_id = env_vars.get('NUCLIA_KB_ID', 'investmentinsights')
    api_key = env_vars.get('NUCLIA_API_KEY')
    zone = env_vars.get('NUCLIA_ZONE', 'aws-us-east-2-1')
    
    # Nuclia Ask API endpoint
    url = f"https://{zone}.nuclia.cloud/api/v1/kb/{kb_id}/ask"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": question,
        "features": ["semantic", "keyword"],
        "max_tokens": 1000,
        "show_source": True
    }
    
    try:
        print(f"Making request to: {url}")
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
print("Testing Nuclia API with real credentials...")
compliance_answer = ask_compliance_question(
    "What are the current economic conditions and market risks we should monitor?"
)

print("\nResult:")
if "error" not in compliance_answer:
    print("✅ SUCCESS!")
    print("AI Answer:", compliance_answer["answer"][:200] + "..." if len(compliance_answer["answer"]) > 200 else compliance_answer["answer"])
    print(f"Sources found: {len(compliance_answer['sources'])}")
    if compliance_answer['sources']:
        print("First source:", compliance_answer['sources'][0] if compliance_answer['sources'] else "None")
else:
    print(f"❌ Error: {compliance_answer['error']}")