#!/usr/bin/env python3
"""
Enterprise Knowledge Manager for DataVault Financial Services
Handles multi-tenant knowledge box architecture with role-based access
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
    Manages multiple knowledge boxes for different business units and regions
    with role-based access control
    """
    
    def __init__(self):
        self.api_key = os.getenv('NUCLIA_API_KEY')
        self.zone = "aws-us-east-2-1"
        
        # Multi-tenant knowledge box structure
        self.knowledge_boxes = {
            'global_research': '45bd361a-7e42-487a-9ff9-c003e7a93560',  # Main KB from Article 2
            'us_compliance': 'kb_us_compliance_demo',     # US-only regulated data
            'eu_compliance': 'kb_eu_compliance_demo',     # EU GDPR-compliant data
            'client_analytics': 'kb_client_facing_demo',  # Client-accessible insights
            'internal_training': 'kb_training_demo'       # Employee resources
        }
        
        # Role permissions matrix
        self.role_permissions = {
            'executive': ['global_research', 'us_compliance', 'eu_compliance', 'client_analytics'],
            'analyst': ['global_research', 'internal_training'],
            'compliance_us': ['global_research', 'us_compliance'],
            'compliance_eu': ['global_research', 'eu_compliance'],
            'client_manager': ['client_analytics', 'global_research'],
            'employee': ['internal_training']
        }
    
    async def federated_search(self, query: str, user_context: Dict) -> Dict:
        """
        Execute parallel searches across allowed knowledge boxes based on user permissions
        """
        user_role = user_context.get('role', 'employee')
        user_region = user_context.get('region', 'US')
        
        # Get accessible KBs for this user
        accessible_kbs = self._get_accessible_kbs(user_role, user_region)
        
        # Create async tasks for parallel searching
        async with aiohttp.ClientSession() as session:
            tasks = []
            for kb_name in accessible_kbs:
                if kb_name in self.knowledge_boxes:
                    kb_id = self.knowledge_boxes[kb_name]
                    # For demo, we'll use the main KB ID for all searches
                    if kb_name == 'global_research':
                        task = self._search_kb(session, kb_id, query, kb_name)
                        tasks.append(task)
            
            if not tasks:
                # If no real KB available, return mock response
                return self._mock_federated_response(query, accessible_kbs)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results from all KBs
        return self._aggregate_results(results, query, user_context)
    
    def _get_accessible_kbs(self, role: str, region: str) -> List[str]:
        """Determine which KBs user can access based on role and region"""
        
        base_kbs = self.role_permissions.get(role, ['internal_training'])
        
        # Apply regional restrictions
        if region == 'EU' and 'us_compliance' in base_kbs:
            base_kbs = [kb for kb in base_kbs if kb != 'us_compliance']
        elif region == 'US' and 'eu_compliance' in base_kbs:
            base_kbs = [kb for kb in base_kbs if kb != 'eu_compliance']
        
        return base_kbs
    
    async def _search_kb(self, session: aiohttp.ClientSession, kb_id: str, 
                        query: str, kb_name: str) -> Dict:
        """Execute search on a single knowledge box"""
        
        url = f"https://{self.zone}.nuclia.cloud/api/v1/kb/{kb_id}/ask"
        
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
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    text = await response.text()
                    return {
                        'kb_name': kb_name,
                        'success': True,
                        'data': self._parse_ndjson(text)
                    }
                else:
                    return {
                        'kb_name': kb_name,
                        'success': False,
                        'error': f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                'kb_name': kb_name,
                'success': False,
                'error': str(e)
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
                                "title": resource["title"],
                                "id": resource_id
                            })
                except json.JSONDecodeError:
                    continue
        
        return {
            "answer": answer_text.strip(),
            "sources": sources
        }
    
    def _aggregate_results(self, results: List[Dict], query: str, 
                          user_context: Dict) -> Dict:
        """Aggregate and rank results from multiple knowledge boxes"""
        
        aggregated = {
            'query': query,
            'user': user_context.get('name', 'Unknown'),
            'role': user_context.get('role', 'employee'),
            'timestamp': datetime.now().isoformat(),
            'results': [],
            'summary': "",
            'total_sources': 0
        }
        
        # Collect successful results
        for result in results:
            if isinstance(result, dict) and result.get('success'):
                aggregated['results'].append({
                    'kb': result['kb_name'],
                    'answer': result['data']['answer'],
                    'sources': result['data']['sources']
                })
                aggregated['total_sources'] += len(result['data']['sources'])
        
        # Generate executive summary if multiple results
        if len(aggregated['results']) > 1:
            aggregated['summary'] = self._generate_executive_summary(aggregated['results'])
        elif len(aggregated['results']) == 1:
            aggregated['summary'] = aggregated['results'][0]['answer']
        else:
            aggregated['summary'] = "No results found for your query."
        
        return aggregated
    
    def _generate_executive_summary(self, results: List[Dict]) -> str:
        """Combine insights from multiple knowledge boxes into executive summary"""
        
        summary_parts = []
        
        for result in results:
            kb_name = result['kb']
            answer_preview = result['answer'][:200] if result['answer'] else "No data"
            
            if kb_name == 'global_research':
                summary_parts.append(f"Market Research: {answer_preview}")
            elif 'compliance' in kb_name:
                summary_parts.append(f"Compliance Note: {answer_preview}")
            elif kb_name == 'client_analytics':
                summary_parts.append(f"Client Insights: {answer_preview}")
        
        return " | ".join(summary_parts)
    
    def _mock_federated_response(self, query: str, accessible_kbs: List[str]) -> Dict:
        """Generate mock response for demo when actual KBs aren't available"""
        
        return {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'results': [
                {
                    'kb': kb,
                    'answer': f"Mock response from {kb}: Analysis shows positive trends in {query}",
                    'sources': [{'title': f'Document from {kb}', 'id': f'mock_{kb}_001'}]
                }
                for kb in accessible_kbs
            ],
            'summary': f"Federated search across {len(accessible_kbs)} knowledge boxes completed",
            'total_sources': len(accessible_kbs)
        }


# Example usage
async def main():
    manager = EnterpriseKnowledgeManager()
    
    # Sarah Rodriguez (US Compliance Officer) query
    sarah_context = {
        'name': 'Sarah Rodriguez',
        'role': 'compliance_us',
        'region': 'US',
        'department': 'Legal & Compliance'
    }
    
    print("DataVault Enterprise Knowledge System")
    print("=" * 50)
    print(f"User: {sarah_context['name']}")
    print(f"Role: {sarah_context['role']}")
    print(f"Region: {sarah_context['region']}")
    print("-" * 50)
    
    # Critical compliance query
    query = "What are the latest regulatory requirements for investment advisors?"
    print(f"\nQuery: {query}")
    print("-" * 50)
    
    result = await manager.federated_search(query, sarah_context)
    
    print(f"\n✅ Searched {len(result['results'])} knowledge boxes")
    print(f"📚 Total sources analyzed: {result['total_sources']}")
    print(f"\n📋 Executive Summary:")
    print(result['summary'][:500])
    
    if result['results']:
        print(f"\n🔍 Detailed Results by Knowledge Box:")
        for kb_result in result['results']:
            print(f"\n  • {kb_result['kb'].upper()}:")
            print(f"    {kb_result['answer'][:200]}...")
            print(f"    Sources: {len(kb_result['sources'])}")


if __name__ == "__main__":
    asyncio.run(main())