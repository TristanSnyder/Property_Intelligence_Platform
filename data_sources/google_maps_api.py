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
                raise ValueError("Google Maps API key is required for real data analysis")
            
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
                        "location_type": result["geometry"].get("location_type", "APPROXIMATE"),
                        "neighborhood": parsed_address.get("neighborhood", parsed_address.get("sublocality", "Urban Area"))
                    }
                else:
                    raise ValueError(f"Google Maps API returned status: {data['status']}")
            else:
                raise ValueError(f"Google Maps API request failed with status {response.status_code}")
                
        except Exception as e:
            raise ValueError(f"Google Maps API error: {str(e)}")

    def get_nearby_places(self, lat: float, lon: float, place_type: str = "establishment", radius: int = 1000) -> List[Dict[str, Any]]:
        """Get nearby places using Google Places API"""
        try:
            if not self.api_key:
                raise ValueError("Google Maps API key is required for real data analysis")
            
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
                return data.get("results", [])[:20]  # Limit to 20 results
            else:
                raise ValueError(f"Google Places API request failed with status {response.status_code}")
                
        except Exception as e:
            raise ValueError(f"Google Places API error: {str(e)}")

    def get_area_insights(self, address: str) -> Dict[str, Any]:
        """Get comprehensive area insights including amenities and scores"""
        try:
            geocode_result = self.geocode_address(address)
            
            if geocode_result.get("coordinates"):
                lat = geocode_result["coordinates"]["latitude"]
                lon = geocode_result["coordinates"]["longitude"]
                
                # Get different types of nearby places
                restaurants = self.get_nearby_places(lat, lon, "restaurant", 800)
                schools = self.get_nearby_places(lat, lon, "school", 1500)
                hospitals = self.get_nearby_places(lat, lon, "hospital", 2000)
                shopping = self.get_nearby_places(lat, lon, "shopping_mall", 1500)
                
                # Calculate area score (FIXED SCALING)
                area_score = self._calculate_area_score(restaurants, schools, hospitals, shopping)
                
                return {
                    "area_score": area_score,  # Now properly scaled 0-10
                    "restaurants": len(restaurants),
                    "schools": len(schools),
                    "hospitals": len(hospitals),
                    "shopping": len(shopping),
                    "nearby_amenities": {
                        "restaurants": len(restaurants),
                        "schools": len(schools),
                        "hospitals": len(hospitals),
                        "shopping_centers": len(shopping)
                    },
                    "amenity_density": "High" if area_score >= 7 else "Moderate" if area_score >= 4 else "Low"
                }
            else:
                raise ValueError("Unable to geocode address for area insights")
                
        except Exception as e:
            raise ValueError(f"Google Maps area insights error: {str(e)}")

    def _parse_address_components(self, components: List[Dict]) -> Dict[str, str]:
        """Parse Google Maps address components"""
        parsed = {
            "street_number": "",
            "route": "",
            "neighborhood": "",
            "sublocality": "",
            "locality": "",
            "administrative_area_level_1": "",
            "administrative_area_level_2": "",
            "country": "",
            "postal_code": ""
        }
        
        for component in components:
            types = component.get("types", [])
            long_name = component.get("long_name", "")
            
            for type_name in types:
                if type_name in parsed:
                    parsed[type_name] = long_name
                    break
        
        # Create simplified mapping
        return {
            "street": f"{parsed['street_number']} {parsed['route']}".strip(),
            "neighborhood": parsed.get("neighborhood") or parsed.get("sublocality") or parsed.get("locality"),
            "city": parsed.get("locality"),
            "state": parsed.get("administrative_area_level_1"),
            "county": parsed.get("administrative_area_level_2"),
            "country": parsed.get("country"),
            "postal_code": parsed.get("postal_code")
        }

    def _calculate_area_score(self, restaurants: List, schools: List, hospitals: List, shopping: List) -> int:
        """Calculate area score based on amenities (FIXED - properly scaled 0-10)"""
        try:
            # Weight different amenities
            restaurant_score = min(len(restaurants) * 0.2, 3.0)  # Max 3 points
            school_score = min(len(schools) * 0.3, 2.5)          # Max 2.5 points
            hospital_score = min(len(hospitals) * 0.4, 2.0)      # Max 2 points
            shopping_score = min(len(shopping) * 0.3, 2.5)       # Max 2.5 points
            
            total_score = restaurant_score + school_score + hospital_score + shopping_score
            
            # Scale to 0-10 and round
            final_score = min(round(total_score), 10)
            
            return max(final_score, 1)  # Minimum score of 1
            
        except Exception:
            return 6  # Default moderate score


