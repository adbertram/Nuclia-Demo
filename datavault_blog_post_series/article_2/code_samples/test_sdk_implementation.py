#!/usr/bin/env python3
"""
Test script to validate the Nuclia SDK implementation
This tests the code exactly as shown in Article 2
"""

import sys
import os

def test_imports():
    """Test that all required imports work"""
    try:
        from nuclia import sdk
        print("✅ Nuclia SDK import successful")
        
        import json
        print("✅ JSON import successful")
        
        from dotenv import load_dotenv
        print("✅ dotenv import successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTo fix this, run:")
        print("pip install nuclia python-dotenv")
        return False

def test_sdk_initialization():
    """Test SDK initialization pattern from the article"""
    try:
        from nuclia import sdk
        
        # Test configuration from article
        NUCLIA_API_KEY = "test_key_placeholder"
        NUCLIA_ZONE = "aws-us-east-2-1"
        KB_ID = "investmentinsights"
        
        # Test the initialization pattern
        auth = sdk.NucliaAuth()
        auth.kb(KB_ID)
        auth.nua_key(NUCLIA_API_KEY)
        
        print("✅ SDK authentication object created successfully")
        
        # Note: We can't create actual SDK instance without valid credentials
        # but we've validated the code structure
        print("✅ SDK initialization pattern validated")
        
        return True
    except Exception as e:
        print(f"❌ SDK initialization error: {e}")
        return False

def test_search_function_structure():
    """Test the search function structure"""
    try:
        # Import the actual function
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Test that our search_financial_insights.py has correct structure
        with open('search_financial_insights.py', 'r') as f:
            content = f.read()
            
        # Check for key SDK components
        checks = [
            ('from nuclia import sdk', 'Nuclia SDK import'),
            ('sdk.NucliaAuth()', 'SDK Auth initialization'),
            ('auth.kb(KB_ID)', 'Knowledge Box configuration'),
            ('auth.nua_key(NUCLIA_API_KEY)', 'API Key configuration'),
            ('sdk.NucliaSDK(auth)', 'SDK instance creation'),
            ('nuclia.search(**search_params)', 'Search method call')
        ]
        
        all_good = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description} found")
            else:
                print(f"❌ {description} missing")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error testing search function: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("DataVault Financial Services - Nuclia SDK Implementation Test")
    print("Testing Article 2 Code Implementation")
    print("=" * 60)
    print()
    
    print("1. Testing Imports...")
    print("-" * 30)
    imports_ok = test_imports()
    print()
    
    if imports_ok:
        print("2. Testing SDK Initialization Pattern...")
        print("-" * 30)
        sdk_ok = test_sdk_initialization()
        print()
        
        print("3. Testing Search Function Structure...")
        print("-" * 30)
        search_ok = test_search_function_structure()
        print()
        
        if sdk_ok and search_ok:
            print("=" * 60)
            print("✅ ALL TESTS PASSED")
            print("The SDK implementation matches Article 2 requirements")
            print("=" * 60)
            return 0
    
    print("=" * 60)
    print("❌ SOME TESTS FAILED")
    print("Please install dependencies: pip install nuclia python-dotenv")
    print("=" * 60)
    return 1

if __name__ == "__main__":
    sys.exit(main())