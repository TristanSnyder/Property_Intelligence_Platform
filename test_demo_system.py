#!/usr/bin/env python3
"""
Test script for the Demo Property Intelligence System
"""

from demo_data_service import DemoDataService

def test_demo_system():
    """Test the complete demo system with various addresses"""
    
    print("🧪 Testing Demo Property Intelligence System")
    print("=" * 60)
    
    # Initialize demo service
    demo_service = DemoDataService()
    
    # Test addresses for different categories
    test_addresses = [
        "3650 Dunigan Ct, Catharpin, VA 20143",  # Virginia suburban
        "123 Main Street, Manhattan, NY 10001",  # Luxury metro
        "456 Oak Avenue, Beverly Hills, CA 90210",  # Luxury metro
        "789 Park Drive, Suburbs, TX 75001",  # Standard suburban
        "321 Downtown Plaza, Metro City, IL 60601"  # Urban center
    ]
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n🏠 TEST {i}: {address}")
        print("-" * 50)
        
        try:
            # Get comprehensive data
            data = demo_service.get_comprehensive_property_data(address)
            
            print(f"📍 Category: {data['category']}")
            print(f"🏠 Property Type: {data['property_data']['property_type']}")
            print(f"💰 Median Home Value: ${data['demographics']['median_home_value']:,}")
            print(f"🎯 Investment Grade: {data['market_analysis']['investment_grade']}")
            
            # Test formatted outputs
            analysis = demo_service.get_formatted_analysis(address)
            
            print(f"\n✅ Property Research: {len(analysis['property_research'])} characters")
            print(f"✅ Market Analysis: {len(analysis['market_analysis'])} characters")
            print(f"✅ Risk Assessment: {len(analysis['risk_assessment'])} characters")
            
        except Exception as e:
            print(f"❌ Error testing {address}: {e}")
    
    print(f"\n🎉 Demo system test completed!")

def test_specific_address():
    """Test the Virginia address specifically"""
    print("\n" + "="*60)
    print("🎯 TESTING VIRGINIA ADDRESS SPECIFICALLY")
    print("="*60)
    
    demo_service = DemoDataService()
    address = "3650 Dunigan Ct, Catharpin, VA 20143"
    
    analysis = demo_service.get_formatted_analysis(address)
    
    print("\n🏠 PROPERTY RESEARCH OUTPUT:")
    print(analysis["property_research"])
    
    print("\n📈 MARKET ANALYSIS OUTPUT:")
    print(analysis["market_analysis"])
    
    print("\n⚖️ RISK ASSESSMENT OUTPUT:")
    print(analysis["risk_assessment"])

if __name__ == "__main__":
    test_demo_system()
    test_specific_address() 