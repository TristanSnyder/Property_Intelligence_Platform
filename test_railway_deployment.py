#!/usr/bin/env python3
"""
Railway Deployment Test Script
Test if the PropertyResearchTool works correctly on Railway with environment variables
"""

import os
import requests
import json
from datetime import datetime

def test_railway_deployment(base_url: str):
    """Test the Railway deployment endpoints"""
    
    print("🚀 TESTING RAILWAY DEPLOYMENT")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test 1: Health Check
    print("1. HEALTH CHECK:")
    try:
        response = requests.get(f"{base_url}/health", timeout=30)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   API Keys: {health_data.get('api_keys')}")
            print(f"   Connectivity: {health_data.get('api_connectivity')}")
            
            if health_data.get('warnings'):
                print(f"   ⚠️ Warnings: {health_data['warnings']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Debug Address Lookup
    print("\n2. DEBUG ADDRESS LOOKUP:")
    test_address = "3650 Dunigan Ct, Catharpin, VA 20143"
    try:
        response = requests.get(
            f"{base_url}/debug-address",
            params={"address": test_address},
            timeout=60
        )
        
        if response.status_code == 200:
            debug_data = response.json()
            print(f"   Address: {debug_data.get('address')}")
            print(f"   Overall Status: {debug_data.get('overall_status')}")
            
            for step in debug_data.get('steps', []):
                print(f"   Step {step['step']}: {step['name']} - {step.get('status', 'unknown')}")
                if 'error' in step:
                    print(f"      ❌ Error: {step['error']}")
                    
        else:
            print(f"   ❌ Debug endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Debug endpoint error: {e}")
    
    # Test 3: Full Property Analysis
    print("\n3. FULL PROPERTY ANALYSIS:")
    try:
        response = requests.post(
            f"{base_url}/analyze-property",
            json={
                "address": test_address,
                "analysis_type": "comprehensive"
            },
            timeout=120
        )
        
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"   ✅ Analysis started: {analysis_data.get('analysis_id')}")
            print(f"   Status: {analysis_data.get('status')}")
            
            # Check if we get immediate results
            if analysis_data.get('result'):
                result = analysis_data['result']
                print(f"   Estimated Value: {result.get('estimated_value', 'N/A')}")
                print(f"   Market Trend: {result.get('market_trend', 'N/A')}")
                print(f"   Risk Score: {result.get('risk_score', 'N/A')}")
                
                # Check data sources
                data_sources = result.get('data_sources', [])
                print(f"   Data Sources: {', '.join(data_sources) if data_sources else 'None listed'}")
                
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")
    
    print("\n" + "=" * 50)
    return True

def main():
    # You can customize this URL to match your Railway deployment
    railway_url = input("Enter your Railway app URL (e.g., https://your-app-name.railway.app): ").strip()
    
    if not railway_url:
        print("❌ No URL provided")
        return
    
    if not railway_url.startswith(('http://', 'https://')):
        railway_url = f"https://{railway_url}"
    
    # Remove trailing slash
    railway_url = railway_url.rstrip('/')
    
    test_railway_deployment(railway_url)
    
    print("\n💡 TROUBLESHOOTING TIPS:")
    print("1. Ensure GOOGLE_MAPS_API_KEY and CENSUS_API_KEY are set in Railway environment variables")
    print("2. Check Railway logs for any startup errors")
    print("3. Verify API keys are valid and have proper permissions")
    print("4. Test the /health endpoint directly in your browser")

if __name__ == "__main__":
    main() 