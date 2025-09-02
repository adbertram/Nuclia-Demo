# test_nuclia_search.py
# Test suite for Nuclia SDK search functionality
# As shown in Article 2 - David's validation before Sarah's critical demo

import os
import pytest
from dotenv import load_dotenv
from nuclia import sdk

# Load environment variables
load_dotenv()

class TestNucliaSearch:
    """Test suite for Nuclia SDK search implementation"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.api_key = os.environ.get('NUCLIA_API_KEY', 'test_key')
        cls.zone = os.environ.get('NUCLIA_ZONE', 'aws-us-east-2-1')
        cls.kb_id = os.environ.get('NUCLIA_KB_ID', 'investmentinsights')
        cls.kb_url = f"https://{cls.zone}.nuclia.cloud/api/v1/kb/{cls.kb_id}"
    
    def test_sdk_authentication(self):
        """Test that SDK authentication can be set"""
        # This sets the authentication globally
        sdk.NucliaAuth().kb(url=self.kb_url, token=self.api_key)
        assert True  # If no exception, auth was set
    
    def test_search_client_creation(self):
        """Test that search client can be created"""
        search_client = sdk.NucliaSearch()
        assert search_client is not None
        assert hasattr(search_client, 'search')
        assert hasattr(search_client, 'find')
        assert hasattr(search_client, 'ask')
    
    def test_search_with_query(self):
        """Test basic search functionality"""
        sdk.NucliaAuth().kb(url=self.kb_url, token=self.api_key)
        search_client = sdk.NucliaSearch()
        
        # Test search with real API
        response = search_client.find(
            query="test query",
            filters=None
        )
        assert response is not None
    
    def test_compliance_search(self):
        """Test compliance-specific search query"""
        sdk.NucliaAuth().kb(url=self.kb_url, token=self.api_key)
        search_client = sdk.NucliaSearch()
        
        # Sarah's compliance query
        query = "risk disclosure regulatory compliance SEC requirements"
        
        # Test search with real API
        response = search_client.find(
            query=query,
            filters=None
        )
        assert response is not None
    
    def test_search_with_filters(self):
        """Test search with various filter options"""
        sdk.NucliaAuth().kb(url=self.kb_url, token=self.api_key)
        search_client = sdk.NucliaSearch()
        
        filters = [
            None,
            ['/icon/application/pdf'],
            ['/classification.labels/region/Europe'],
            ['/icon/application/pdf', '/classification.labels/compliance/SEC']
        ]
        
        for filter_set in filters:
            # Test each filter combination with real API
            response = search_client.find(
                query="financial markets",
                filters=filter_set
            )
            assert response is not None
    
    def test_financial_terms_search(self):
        """Test search for specific financial terms"""
        sdk.NucliaAuth().kb(url=self.kb_url, token=self.api_key)
        search_client = sdk.NucliaSearch()
        
        financial_terms = [
            "Basel III requirements",
            "systemic risk assessment",
            "Federal Reserve policy",
            "market volatility analysis",
            "portfolio risk management"
        ]
        
        for term in financial_terms:
            # Test each financial term with real API
            response = search_client.find(query=term)
            assert response is not None
    
    def test_ask_method(self):
        """Test the ask method for generative answers"""
        sdk.NucliaAuth().kb(url=self.kb_url, token=self.api_key)
        search_client = sdk.NucliaSearch()
        
        # Test ask method with real API
        response = search_client.ask(
            query="What are the Basel III requirements?"
        )
        assert response is not None
    
    def test_search_error_handling(self):
        """Test that SDK properly handles errors"""
        # Test with invalid URL should raise an exception
        invalid_url = "https://invalid.nuclia.cloud/api/v1/kb/invalid"
        
        # This should raise an exception when trying to connect
        with pytest.raises(Exception):
            sdk.NucliaAuth().kb(url=invalid_url, token="invalid_key")

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])