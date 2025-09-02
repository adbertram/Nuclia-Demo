# search_financial_insights.py
import urllib.request
import urllib.parse
import json
import os
import ssl

# DataVault's InvestmentInsights Knowledge Box configuration
NUCLIA_API_KEY = os.environ.get('NUCLIA_API_KEY', 'YOUR_API_KEY_HERE')
KB_ID = '45bd361a-7e42-487a-9ff9-c003e7a93560'
API_ENDPOINT = f'https://aws-us-east-2-1.nuclia.cloud/api/v1/kb/{KB_ID}/search'

def search_financial_insights(query, show_details=True):
    """
    Search across all DataVault's financial documents
    with semantic understanding
    """
    headers = {
        'X-NUCLIA-SERVICEACCOUNT': f'Bearer {NUCLIA_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'query': query,
        'features': ['keyword', 'semantic', 'relations'],
        'min_score': 0.7,
        'page_size': 10
    }
    
    # Convert payload to JSON
    data = json.dumps(payload).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(API_ENDPOINT, data=data, headers=headers)
    
    # Make the request
    try:
        response = urllib.request.urlopen(req)
        response_data = response.read().decode('utf-8')
        status_code = response.getcode()
    except urllib.error.HTTPError as e:
        status_code = e.code
        response_data = e.read().decode('utf-8')
    
    if status_code == 200:
        data = json.loads(response_data)
        
        # Process results from multiple sources
        results = {
            'documents': [],
            'news': [],
            'compliance': []
        }
        
        if 'resources' in data:
            for resource_id, resource_data in data['resources'].items():
                # Extract title and summary
                title = resource_data.get('title', 'Untitled')
                summary = ''
                
                # Get summary from paragraphs if available
                if 'paragraphs' in resource_data:
                    for para_id, para_data in resource_data['paragraphs'].items():
                        if 'text' in para_data:
                            summary = para_data['text'][:200] + '...'
                            break
                
                # Categorize by source
                if 'wsj.com' in title.lower() or 'marketwatch' in title.lower():
                    results['news'].append({'title': title, 'summary': summary})
                elif 'compliance' in title.lower() or 'sec' in title.lower():
                    results['compliance'].append({'title': title, 'summary': summary})
                else:
                    results['documents'].append({'title': title, 'summary': summary})
        
        # Display results
        if show_details:
            print(f"\n🔍 Query: '{query}'")
            print(f"📊 Total results: {data.get('total', 0)}")
            
            if results['compliance']:
                print("\n📋 Compliance Documents:")
                for doc in results['compliance'][:3]:
                    print(f"  • {doc['title']}")
            
            if results['news']:
                print("\n📰 Recent News:")
                for article in results['news'][:3]:
                    print(f"  • {article['title']}")
            
            if results['documents']:
                print("\n📄 Research Documents:")
                for doc in results['documents'][:3]:
                    print(f"  • {doc['title']}")
        
        return results
    else:
        print(f"Error: {status_code} - {response_data}")
        return None

# Test the search with Sarah's compliance query
if __name__ == "__main__":
    # Sarah's audit query
    test_query = "risk disclosure regulatory compliance SEC requirements"
    results = search_financial_insights(test_query)