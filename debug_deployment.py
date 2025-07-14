#!/usr/bin/env python3
"""
Debug script to test Census API connectivity in Railway deployment
"""

import os
import requests
import sys

def test_api_keys():
    """Test if API keys are available"""
    print("🔍 Testing API Key Availability...")
    
    google_key = os.getenv("GOOGLE_MAPS_API_KEY")
    census_key = os.getenv("CENSUS_API_KEY")
    
    print(f"📋 Google Maps API Key: {'✅ Present' if google_key else '❌ Missing'}")
    print(f"📋 Census API Key: {'✅ Present' if census_key else '❌ Missing'}")
    
    if not census_key:
        print("\n🚨 CRITICAL: Census API key is missing!")
        print("💡 This explains why the demographics lookup is hanging.")
        print("📝 Action needed: Add CENSUS_API_KEY to Railway environment variables")
        return False
    
    return True

def test_census_api():
    """Test Census API connectivity"""
    print("\n🧪 Testing Census API Connectivity...")
    
    census_key = os.getenv("CENSUS_API_KEY")
    if not census_key:
        print("❌ Cannot test - Census API key missing")
        return False
    
    try:
        # Test with Virginia state data (state code 51)
        test_url = "https://api.census.gov/data/2022/acs/acs5"
        params = {
            "get": "B01003_001E",  # Total population
            "for": "state:51",     # Virginia
            "key": census_key
        }
        
        print(f"🌐 Testing Census API request...")
        response = requests.get(test_url, params=params, timeout=10)
        
        print(f"📊 Census API Response: Status {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Census API working! Got {len(data)} rows")
            return True
        else:
            print(f"❌ Census API failed: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Census API test failed: {e}")
        return False

def main():
    print("🚀 Railway Deployment Debug Tool")
    print("=" * 50)
    
    # Test API keys
    keys_ok = test_api_keys()
    
    # Test Census API if key exists
    if keys_ok:
        api_ok = test_census_api()
        
        if api_ok:
            print("\n✅ All tests passed!")
            print("💭 Issue might be:")
            print("   - County lookup hanging")
            print("   - Address parsing issue")
            print("   - Timeout in property research tool")
        else:
            print("\n❌ Census API connectivity failed")
    else:
        print("\n🚨 Missing API keys - this is likely the main issue!")
        print("\n📋 Required Railway Environment Variables:")
        print("   - GOOGLE_MAPS_API_KEY")
        print("   - CENSUS_API_KEY") 
        print("   - OPENAI_API_KEY")

if __name__ == "__main__":
    main() 