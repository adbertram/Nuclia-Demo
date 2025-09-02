# Installation Notes for Article 2 Code Samples

## Nuclia SDK Installation

✅ **WORKING**: This article uses Nuclia Python SDK version 4.9.8 (latest stable as of September 2025)

### Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Version History
- **nuclia 3.0.0** - Had pydantic dependency conflicts with nucliadb-models
- **nuclia 4.9.8** - Current stable version, all dependency conflicts resolved

### Files Using SDK
All Python files in this folder use the Nuclia SDK:
1. **search_financial_insights.py** - Core search implementation using SDK
2. **compliance_audit_query.py** - Compliance audit query using SDK  
3. **rss_feed_config.py** - RSS feed configuration examples
4. **search_config.py** - Search configuration examples
5. **test_nuclia_search.py** - Tests for SDK functionality

The article demonstrates the correct SDK usage patterns for integrating with Nuclia's RAG-as-a-Service platform.