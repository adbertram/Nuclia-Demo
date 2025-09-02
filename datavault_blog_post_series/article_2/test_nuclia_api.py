import requests
import json

# DataVault's actual implementation
def ask_compliance_question(question):
    """
    Query DataVault's Nuclia knowledge box programmatically
    """
    kb_id = "investment-insights-kb"
    api_key = "YOUR_API_KEY"  # This would be replaced with real API key
    
    # Nuclia Ask API endpoint
    url = f"https://nuclia.cloud/api/v1/kb/{kb_id}/ask"
    
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
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            return {
                "answer": result.get("text", ""),
                "sources": result.get("citations", []),
                "relations": result.get("relations", [])
            }
        else:
            return {
                "error": f"API returned {response.status_code}",
                "response": response.text
            }
    except Exception as e:
        return {"error": str(e)}

# Sarah's urgent compliance question
print("Testing Nuclia API call...")
compliance_answer = ask_compliance_question(
    "What are the current economic conditions and market risks we should monitor?"
)

print("Result:")
if "error" in compliance_answer:
    print(f"Error: {compliance_answer['error']}")
    print("Note: This requires a valid API key and knowledge box to work properly")
else:
    print("AI Answer:", compliance_answer["answer"])
    print(f"Sources found: {len(compliance_answer['sources'])}")