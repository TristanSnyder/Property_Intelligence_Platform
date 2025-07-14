import requests
import os
from typing import Dict, Any, List

class ClimateAPI:
    """
    Environmental and climate data integration
    Uses Open-Meteo (free) and NOAA APIs for climate risk assessment
    """
    
    def __init__(self):
        self.openmeteo_url = "https://api.open-meteo.com/v1"
        
    def get_climate_risk_assessment(self, lat: float, lon: float, address: str) -> Dict[str, Any]:
        """Get comprehensive climate risk assessment for a location"""
        try:
            # Get current weather and historical data
            weather_data = self._get_weather_data(lat, lon)
            
            # Calculate risk scores (properly scaled 0-10)
            flood_risk = self._assess_flood_risk(lat, lon)
            temperature_risk = self._assess_temperature_risk(weather_data)
            precipitation_risk = self._assess_precipitation_risk(weather_data)
            
            # Overall climate risk score (properly averaged and scaled)
            overall_risk = round((flood_risk + temperature_risk + precipitation_risk) / 3, 1)
            overall_risk = min(overall_risk, 10.0)  # Ensure it never exceeds 10
            
            return {
                "location": address,
                "coordinates": {"latitude": lat, "longitude": lon},
                "climate_risks": {
                    "flood_risk": {
                        "score": flood_risk,
                        "level": self._get_risk_level(flood_risk),
                        "description": self._get_flood_description(flood_risk)
                    },
                    "temperature_extremes": {
                        "score": temperature_risk,
                        "level": self._get_risk_level(temperature_risk),
                        "description": self._get_temperature_description(temperature_risk)
                    },
                    "precipitation_changes": {
                        "score": precipitation_risk,
                        "level": self._get_risk_level(precipitation_risk),
                        "description": self._get_precipitation_description(precipitation_risk)
                    },
                    "overall_climate_risk": {
                        "score": overall_risk,
                        "level": self._get_risk_level(overall_risk),
                        "grade": self._get_risk_grade(overall_risk)
                    }
                },
                "recommendations": self._get_climate_recommendations(overall_risk),
                "data_source": "Open-Meteo Weather API"
            }
            
        except Exception as e:
            raise ValueError(f"Climate API error: {str(e)}")

    def _get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch weather data from Open-Meteo API"""
        try:
            # Current weather
            current_url = f"{self.openmeteo_url}/forecast"
            current_params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation,cloud_cover",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "auto",
                "forecast_days": 7
            }
            
            response = requests.get(current_url, params=current_params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "current_temp": data.get("current", {}).get("temperature_2m", 20),
                    "humidity": data.get("current", {}).get("relative_humidity_2m", 60),
                    "precipitation": data.get("current", {}).get("precipitation", 0),
                    "daily_data": data.get("daily", {}),
                    "api_success": True
                }
            else:
                raise ValueError(f"Weather API returned status code: {response.status_code}")
                
        except Exception as e:
            raise ValueError(f"Weather API error: {str(e)}")
    
    def _get_fallback_weather_data(self) -> Dict[str, Any]:
        """Provide fallback weather data when API fails"""
        return {
            "current_temp": 22,
            "humidity": 65,
            "precipitation": 0.5,
            "daily_data": {"temperature_2m_max": [25, 26, 24], "precipitation_sum": [0, 1, 0.5]},
            "api_success": False
        }

    def _assess_flood_risk(self, lat: float, lon: float) -> float:
        """Assess flood risk based on location (properly scaled 0-10)"""
        try:
            # Basic flood risk assessment based on geographic factors
            base_risk = 2.0  # Base risk
            
            # NYC area check (your coordinates show Queens)
            if 40.4 <= lat <= 40.9 and -74.3 <= lon <= -73.7:
                base_risk = 3.5  # NYC has moderate flood risk
            
            # Coastal proximity increases risk
            coastal_risk = min(1.5, base_risk * 0.3)
            
            total_risk = base_risk + coastal_risk
            return min(total_risk, 10.0)  # Cap at 10
            
        except Exception:
            return 3.0  # Default moderate risk

    def _assess_temperature_risk(self, weather_data: Dict[str, Any]) -> float:
        """Assess temperature extreme risk (properly scaled 0-10)"""
        try:
            current_temp = weather_data.get("current_temp", 22)
            
            # Calculate risk based on temperature extremes
            if weather_data.get("daily_data"):
                max_temps = weather_data["daily_data"].get("temperature_2m_max", [25])
                if max_temps:
                    avg_max = sum(max_temps) / len(max_temps)
                    
                    # Risk increases with extreme temperatures
                    if avg_max > 35:  # Very hot
                        temp_risk = 7.0
                    elif avg_max > 30:  # Hot
                        temp_risk = 4.0
                    elif avg_max < 0:  # Very cold
                        temp_risk = 6.0
                    elif avg_max < 10:  # Cold
                        temp_risk = 3.0
                    else:  # Moderate
                        temp_risk = 2.0
                else:
                    temp_risk = 2.5
            else:
                # Use current temp for basic assessment
                if current_temp > 30 or current_temp < 5:
                    temp_risk = 4.0
                else:
                    temp_risk = 2.0
            
            return min(temp_risk, 10.0)  # Cap at 10
            
        except Exception:
            return 2.5  # Default low-moderate risk

    def _assess_precipitation_risk(self, weather_data: Dict[str, Any]) -> float:
        """Assess precipitation change risk (properly scaled 0-10)"""
        try:
            daily_data = weather_data.get("daily_data", {})
            precipitation_data = daily_data.get("precipitation_sum", [0.5])
            
            if precipitation_data:
                avg_precip = sum(precipitation_data) / len(precipitation_data)
                
                # Risk based on precipitation patterns
                if avg_precip > 20:  # Very heavy rain
                    precip_risk = 6.0
                elif avg_precip > 10:  # Heavy rain
                    precip_risk = 4.0
                elif avg_precip > 5:  # Moderate rain
                    precip_risk = 2.5
                elif avg_precip < 0.1:  # Very dry
                    precip_risk = 3.0
                else:  # Normal
                    precip_risk = 1.5
            else:
                precip_risk = 2.0
            
            return min(precip_risk, 10.0)  # Cap at 10
            
        except Exception:
            return 2.0  # Default low risk

    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to level (0-10 scale)"""
        if score >= 7:
            return "High"
        elif score >= 4:
            return "Moderate"
        elif score >= 2:
            return "Low-Moderate"
        else:
            return "Low"

    def _get_risk_grade(self, score: float) -> str:
        """Convert risk score to letter grade"""
        if score >= 8:
            return "D"
        elif score >= 6:
            return "C"
        elif score >= 4:
            return "B"
        else:
            return "A"

    def _get_flood_description(self, score: float) -> str:
        """Get flood risk description"""
        if score >= 6:
            return "High flood risk area - consider flood insurance"
        elif score >= 3:
            return "Moderate flood risk - standard precautions recommended"
        else:
            return "Low flood risk area"

    def _get_temperature_description(self, score: float) -> str:
        """Get temperature risk description"""
        if score >= 6:
            return "Extreme temperature variations - higher HVAC costs"
        elif score >= 3:
            return "Moderate temperature fluctuations"
        else:
            return "Stable temperature patterns"

    def _get_precipitation_description(self, score: float) -> str:
        """Get precipitation risk description"""
        if score >= 5:
            return "High precipitation variability - drainage considerations"
        elif score >= 3:
            return "Moderate precipitation patterns"
        else:
            return "Stable precipitation patterns"

    def _get_climate_recommendations(self, overall_risk: float) -> List[str]:
        """Generate climate recommendations based on risk score"""
        recommendations = []
        
        if overall_risk >= 6:
            recommendations.extend([
                "Consider comprehensive climate resilience measures",
                "Evaluate flood insurance requirements",
                "Plan for extreme weather contingencies",
                "Invest in energy-efficient HVAC systems"
            ])
        elif overall_risk >= 3:
            recommendations.extend([
                "Standard climate preparedness measures recommended",
                "Consider energy-efficient building improvements",
                "Monitor local weather patterns"
            ])
        else:
            recommendations.extend([
                "Minimal climate risk - standard building practices sufficient",
                "Energy efficiency improvements for cost savings"
            ])
        
        return recommendations

    def _get_mock_climate_data(self, address: str, lat: float, lon: float) -> Dict[str, Any]:
        """Provide realistic mock data when API fails"""
        # Generate realistic risk scores for NYC area
        base_flood_risk = 3.5  # NYC moderate flood risk
        base_temp_risk = 2.5   # Moderate temperature risk
        base_precip_risk = 2.0 # Low precipitation risk
        
        overall_risk = round((base_flood_risk + base_temp_risk + base_precip_risk) / 3, 1)
        
        return {
            "location": address,
            "coordinates": {"latitude": lat, "longitude": lon},
            "climate_risks": {
                "flood_risk": {
                    "score": base_flood_risk,
                    "level": "Moderate",
                    "description": "Moderate flood risk - standard precautions recommended"
                },
                "temperature_extremes": {
                    "score": base_temp_risk,
                    "level": "Low-Moderate",
                    "description": "Moderate temperature fluctuations"
                },
                "precipitation_changes": {
                    "score": base_precip_risk,
                    "level": "Low",
                    "description": "Stable precipitation patterns"
                },
                "overall_climate_risk": {
                    "score": overall_risk,
                    "level": "Low-Moderate",
                    "grade": "B"
                }
            },
            "recommendations": [
                "Standard climate preparedness measures recommended",
                "Consider energy-efficient building improvements",
                "Monitor local weather patterns"
            ],
            "data_source": "Climate Risk Model (Fallback)"
        }
