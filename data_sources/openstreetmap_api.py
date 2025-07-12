import requests
from typing import Dict, Any, List, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

class OpenStreetMapAPI:
    """
    OpenStreetMap API integration for geospatial data and amenities
    Free API - no key required
    """
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="property-intelligence-ai")
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
    def get_location_intelligence(self, address: str) -> Dict[str, Any]:
        """Get comprehensive location intelligence"""
        try:
            # Geocode the address
            location = self.geocoder.geocode(address, timeout=10)
            
            if not location:
                return self._get_mock_location_data(address)
            
            lat, lon = location.latitude, location.longitude
            
            # Get nearby amenities
            amenities = self._get_nearby_amenities(lat, lon)
            
            # Calculate scores
            walkability_score = self._calculate_walkability_score(amenities)
            transit_score = self._calculate_transit_score(amenities)
            lifestyle_score = self._calculate_lifestyle_score(amenities)
            
            return {
                "address": address,
                "coordinates": {"latitude": lat, "longitude": lon},
                "amenities": amenities,
                "scores": {
                    "walkability": walkability_score,
                    "transit_access": transit_score,
                    "lifestyle": lifestyle_score,
                    "overall_location": round((walkability_score + transit_score + lifestyle_score) / 3, 1)
                },
                "location_highlights": self._get_location_highlights(amenities),
                "data_source": "OpenStreetMap"
            }
            
        except Exception as e:
            print(f"OpenStreetMap API error: {str(e)}")
            return self._get_mock_location_data(address)
    
    def _get_nearby_amenities(self, lat: float, lon: float, radius_km: float = 1.0) -> Dict[str, List[Dict]]:
        """Get nearby amenities using Overpass API"""
        try:
            # Overpass query for various amenities within radius
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["amenity"~"^(restaurant|cafe|bar|fast_food|school|university|hospital|clinic|pharmacy|bank|atm|supermarket|convenience|shopping_mall|park|library|gym|fuel)$"](around:{radius_km * 1000},{lat},{lon});
              node["public_transport"~"^(platform|station|stop_position)$"](around:{radius_km * 1000},{lat},{lon});
              node["shop"~"^(supermarket|convenience|mall|department_store)$"](around:{radius_km * 1000},{lat},{lon});
              node["leisure"~"^(park|playground|sports_centre|fitness_centre|swimming_pool)$"](around:{radius_km * 1000},{lat},{lon});
            );
            out geom;
            """
            
            response = requests.post(
                self.overpass_url,
                data=overpass_query,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Categorize amenities
                categorized = {
                    "restaurants": [],
                    "schools": [],
                    "healthcare": [],
                    "shopping": [],
                    "transit": [],
                    "recreation": [],
                    "services": []
                }
                
                for element in data.get("elements", []):
                    tags = element.get("tags", {})
                    amenity = tags.get("amenity", "")
                    shop = tags.get("shop", "")
                    leisure = tags.get("leisure", "")
                    public_transport = tags.get("public_transport", "")
                    
                    name = tags.get("name", "Unnamed")
                    lat_item = element.get("lat", 0)
                    lon_item = element.get("lon", 0)
                    
                    # Categorize based on tags
                    if amenity in ["restaurant", "cafe", "bar", "fast_food"]:
                        categorized["restaurants"].append({"name": name, "type": amenity, "lat": lat_item, "lon": lon_item})
                    elif amenity in ["school", "university"]:
                        categorized["schools"].append({"name": name, "type": amenity, "lat": lat_item, "lon": lon_item})
                    elif amenity in ["hospital", "clinic", "pharmacy"]:
                        categorized["healthcare"].append({"name": name, "type": amenity, "lat": lat_item, "lon": lon_item})
                    elif amenity in ["bank", "atm"] or shop in ["supermarket", "convenience", "mall", "department_store"]:
                        categorized["services"].append({"name": name, "type": amenity or shop, "lat": lat_item, "lon": lon_item})
                    elif public_transport or amenity == "fuel":
                        categorized["transit"].append({"name": name, "type": public_transport or "fuel", "lat": lat_item, "lon": lon_item})
                    elif leisure or amenity == "park":
                        categorized["recreation"].append({"name": name, "type": leisure or "park", "lat": lat_item, "lon": lon_item})
                
                return categorized
                
            else:
                return self._get_mock_amenities()
                
        except Exception as e:
            print(f"Overpass API error: {str(e)}")
            return self._get_mock_amenities()
    
    def _calculate_walkability_score(self, amenities: Dict[str, List[Dict]]) -> int:
        """Calculate walkability score based on nearby amenities"""
        score = 0
        
        # Restaurants and cafes (max 25 points)
        score += min(len(amenities.get("restaurants", [])) * 3, 25)
        
        # Shopping and services (max 20 points)
        score += min(len(amenities.get("services", [])) * 2, 20)
        
        # Schools (max 15 points)
        score += min(len(amenities.get("schools", [])) * 5, 15)
        
        # Healthcare (max 15 points)
        score += min(len(amenities.get("healthcare", [])) * 5, 15)
        
        # Recreation (max 15 points)
        score += min(len(amenities.get("recreation", [])) * 3, 15)
        
        # Transit (max 10 points)
        score += min(len(amenities.get("transit", [])) * 2, 10)
        
        return min(score, 100)
    
    def _calculate_transit_score(self, amenities: Dict[str, List[Dict]]) -> int:
        """Calculate transit accessibility score"""
        transit_count = len(amenities.get("transit", []))
        
        if transit_count >= 5:
            return 90
        elif transit_count >= 3:
            return 75
        elif transit_count >= 1:
            return 60
        else:
            return 30
    
    def _calculate_lifestyle_score(self, amenities: Dict[str, List[Dict]]) -> int:
        """Calculate lifestyle quality score"""
        restaurants = len(amenities.get("restaurants", []))
        recreation = len(amenities.get("recreation", []))
        services = len(amenities.get("services", []))
        
        # Balanced lifestyle score
        variety_score = min((restaurants + recreation + services) * 2, 60)
        convenience_score = min(services * 5, 40)
        
        return min(variety_score + convenience_score, 100)
    
    def _get_location_highlights(self, amenities: Dict[str, List[Dict]]) -> List[str]:
        """Generate location highlights based on amenities"""
        highlights = []
        
        restaurant_count = len(amenities.get("restaurants", []))
        school_count = len(amenities.get("schools", []))
        healthcare_count = len(amenities.get("healthcare", []))
        transit_count = len(amenities.get("transit", []))
        recreation_count = len(amenities.get("recreation", []))
        
        if restaurant_count >= 10:
            highlights.append(f"🍽️ Vibrant dining scene with {restaurant_count}+ restaurants nearby")
        elif restaurant_count >= 5:
            highlights.append(f"🍽️ Good dining options with {restaurant_count} restaurants")
        
        if school_count >= 3:
            highlights.append(f"🏫 Excellent educational access with {school_count} schools")
        elif school_count >= 1:
            highlights.append(f"🏫 Educational facilities available")
        
        if healthcare_count >= 2:
            highlights.append(f"🏥 Good healthcare access with {healthcare_count} facilities")
        
        if transit_count >= 5:
            highlights.append(f"🚊 Excellent public transportation with {transit_count} stops")
        elif transit_count >= 2:
            highlights.append(f"🚊 Good transit access with {transit_count} stops")
        
        if recreation_count >= 5:
            highlights.append(f"🏞️ Great recreation options with {recreation_count} parks/facilities")
        
        if not highlights:
            highlights.append("🏡 Quiet residential area")
        
        return highlights
    
    def _get_mock_amenities(self) -> Dict[str, List[Dict]]:
        """Mock amenities data for fallback"""
        return {
            "restaurants": [
                {"name": "Local Cafe", "type": "cafe", "lat": 0, "lon": 0},
                {"name": "Pizza Place", "type": "restaurant", "lat": 0, "lon": 0}
            ],
            "schools": [
                {"name": "Elementary School", "type": "school", "lat": 0, "lon": 0}
            ],
            "healthcare": [
                {"name": "Medical Center", "type": "clinic", "lat": 0, "lon": 0}
            ],
            "services": [
                {"name": "Grocery Store", "type": "supermarket", "lat": 0, "lon": 0},
                {"name": "Bank", "type": "bank", "lat": 0, "lon": 0}
            ],
            "transit": [
                {"name": "Bus Stop", "type": "platform", "lat": 0, "lon": 0}
            ],
            "recreation": [
                {"name": "City Park", "type": "park", "lat": 0, "lon": 0}
            ]
        }
    
    def _get_mock_location_data(self, address: str) -> Dict[str, Any]:
        """Mock location data for fallback"""
        return {
            "address": address,
            "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
            "amenities": self._get_mock_amenities(),
            "scores": {
                "walkability": 75,
                "transit_access": 68,
                "lifestyle": 82,
                "overall_location": 75.0
            },
            "location_highlights": [
                "🏡 Established residential neighborhood",
                "🏫 Good school access",
                "🍽️ Variety of dining options nearby"
            ],
            "data_source": "Mock Data (OpenStreetMap unavailable)"
        }
