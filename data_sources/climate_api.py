import requests
import os
from typing import Dict, Any

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
            
            # Calculate risk scores
            flood_risk = self._assess_flood_risk(lat, lon)
            temperature_risk = self._assess_temperature_risk(weather_data)
            precipitation_risk = self._assess_precipitation_risk(weather_data)
            
            # Overall climate risk score
            overall_risk = round((flood_risk + temperature_risk + precipitation_risk) / 3, 1)
            
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
                "current_conditions": weather_data,
                "recommendations": self._get_climate_recommendations(overall_risk),
                "data_source": "Open-Meteo API"
            }
            
        except Exception as e:
            print(f"Climate API error: {str(e)}")
            return self._get_mock_climate_data(address, lat, lon)
    
    def _get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather and recent historical data"""
        try:
            # Current weather
            current_url = f"{self.openmeteo_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "forecast_days": 7
            }
            
            response = requests.get(current_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                daily = data.get("daily", {})
                
                return {
                    "current_temperature": current.get("temperature_2m", 0),
                    "humidity": current.get("relative_humidity_2m", 0),
                    "precipitation": current.get("precipitation", 0),
                    "avg_high_temp": sum(daily.get("temperature_2m_max", [])) / len(daily.get("temperature_2m_max", [1])),
                    "avg_low_temp": sum(daily.get("temperature_2m_min", [])) / len(daily.get("temperature_2m_min", [1])),
                    "total_precipitation": sum(daily.get("precipitation_sum", []))
                }
            
            return {"error": "Could not fetch weather data"}
            
        except:
            return {"error": "Weather API unavailable"}
    
    def _assess_flood_risk(self, lat: float, lon: float) -> float:
        """Assess flood risk based on location (simplified)"""
        # Simplified flood risk assessment
        # In production, would use FEMA flood maps or similar
        
        # Mock assessment based on coastal proximity and elevation
        # This is a placeholder - real implementation would use USGS/FEMA data
        
        if lat < 30 and lat > 25:  # Florida area - higher flood risk
            return 45.0
        elif abs(lat - 40.7) < 2 and abs(lon + 74) < 2:  # NYC area - moderate flood risk
            return 35.0
        elif lat > 45:  # Northern areas - lower flood risk
            return 15.0
        else:
            return 25.0  # Average flood risk
    
    def _assess_temperature_risk(self, weather_data: Dict[str, Any]) -> float:
        """Assess temperature extreme risk"""
        if "error" in weather_data:
            return 25.0
        
        avg_high = weather_data.get("avg_high_temp", 75)
        avg_low = weather_data.get("avg_low_temp", 45)
        
        # Risk increases with extreme temperatures
        risk = 0
        if avg_high > 95 or avg_high < 32:
            risk += 30
        elif avg_high > 85 or avg_high < 40:
            risk += 15
        
        if avg_low < 10 or avg_low > 80:
            risk += 20
        elif avg_low < 25 or avg_low > 75:
            risk += 10
        
        return min(risk, 100)
    
    def _assess_precipitation_risk(self, weather_data: Dict[str, Any]) -> float:
        """Assess precipitation-related risk"""
        if "error" in weather_data:
            return 20.0
        
        total_precip = weather_data.get("total_precipitation", 0)
        
        # Risk based on extreme precipitation patterns
        if total_precip > 50:  # Very high precipitation
            return 40.0
        elif total_precip > 30:  # High precipitation
            return 25.0
        elif total_precip < 2:  # Very low precipitation (drought risk)
            return 35.0
        else:
            return 15.0  # Normal precipitation
    
    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to level"""
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Moderate"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _get_risk_grade(self, score: float) -> str:
        """Convert risk score to letter grade"""
        if score >= 80:
            return "D"
        elif score >= 60:
            return "C"
        elif score >= 40:
            return "B"
        else:
            return "A"
    
    def _get_flood_description(self, score: float) -> str:
        """Get flood risk description"""
        if score >= 50:
            return "High flood risk area. Consider flood insurance and elevation."
        elif score >= 30:
            return "Moderate flood risk. Monitor local flood zones and drainage."
        else:
            return "Low flood risk. Standard precautions sufficient."
    
    def _get_temperature_description(self, score: float) -> str:
        """Get temperature risk description"""
        if score >= 40:
            return "Extreme temperature variations. Higher HVAC costs expected."
        elif score >= 20:
            return "Moderate temperature ranges. Standard climate control needs."
        else:
            return "Mild climate conditions. Energy efficient location."
    
    def _get_precipitation_description(self, score: float) -> str:
        """Get precipitation risk description"""
        if score >= 40:
            return "Extreme precipitation patterns. Enhanced drainage recommended."
        elif score >= 20:
            return "Variable precipitation. Standard water management sufficient."
        else:
            return "Stable precipitation patterns. Low water-related risks."
    
    def _get_climate_recommendations(self, overall_risk: float) -> List[str]:
        """Get climate adaptation recommendations"""
        recommendations = []
        
        if overall_risk >= 50:
            recommendations.extend([
                "🏠 Consider climate-resilient building materials",
                "💧 Install comprehensive drainage systems",
                "🌡️ Invest in efficient HVAC systems",
                "📋 Review insurance coverage for climate risks"
            ])
        elif overall_risk >= 30:
            recommendations.extend([
                "🔍 Monitor local climate trends",
                "💧 Ensure adequate drainage",
                "🌡️ Consider energy-efficient upgrades"
            ])
        else:
            recommendations.extend([
                "✅ Location has favorable climate conditions",
                "🌱 Consider sustainable landscaping",
                "📊 Monitor long-term climate trends"
            ])
        
        return recommendations
    
    def _get_mock_climate_data(self, address: str, lat: float, lon: float) -> Dict[str, Any]:
        """Mock climate data for fallback"""
        return {
            "location": address,
            "coordinates": {"latitude": lat, "longitude": lon},
            "climate_risks": {
                "flood_risk": {"score": 25.0, "level": "Low", "description": "Low flood risk area"},
                "temperature_extremes": {"score": 20.0, "level": "Low", "description": "Moderate temperature ranges"},
                "precipitation_changes": {"score": 15.0, "level": "Low", "description": "Stable precipitation patterns"},
                "overall_climate_risk": {"score": 20.0, "level": "Low", "grade": "A"}
            },
            "current_conditions": {"current_temperature": 72, "humidity": 65},
            "recommendations": ["✅ Favorable climate conditions", "🌱 Consider sustainable features"],
            "data_source": "Mock Data (Climate API unavailable)"
        }
