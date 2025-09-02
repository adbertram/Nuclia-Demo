# search_config.py
# Search configuration for financial data optimization
# As implemented by David Kim for DataVault Financial Services

"""
Technical Insights from Article 2:
DataVault discovered these optimal settings for financial document search
after extensive testing with their 20-year archive of research reports.
"""

# Search configuration for financial data
search_config = {
    'semantic_weight': 0.7,  # Understand intent
    'keyword_weight': 0.3,   # Catch specific terms
    'enable_synonyms': True,  # "Fed" = "Federal Reserve"
    'boost_recent': True,    # Prioritize recent news
    'min_confidence': 0.75   # High accuracy requirement
}

# Data Source Priority Configuration
# Not all sources are equal - DataVault structured their ingestion priority
data_source_priority = {
    'compliance_documents': {
        'priority': 1,
        'update_frequency': 'daily',
        'description': 'Regulatory and compliance documentation'
    },
    'market_news': {
        'priority': 2,
        'update_frequency': 'real-time',
        'description': 'RSS feeds from financial news sources'
    },
    'historical_analyses': {
        'priority': 3,
        'update_frequency': 'weekly',
        'description': 'Research reports and historical data'
    }
}

# Performance Tuning Settings
performance_tuning = {
    'chunking_strategy': {
        'regulatory_documents': 512,   # tokens for regulatory documents
        'research_reports': 1024       # tokens for research reports
    },
    'metadata_extraction': {
        'auto_date': True,
        'auto_source': True,
        'auto_category': True
    },
    'update_frequency': {
        'rss_feeds': 15,     # minutes
        'documents': 60      # minutes
    }
}

# Synonym Configuration for Financial Terms
financial_synonyms = {
    'Fed': ['Federal Reserve', 'FOMC', 'Federal Open Market Committee'],
    'SEC': ['Securities and Exchange Commission', 'securities regulator'],
    'Basel': ['Basel III', 'Basel Accord', 'Basel Framework'],
    'QE': ['Quantitative Easing', 'asset purchases', 'monetary stimulus'],
    'rate hike': ['interest rate increase', 'tightening', 'rate rise'],
    'bear market': ['market decline', 'downturn', 'correction'],
    'bull market': ['market rally', 'uptrend', 'market gains']
}

def apply_search_config(nuclia_search_params):
    """
    Apply DataVault's optimized search configuration to Nuclia search parameters
    
    Args:
        nuclia_search_params: Base search parameters dictionary
    
    Returns:
        Enhanced search parameters with DataVault's optimizations
    """
    
    # Apply semantic and keyword weights
    if 'features' not in nuclia_search_params:
        nuclia_search_params['features'] = []
    
    # Ensure both semantic and keyword search are enabled
    if 'semantic' not in nuclia_search_params['features']:
        nuclia_search_params['features'].append('semantic')
    if 'keyword' not in nuclia_search_params['features']:
        nuclia_search_params['features'].append('keyword')
    
    # Apply minimum confidence score
    nuclia_search_params['min_score'] = search_config['min_confidence']
    
    # Enable relations for better context understanding
    if 'relations' not in nuclia_search_params['features']:
        nuclia_search_params['features'].append('relations')
    
    return nuclia_search_params

def expand_query_with_synonyms(query):
    """
    Expand search query with financial synonyms
    
    Args:
        query: Original search query
    
    Returns:
        Expanded query with relevant synonyms
    """
    
    expanded_terms = []
    query_lower = query.lower()
    
    for term, synonyms in financial_synonyms.items():
        if term.lower() in query_lower:
            expanded_terms.extend(synonyms)
    
    if expanded_terms:
        return f"{query} {' '.join(expanded_terms)}"
    return query

def get_source_priority(source_type):
    """
    Get the processing priority for a data source
    
    Args:
        source_type: Type of data source
    
    Returns:
        Priority level (1 = highest)
    """
    
    if source_type in data_source_priority:
        return data_source_priority[source_type]['priority']
    return 999  # Default low priority

if __name__ == "__main__":
    print("DataVault Financial Services - Search Configuration")
    print("=" * 60)
    print()
    
    print("Search Strategy Optimization:")
    print("-" * 30)
    for key, value in search_config.items():
        print(f"  {key}: {value}")
    print()
    
    print("Data Source Priorities:")
    print("-" * 30)
    for source, config in data_source_priority.items():
        print(f"  Priority {config['priority']}: {source}")
        print(f"    Update: {config['update_frequency']}")
        print(f"    Description: {config['description']}")
    print()
    
    print("Performance Tuning:")
    print("-" * 30)
    print(f"  Chunking Strategy:")
    for doc_type, tokens in performance_tuning['chunking_strategy'].items():
        print(f"    {doc_type}: {tokens} tokens")
    print(f"  Update Frequency:")
    for source, minutes in performance_tuning['update_frequency'].items():
        print(f"    {source}: every {minutes} minutes")
    print()
    
    # Example query expansion
    test_query = "Fed interest rate policy"
    expanded = expand_query_with_synonyms(test_query)
    print("Query Expansion Example:")
    print("-" * 30)
    print(f"  Original: {test_query}")
    print(f"  Expanded: {expanded}")
    print()
    
    print("Implementation Note:")
    print("-" * 30)
    print("These settings enabled DataVault to achieve:")
    print("  • 70% reduction in research time")
    print("  • 90% faster compliance audits")
    print("  • Instant correlation between real-time and historical data")