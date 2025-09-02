# search_financial_insights.py
from nuclia import sdk
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DataVault's InvestmentInsights Knowledge Box configuration
NUCLIA_API_KEY = os.environ.get('NUCLIA_API_KEY', 'YOUR_API_KEY_HERE')
NUCLIA_ZONE = os.environ.get('NUCLIA_ZONE', 'aws-us-east-2-1')
KB_ID = os.environ.get('NUCLIA_KB_ID', 'investmentinsights')

def search_financial_insights(query, show_details=True):
    """
    Search across all DataVault's financial documents
    with semantic understanding using Nuclia SDK
    """
    
    # Initialize Nuclia SDK client
    auth = sdk.NucliaAuth()
    auth.kb(KB_ID)
    auth.nua_key(NUCLIA_API_KEY)
    
    # Create the SDK instance
    nuclia = sdk.NucliaSDK(auth)
    
    # Configure search parameters
    search_params = {
        'query': query,
        'features': ['keyword', 'semantic', 'relations'],
        'min_score': 0.7,
        'page_size': 10
    }
    
    # Perform the search using SDK
    try:
        response = nuclia.search(**search_params)
        data = response.json() if hasattr(response, 'json') else response
        
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
    except Exception as e:
        print(f"Error performing search: {str(e)}")
        return None

# Test the search with Sarah's compliance query
if __name__ == "__main__":
    # Sarah's audit query
    test_query = "risk disclosure regulatory compliance SEC requirements"
    results = search_financial_insights(test_query)