#!/usr/bin/env python3
"""
Enterprise Knowledge Manager for DataVault Financial Services
Real Nuclia API implementation with multi-tenant simulation
Author: David Kim
"""

import os
import requests
import json
from typing import Dict, List
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env')

class EnterpriseKnowledgeManager:
    """
    Manages multiple knowledge boxes for different business units
    Uses real Nuclia API to demonstrate enterprise features
    """
    
    def __init__(self):
        self.api_key = os.getenv('NUCLIA_API_KEY')
        self.zone = os.getenv('NUCLIA_ZONE', 'aws-us-east-2-1')
        self.main_kb_id = os.getenv('NUCLIA_KB_ID', '45bd361a-7e42-487a-9ff9-c003e7a93560')
        
        # Simulate multi-tenant knowledge box structure
        # In production, these would be separate KBs
        self.knowledge_boxes = {
            'global_research': self.main_kb_id,      # Using main KB for demo
            'us_compliance': 'kb_us_compliance_demo',  # Simulated
            'eu_compliance': 'kb_eu_compliance_demo',  # Simulated
            'client_analytics': 'kb_client_demo'       # Simulated
        }
        
        # Role permissions matrix
        self.role_permissions = {
            'executive': ['global_research', 'client_analytics'],
            'analyst': ['global_research'],
            'compliance_us': ['global_research', 'us_compliance'],
            'compliance_eu': ['global_research', 'eu_compliance'],
            'client_manager': ['client_analytics', 'global_research']
        }
    
    def get_accessible_kbs(self, user_role: str, region: str) -> List[str]:
        """
        Determine which knowledge boxes a user can access
        based on their role and geographic location
        """
        # Get base permissions for role
        base_permissions = self.role_permissions.get(user_role, [])
        
        # Apply regional restrictions for compliance roles
        if 'compliance' in user_role:
            if region == 'US' and user_role == 'compliance_us':
                return base_permissions
            elif region == 'EU' and user_role == 'compliance_eu':
                return base_permissions
            else:
                return ['global_research']  # Default to global only
        
        return base_permissions
    
    def federated_search(self, query: str, user_context: Dict) -> Dict:
        """
        Execute search across allowed knowledge boxes using real Nuclia API
        """
        user_role = user_context.get('role', 'analyst')
        user_region = user_context.get('region', 'US')
        user_name = user_context.get('name', 'Unknown User')
        
        # Get accessible KBs for this user
        accessible_kbs = self.get_accessible_kbs(user_role, user_region)
        
        print(f"\n🔍 Executing Federated Search")
        print(f"   User: {user_name} ({user_role})")
        print(f"   Region: {user_region}")
        print(f"   Accessible KBs: {accessible_kbs}")
        
        # For demo, search the main KB (simulating federated search)
        if 'global_research' in accessible_kbs:
            results = self._search_nuclia_kb(query)
        else:
            results = {'answer': 'Access restricted - no available knowledge boxes', 'sources': []}
        
        return {
            'query': query,
            'user': user_name,
            'role': user_role,
            'region': user_region,
            'timestamp': datetime.now().isoformat(),
            'accessible_kbs': accessible_kbs,
            'results': results
        }
    
    def _search_nuclia_kb(self, query: str) -> Dict:
        """Execute real search on Nuclia KB using API"""
        
        url = f"https://{self.zone}.nuclia.cloud/api/v1/kb/{self.main_kb_id}/ask"
        
        headers = {
            "X-NUCLIA-SERVICEACCOUNT": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "features": ["semantic", "keyword"],
            "max_tokens": 500
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                # Parse NDJSON response
                answer_text = ""
                sources = []
                
                for line in response.text.strip().split('\n'):
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get("item", {}).get("type") == "answer":
                                answer_text += data["item"]["text"]
                            elif data.get("item", {}).get("type") == "retrieval":
                                resources = data["item"]["results"]["resources"]
                                for resource_id, resource in resources.items():
                                    sources.append({
                                        "title": resource.get("title", "Untitled"),
                                        "id": resource_id[:8] + "..."  # Shortened for display
                                    })
                        except json.JSONDecodeError:
                            continue
                
                return {
                    "answer": answer_text.strip() if answer_text else "No specific answer found.",
                    "sources": sources,
                    "source_count": len(sources)
                }
            else:
                return {
                    "error": f"API returned {response.status_code}",
                    "answer": "Search service temporarily unavailable",
                    "sources": []
                }
        except Exception as e:
            return {
                "error": str(e),
                "answer": "Unable to connect to search service",
                "sources": []
            }
    
    def validate_access(self, user_role: str, action: str, resource: str) -> bool:
        """
        Validate if user has permission for specific action on resource
        """
        permissions = {
            'compliance': {
                'read': ['compliance_*', 'global_research'],
                'write': ['compliance_*'],
                'delete': []
            },
            'analyst': {
                'read': ['global_research'],
                'write': ['global_research'],
                'delete': []
            },
            'executive': {
                'read': ['all'],
                'write': ['global_research', 'client_analytics'],
                'delete': []
            }
        }
        
        # Get base role (compliance_us -> compliance)
        base_role = user_role.split('_')[0] if '_' in user_role else user_role
        allowed = permissions.get(base_role, {}).get(action, [])
        
        # Check permissions
        if 'all' in allowed:
            return True
        
        for pattern in allowed:
            if '*' in pattern:
                prefix = pattern.replace('*', '')
                if prefix in resource:
                    return True
            elif resource == pattern:
                return True
        
        return False


def main():
    """Demo the enterprise knowledge management system with real API"""
    
    manager = EnterpriseKnowledgeManager()
    
    print("=" * 70)
    print("DataVault Enterprise Knowledge System - Real Nuclia API")
    print("=" * 70)
    
    # Test 1: Multi-tenant access control
    print("\n1. MULTI-TENANT ACCESS CONTROL")
    print("-" * 70)
    
    test_users = [
        {'name': 'Sarah Rodriguez', 'role': 'compliance_us', 'region': 'US'},
        {'name': 'Marcus Chen', 'role': 'executive', 'region': 'US'},
        {'name': 'European Compliance', 'role': 'compliance_eu', 'region': 'EU'},
        {'name': 'Lisa Thompson', 'role': 'analyst', 'region': 'US'}
    ]
    
    for user in test_users:
        accessible = manager.get_accessible_kbs(user['role'], user['region'])
        print(f"{user['name']} ({user['role']}): {accessible}")
    
    # Test 2: Access validation
    print("\n2. ACCESS VALIDATION")
    print("-" * 70)
    
    test_cases = [
        ('compliance', 'read', 'compliance_us'),
        ('compliance', 'write', 'compliance_us'),
        ('compliance', 'delete', 'compliance_us'),
        ('analyst', 'read', 'global_research'),
        ('analyst', 'write', 'eu_compliance'),
        ('executive', 'read', 'client_analytics')
    ]
    
    for role, action, resource in test_cases:
        result = manager.validate_access(role, action, resource)
        status = "✅" if result else "❌"
        print(f"{status} {role}: {action} on {resource} = {result}")
    
    # Test 3: Real API search - Sarah Rodriguez (US Compliance)
    print("\n3. REAL API SEARCH - US COMPLIANCE OFFICER")
    print("-" * 70)
    
    sarah_context = {
        'name': 'Sarah Rodriguez',
        'role': 'compliance_us',
        'region': 'US'
    }
    
    query = "What are the key regulatory requirements for financial services?"
    result = manager.federated_search(query, sarah_context)
    
    print(f"\n📋 Query: '{query}'")
    print(f"⏰ Timestamp: {result['timestamp']}")
    
    if 'error' not in result['results']:
        answer = result['results'].get('answer', 'No answer')
        print(f"\n💡 Answer from Nuclia:")
        print(f"   {answer[:400]}..." if len(answer) > 400 else f"   {answer}")
        print(f"\n📑 Sources: {result['results'].get('source_count', 0)} documents found")
        
        if result['results'].get('sources'):
            print("   Top sources:")
            for i, source in enumerate(result['results']['sources'][:3], 1):
                print(f"   {i}. {source['title']}")
    else:
        print(f"\n⚠️ Error: {result['results'].get('error')}")
    
    # Test 4: Executive multi-context access
    print("\n4. EXECUTIVE MULTI-CONTEXT ACCESS")
    print("-" * 70)
    
    marcus_context = {
        'name': 'Marcus Chen',
        'role': 'executive',
        'region': 'US'
    }
    
    exec_query = "Market trends and investment opportunities"
    exec_result = manager.federated_search(exec_query, marcus_context)
    
    print(f"\n📋 Query: '{exec_query}'")
    print(f"👤 User: {exec_result['user']} can access: {exec_result['accessible_kbs']}")
    
    if 'error' not in exec_result['results']:
        print(f"✅ Search executed successfully")
        print(f"📑 Sources found: {exec_result['results'].get('source_count', 0)}")
    
    print("\n" + "=" * 70)
    print("Enterprise API Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()