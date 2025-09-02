# compliance_audit_query.py
# Sarah's urgent compliance audit query implementation
# As shown in Article 2 - The critical 48-hour audit deadline

import os
import sys

# Import the search function that uses Nuclia SDK
from search_financial_insights import search_financial_insights

def run_compliance_audit():
    """
    Sarah Rodriguez's urgent compliance audit query
    This is the actual query that saved DataVault's audit deadline
    """
    
    print("=" * 60)
    print("DATAVAULT FINANCIAL SERVICES - COMPLIANCE AUDIT")
    print("Requested by: Sarah Rodriguez, Head of Compliance")
    print("Deadline: Monday Morning (48 hours)")
    print("=" * 60)
    print()
    
    # Sarah's urgent compliance audit query - exactly as shown in the article
    audit_query = "risk disclosure regulatory updates systemic risk market analysis"
    
    print(f"Executing search: {audit_query}")
    print("-" * 60)
    
    # Run the search using the Nuclia SDK
    results = search_financial_insights(audit_query)
    
    if results:
        # Display categorized results as shown in the article
        print()
        print("🔍 Query: 'risk disclosure regulatory updates systemic risk market analysis'")
        
        total = len(results.get('compliance', [])) + len(results.get('news', [])) + len(results.get('documents', []))
        print(f"📊 Total results: {total}")
        print()
        
        if results.get('compliance'):
            print("📋 Compliance Documents:")
            for doc in results['compliance'][:3]:
                print(f"  • {doc['title']}")
            print()
        
        if results.get('news'):
            print("📰 Recent News:")
            for article in results['news'][:3]:
                print(f"  • {article['title']}")
            print()
        
        if results.get('documents'):
            print("📄 Research Documents:")
            for doc in results['documents'][:3]:
                print(f"  • {doc['title']}")
            print()
        
        print("-" * 60)
        print("✅ AUDIT DOCUMENTATION COMPILED")
        print()
        print("Sarah's comment: 'This would have taken me three days to compile manually.'")
        print("Time saved: ~70 hours")
        print("Audit status: READY FOR SUBMISSION")
    else:
        print()
        print("⚠️  No results returned. Please check:")
        print("  1. API credentials are configured in .env file")
        print("  2. Knowledge Box ID matches your Nuclia setup")
        print("  3. Network connection is available")
    
    return results

def generate_audit_report(results):
    """
    Generate the formatted audit report for regulators
    As Sarah presented to the audit team
    """
    
    if not results:
        return "No data available for report generation"
    
    print()
    print("=" * 60)
    print("GENERATING FORMAL AUDIT REPORT")
    print("=" * 60)
    print()
    
    report = []
    report.append("BASEL III IMPLEMENTATION STATUS - DATAVAULT 2024")
    report.append("-" * 50)
    report.append("")
    report.append("1. REGULATORY COMPLIANCE DOCUMENTATION")
    
    if results.get('compliance'):
        for doc in results['compliance']:
            report.append(f"   - {doc['title']}")
    
    report.append("")
    report.append("2. RECENT REGULATORY UPDATES")
    
    if results.get('news'):
        for article in results['news']:
            report.append(f"   - {article['title']}")
    
    report.append("")
    report.append("3. INTERNAL RISK ASSESSMENTS")
    
    if results.get('documents'):
        for doc in results['documents']:
            report.append(f"   - {doc['title']}")
    
    report.append("")
    report.append("Report Generated: Using Nuclia RAG-as-a-Service Platform")
    report.append("Processing Time: Seconds vs. 2 weeks manual compilation")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("DATAVAULT FINANCIAL SERVICES")
    print("Compliance Audit System - Article 2 Demo")
    print()
    
    # Run Sarah's actual compliance audit query
    results = run_compliance_audit()
    
    # Generate the formal report if we have results
    if results:
        print()
        print("Generating formal audit report...")
        report = generate_audit_report(results)
        print(report)
        
        print()
        print("=" * 60)
        print("The lead auditor leaned forward. 'How did you connect all")
        print("these systems so quickly?'")
        print()
        print("Sarah smiled. 'We built a unified intelligence network using")
        print("RAG-as-a-Service. Every document, every news feed, every")
        print("analysis – it's all connected and searchable in natural language.'")
        print("=" * 60)