#!/usr/bin/env python3
"""
Diagnostic script to test address lookup functionality
Run this to troubleshoot "state-related errors" in property analysis
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append('.')

def test_address_lookup(address: str):
    """Test the complete address lookup pipeline"""
    print(f"🔍 TESTING ADDRESS: {address}")
    print("=" * 60)
    
    # Check API keys
    print("1. API KEY STATUS:")
    google_key = os.getenv("GOOGLE_MAPS_API_KEY")
    census_key = os.getenv("CENSUS_API_KEY")
    
    print(f"   Google Maps API: {'✅ SET' if google_key else '❌ NOT SET'}")
    print(f"   Census API: {'✅ SET' if census_key else '❌ NOT SET'}")
    
    if not google_key:
        print("❌ Cannot proceed without Google Maps API key")
        print("   Please create a .env file with GOOGLE_MAPS_API_KEY")
        return False
    
    try:
        # Test Google Maps geocoding
        print("\n2. GOOGLE MAPS GEOCODING:")
        from data_sources.google_maps_api import GoogleMapsAPI
        
        google_maps = GoogleMapsAPI()
        geocode_result = google_maps.geocode_address(address)
        
        print(f"   ✅ Geocoding successful")
        print(f"   📍 Coordinates: {geocode_result.get('coordinates')}")
        print(f"   🏠 Formatted Address: {geocode_result.get('address')}")
        print(f"   🗺️ Address Components: {geocode_result.get('address_components')}")
        
        # Test state extraction
        print("\n3. STATE/COUNTY EXTRACTION:")
        components = geocode_result.get('address_components', {})
        state = components.get('state', '')
        county = components.get('county', '')
        
        print(f"   🏛️ State: '{state}'")
        print(f"   🏘️ County: '{county}'")
        
        # Test Census API if available
        if census_key:
            print("\n4. CENSUS API PROCESSING:")
            from data_sources.census_api import CensusAPI
            
            census = CensusAPI()
            
            # Test state code conversion
            state_code = census.get_state_code(state) if state else ""
            print(f"   🔢 State Code: '{state_code}'")
            
            if state_code:
                # Test county FIPS lookup
                if county:
                    county_fips = census.lookup_county_fips(state_code, county)
                    print(f"   📊 County FIPS: '{county_fips}'")
                
                # Test demographics retrieval
                try:
                    demographics = census.get_location_demographics(address, state_code, geocode_result)
                    print(f"   ✅ Demographics retrieved successfully")
                    print(f"   👥 Population: {demographics.get('population', 'N/A')}")
                    print(f"   💰 Median Income: ${demographics.get('median_income', 0):,}")
                    print(f"   🏡 Median Home Value: ${demographics.get('median_home_value', 0):,}")
                except Exception as demo_error:
                    print(f"   ❌ Demographics failed: {demo_error}")
            else:
                print(f"   ❌ Invalid state code for '{state}'")
        else:
            print("\n4. CENSUS API: ❌ NO API KEY")
            print("   Please add CENSUS_API_KEY to your .env file")
        
        # Test Property Research Tool
        print("\n5. PROPERTY RESEARCH TOOL:")
        from agents.crew_setup import PropertyResearchTool
        
        tool = PropertyResearchTool()
        result = tool._run(address)
        
        if "❌" in result:
            print(f"   ❌ Tool failed with error")
            print(f"   Error details: {result[:200]}...")
        else:
            print(f"   ✅ Tool succeeded")
            print(f"   Report length: {len(result)} characters")
        
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏠 Property Intelligence Platform - Address Lookup Diagnostic Tool")
    print("=" * 70)
    
    # Test the specific problematic address first
    test_addresses = [
        "3650 Dunigan Ct, Catharpin, VA 20143",  # The problematic address
        "1600 Pennsylvania Avenue, Washington, DC",  # Test case
        "Times Square, New York, NY"  # Another test case
    ]
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n\n🧪 TEST {i}/3")
        success = test_address_lookup(address)
        print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print("=" * 60)
    
    print(f"\n\n💡 TROUBLESHOOTING TIPS:")
    print("1. Ensure .env file exists with API keys")
    print("2. Check ADDRESS_LOOKUP_TROUBLESHOOTING.md for detailed guidance")
    print("3. Verify your Google Maps and Census API keys are valid")
    print("4. The system should now handle state/county extraction robustly") 