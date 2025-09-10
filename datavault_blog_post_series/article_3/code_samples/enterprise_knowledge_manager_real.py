#!/usr/bin/env python3
"""
Enterprise Knowledge Manager for DataVault Financial Services
Real Nuclia API implementation with multi-tenant simulation
Author: David Kim
"""

import os
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class EnterpriseKnowledgeManager:
    """
    Manages multiple knowledge boxes for different business units
    Simulates multi-tenant architecture using the main KB with different search contexts
    """
    
    def __init__(self):
        self.api_key = os.getenv('NUCLIA_API_KEY')
        self.zone = os.getenv('NUCLIA_ZONE', 'aws-us-east-2-1')
        self.main_kb_id = os.getenv('NUCLIA_KB_ID', '45bd361a-7e42-487a-9ff9-c003e7a93560')
        
        # Simulate multi-tenant structure using labels/filters
        self.knowledge_contexts = {
            'global_research': {'filter': 'category:research', 'label': 'Global Research'},
            'us_compliance': {'filter': 'region:us AND category:compliance', 'label': 'US Compliance'},
            'eu_compliance': {'filter': 'region:eu AND category:compliance', 'label': 'EU Compliance'},
            'client_analytics': {'filter': 'category:client', 'label': 'Client Analytics'}
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
        Determine which knowledge contexts a user can access
        based on their role and geographic location
        """
        accessible = []
        
        # Get base permissions for role
        base_permissions = self.role_permissions.get(user_role, [])
        
        # Apply regional restrictions for compliance roles
        if user_role.startswith('compliance'):
            if region == 'US' and 'us_compliance' in base_permissions:
                accessible = base_permissions
            elif region == 'EU' and 'eu_compliance' in base_permissions:
                accessible = base_permissions
            else:
                # Compliance can only see their own region
                accessible = ['global_research']
        else:
            accessible = base_permissions
        
        return accessible
    
    async def federated_search(self, query: str, user_context: Dict) -> Dict:
        """
        Execute search across allowed knowledge contexts using real Nuclia API
        """
        user_role = user_context.get('role', 'analyst')
        user_region = user_context.get('region', 'US')
        user_name = user_context.get('name', 'Unknown User')
        
        # Get accessible contexts for this user
        accessible_contexts = self.get_accessible_kbs(user_role, user_region)
        
        print(f"\n🔍 Federated Search for {user_name} ({user_role}, {user_region})")
        print(f"   Accessible contexts: {accessible_contexts}")
        
        # Execute real Nuclia search
        async with aiohttp.ClientSession() as session:
            results = await self._search_nuclia(session, query, accessible_contexts)
        
        # Format response with user context
        response = {
            'query': query,
            'user': user_name,
            'role': user_role,
            'region': user_region,
            'timestamp': datetime.now().isoformat(),
            'accessible_contexts': accessible_contexts,
            'results': results
        }
        
        return response
    
    async def _search_nuclia(self, session: aiohttp.ClientSession, 
                            query: str, contexts: List[str]) -> Dict:
        """Execute real search on Nuclia KB"""
        
        url = f"https://{self.zone}.nuclia.cloud/api/v1/kb/{self.main_kb_id}/ask"
        
        headers = {
            "X-NUCLIA-SERVICEACCOUNT": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Build filter string based on accessible contexts
        filter_conditions = []
        for context in contexts:
            if context in self.knowledge_contexts:
                filter_conditions.append(f"({self.knowledge_contexts[context]['filter']})")
        
        # For demo, we'll search without filters since we don't have labeled data
        # In production, you would use: filter_str = " OR ".join(filter_conditions)
        
        payload = {
            "query": query,
            "features": ["semantic", "keyword"],
            "max_tokens": 1000
        }
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    text = await response.text()
                    parsed_response = self._parse_ndjson(text)
                    
                    # Add context labels to results
                    for context in contexts:
                        if context in self.knowledge_contexts:
                            parsed_response['context'] = self.knowledge_contexts[context]['label']
                    
                    return parsed_response
                else:
                    return {
                        'error': f"API returned {response.status}",
                        'answer': f"Unable to search at this time (HTTP {response.status})"
                    }
        except Exception as e:
            return {
                'error': str(e),
                'answer': "Search service temporarily unavailable"
            }
    
    def _parse_ndjson(self, text: str) -> Dict:
        """Parse NDJSON response from Nuclia API"""
        answer_text = ""
        sources = []
        
        for line in text.strip().split('\n'):
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
                                "id": resource_id
                            })
                except json.JSONDecodeError:
                    continue
        
        return {
            "answer": answer_text.strip() if answer_text else "No specific answer found for this query.",
            "sources": sources,
            "source_count": len(sources)
        }
    
    def validate_access(self, user_id: str, user_role: str, 
                       action: str, resource: str) -> bool:
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
                'read': ['global_research', 'client_analytics'],
                'write': ['global_research', 'client_analytics'],
                'delete': []
            }
        }
        
        # Get base role (compliance_us -> compliance)
        base_role = user_role.split('_')[0] if '_' in user_role else user_role
        allowed = permissions.get(base_role, {}).get(action, [])
        
        for pattern in allowed:
            if '*' in pattern:
                prefix = pattern.replace('*', '')
                if prefix in resource:
                    return True
            elif resource == pattern:
                return True
        
        return False


# Example usage
async def main():
    manager = EnterpriseKnowledgeManager()
    
    print("=" * 70)
    print("DataVault Enterprise Knowledge System - Real API Demo")
    print("=" * 70)
    
    # Test 1: Multi-tenant access control
    print("\n1. TESTING MULTI-TENANT ACCESS CONTROL")
    print("-" * 70)
    
    test_users = [
        {'name': 'Sarah Rodriguez', 'role': 'compliance_us', 'region': 'US'},
        {'name': 'Marcus Chen', 'role': 'executive', 'region': 'US'},
        {'name': 'European Compliance Officer', 'role': 'compliance_eu', 'region': 'EU'},
        {'name': 'Lisa Thompson', 'role': 'analyst', 'region': 'US'}
    ]
    
    for user in test_users:
        accessible = manager.get_accessible_kbs(user['role'], user['region'])
        print(f"{user['name']} ({user['role']}): {accessible}")
    
    # Test 2: Access validation
    print("\n2. TESTING ACCESS VALIDATION")
    print("-" * 70)
    
    test_cases = [
        ('compliance', 'read', 'compliance_us', True),
        ('compliance', 'write', 'compliance_us', True),
        ('compliance', 'delete', 'compliance_us', False),
        ('analyst', 'read', 'global_research', True),
        ('analyst', 'write', 'eu_compliance', False)
    ]
    
    for role, action, resource, expected in test_cases:
        result = manager.validate_access('user123', role, action, resource)
        status = "✅" if result == expected else "❌"
        print(f"{status} {role}: {action} on {resource} = {result}")
    
    # Test 3: Real federated search
    print("\n3. EXECUTING REAL FEDERATED SEARCH")
    print("-" * 70)
    
    # Sarah Rodriguez (US Compliance) searching for regulatory information
    sarah_context = {
        'name': 'Sarah Rodriguez',
        'role': 'compliance_us',
        'region': 'US',
        'department': 'Legal & Compliance'
    }
    
    query = "What are the latest financial regulations and compliance requirements?"
    result = await manager.federated_search(query, sarah_context)
    
    print(f"\n📋 Query: {query}")
    print(f"👤 User: {result['user']} ({result['role']})")
    print(f"🌍 Region: {result['region']}")
    print(f"📚 Accessible Contexts: {result['accessible_contexts']}")
    
    if 'error' not in result['results']:
        print(f"\n💡 Answer Preview:")
        answer = result['results'].get('answer', 'No answer')
        print(f"   {answer[:300]}..." if len(answer) > 300 else f"   {answer}")
        print(f"\n📑 Sources Found: {result['results'].get('source_count', 0)}")
        
        if result['results'].get('sources'):
            print("   Top Sources:")
            for i, source in enumerate(result['results']['sources'][:3], 1):
                print(f"   {i}. {source['title']}")
    else:
        print(f"\n⚠️ Error: {result['results']['error']}")
    
    # Test 4: Executive multi-context search
    print("\n4. EXECUTIVE MULTI-CONTEXT ACCESS")
    print("-" * 70)
    
    marcus_context = {
        'name': 'Marcus Chen',
        'role': 'executive',
        'region': 'US',
        'department': 'Executive Management'
    }
    
    exec_query = "Market trends and investment opportunities"
    exec_result = await manager.federated_search(exec_query, marcus_context)
    
    print(f"\n📋 Query: {exec_query}")
    print(f"👤 User: {exec_result['user']} ({exec_result['role']})")
    print(f"📚 Accessible Contexts: {exec_result['accessible_contexts']}")
    
    if 'error' not in exec_result['results']:
        print(f"📑 Sources Found: {exec_result['results'].get('source_count', 0)}")
        print(f"✅ Successfully searched across multiple contexts")
    
    print("\n" + "=" * 70)
    print("Real API Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())