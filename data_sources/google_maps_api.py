import requests
import os
from typing import Dict, Any, Optional, List

class GoogleMapsAPI:
    """
    Google Maps API integration for geocoding and place data
    Get free API key at: https://developers.google.com/maps/documentation/places/web-service/get-api-key
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """Geocode an address and get detailed location information"""
        try:
            if not self.api_key:
                return self._get_mock_geocoding(address)
            
            # Geocoding API request
            geocode_url = f"{self.base_url}/geocode/json"
            params = {
                "address": address,
                "key": self.api_key
            }
            
            response = requests.get(geocode_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data["status"] == "OK" and data["results"]:
                    result = data["results"][0]
                    
                    # Extract location details
                    location = result["geometry"]["location"]
                    components = result["address_components"]
                    
                    # Parse address components
                    parsed_address = self._parse_address_components(components)
                    
                    return {
                        "address": result["formatted_address"],
                        "coordinates": {
                            "latitude": location["lat"],
                            "longitude": location["lng"]
                        },
                        "address_components": parsed_address,
                        "place_id": result["place_id"],
                        "location_type": result["geometry"]["location_type"],
                        "data_source": "Google Maps API"
                    }
            
            return self._get_mock_geocoding(address)
            
        except Exception as e:
            print(f"Google Maps API error: {str(e)}")
            return self._get_mock_geocoding(address)
    
    def get_nearby_places(self, lat: float, lon: float, place_type: str = "establishment", radius: int = 1000) -> List[Dict[str, Any]]:
        """Get nearby places of a specific type"""
        try:
            if not self.api_key:
                return self._get_mock_places(place_type)
            
            # Places Nearby Search API
            places_url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lon}",
                "radius": radius,
                "type": place_type,
                "key": self.api_key
            }
            
            response = requests.get(places_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                places = []
                for place in data.get("results", [])[:10]:  # Limit to 10 results
                    places.append({
                        "name": place.get("name", "Unknown"),
                        "rating": place.get("rating", 0),
                        "price_level": place.get("price_level", 0),
                        "types": place.get("types", []),
                        "vicinity": place.get("vicinity", ""),
                        "place_id": place.get("place_id", "")
                    })
                
                return places
            
            return self._get_mock_places(place_type)
            
        except Exception as e:
            print(f"Google Places API error: {str(e)}")
            return self._get_mock_places(place_type)
    
    def get_area_insights(self, address: str) -> Dict[str, Any]:
        """Get comprehensive area insights combining geocoding and places"""
        geocode_result = self.geocode_address(address)
        
        if geocode_result.get("coordinates"):
            lat = geocode_result["coordinates"]["latitude"]
            lon = geocode_result["coordinates"]["longitude"]
            
            # Get various types of nearby places
            restaurants = self.get_nearby_places(lat, lon, "restaurant", 1000)
            schools = self.get_nearby_places(lat, lon, "school", 2000)
            hospitals = self.get_nearby_places(lat, lon, "hospital", 5000)
            shopping = self.get_nearby_places(lat, lon, "shopping_mall", 2000)
            
            return {
                "location_info": geocode_result,
                "nearby_amenities": {
                    "restaurants": len(restaurants),
                    "schools": len(schools),
                    "hospitals": len(hospitals),
                    "shopping_centers": len(shopping)
                },
                "top_restaurants": restaurants[:3],
                "top_schools": schools[:3],
                "area_score": self._calculate_area_score(restaurants, schools, hospitals, shopping),
                "data_source": "Google Maps API"
            }
        
        return {"error": "Could not geocode address"}
    
    def _parse_address_components(self, components: List[Dict]) -> Dict[str, str]:
        """Parse Google Maps address components"""
        parsed = {}
        
        for component in components:
            types = component["types"]
            value = component["long_name"]
            
            if "street_number" in types:
                parsed["street_number"] = value
            elif "route" in types:
                parsed["street_name"] = value
            elif "locality" in types:
                parsed["city"] = value
            elif "administrative_area_level_1" in types:
                parsed["state"] = value
            elif "postal_code" in types:
                parsed["zip_code"] = value
            elif "country" in types:
                parsed["country"] = value
        
        return parsed
    
    def _calculate_area_score(self, restaurants: List, schools: List, hospitals: List, shopping: List) -> int:
        """Calculate overall area desirability score"""
        score = 0
        
        # Restaurants (max 30 points)
        score += min(len(restaurants) * 3, 30)
        
        # Schools (max 25 points)
        score += min(len(schools) * 5, 25)
        
        # Healthcare (max 20 points)
        score += min(len(hospitals) * 10, 20)
        
        # Shopping (max 25 points)
        score += min(len(shopping) * 5, 25)
        
        return min(score, 100)
    
    def _get_mock_geocoding(self, address: str) -> Dict[str, Any]:
        """Mock geocoding data"""
        return {
            "address": address,
            "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
            "address_components": {
                "street_number": "123",
                "street_name": "Main Street", 
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "United States"
            },
            "place_id": "mock_place_id",
            "location_type": "ROOFTOP",
            "data_source": "Mock Data (Google Maps API key not configured)"
        }
    
    def _get_mock_places(self, place_type: str) -> List[Dict[str, Any]]:
        """Mock places data"""
        return [
            {"name": f"Sample {place_type.title()}", "rating": 4.2, "price_level": 2, "types": [place_type], "vicinity": "Nearby Area"}
        ]
