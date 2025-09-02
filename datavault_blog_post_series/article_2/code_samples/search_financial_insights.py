# search_financial_insights.py
import os
from dotenv import load_dotenv
from nuclia import sdk

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
    
    # Initialize Nuclia authentication
    kb_url = f"https://{NUCLIA_ZONE}.nuclia.cloud/api/v1/kb/{KB_ID}"
    sdk.NucliaAuth().kb(url=kb_url, token=NUCLIA_API_KEY)
    
    # Create search instance
    search_client = sdk.NucliaSearch()
    
    # Perform the search using Nuclia SDK
    try:
        response = search_client.find(
            query=query,
            filters=None  # Can add filters like ['/icon/application/pdf']
        )
        
        # Process results from multiple sources
        results = {
            'documents': [],
            'news': [],
            'compliance': []
        }
        
        if response and hasattr(response, 'resources') and response.resources:
            for resource_id, resource in response.resources.items():
                # Extract title and summary from resource
                title = resource.title if hasattr(resource, 'title') else 'Untitled'
                summary = resource.summary if hasattr(resource, 'summary') else ''
                
                # If no summary, try to get text from paragraphs
                if not summary and hasattr(resource, 'paragraphs') and resource.paragraphs:
                    for para_id, para in resource.paragraphs.items():
                        if 'text' in para:
                            summary = para['text'][:200] + '...' if len(para['text']) > 200 else para['text']
                            break
                
                # Categorize by source or title
                title_lower = title.lower()
                if any(news in title_lower for news in ['wsj', 'wall street', 'marketwatch', 'reuters', 'bloomberg', 'federal reserve']):
                    results['news'].append({'title': title, 'summary': summary})
                elif any(comp in title_lower for comp in ['compliance', 'sec', 'regulatory', 'risk', 'disclosure']):
                    results['compliance'].append({'title': title, 'summary': summary})
                else:
                    results['documents'].append({'title': title, 'summary': summary})
        
        # Display results
        if show_details:
            print(f"\n🔍 Query: '{query}'")
            print(f"📊 Total results: {len(results['documents']) + len(results['news']) + len(results['compliance'])}")
            
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
        if NUCLIA_API_KEY == 'YOUR_API_KEY_HERE':
            print("\n⚠️  No API key configured.")
            print("To use this script with real data:")
            print("1. Create a .env file from .env.template")
            print("2. Add your Nuclia API key and Knowledge Box ID")
            print("3. Run the script again")
        return None

# Test the search with Sarah's compliance query
if __name__ == "__main__":
    # Sarah's audit query
    test_query = "risk disclosure regulatory compliance SEC requirements"
    
    print("Testing Nuclia SDK Search Implementation")
    print("=" * 50)
    
    # Try real search
    results = search_financial_insights(test_query)
    
    if results is None:
        print("\n" + "=" * 50)
        print("Note: Configure your API credentials to see real results")
        print("The SDK implementation requires valid credentials.")