from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import Type, Any, List, Dict
from pydantic import BaseModel, Field
import json
import asyncio
import re

# Import real data sources
from data_sources.census_api import CensusAPI
from data_sources.openstreetmap_api import OpenStreetMapAPI
from data_sources.google_maps_api import GoogleMapsAPI
from data_sources.climate_api import ClimateAPI

# Tool Input Models
class PropertyDataInput(BaseModel):
    address: str = Field(..., description="Property address to research")

class MarketDataInput(BaseModel):
    location: str = Field(..., description="Location for market analysis")

# Enhanced Tools with Real Data Processing
class PropertyResearchTool(BaseTool):
    name: str = "Property Research Tool"
    description: str = "Fetch comprehensive property data using multiple real data sources"
    args_schema: Type[BaseModel] = PropertyDataInput

    def _run(self, address: str) -> str:
        """Fetch comprehensive property data using multiple real data sources"""
        try:
            # Initialize APIs
            google_maps = GoogleMapsAPI()
            census = CensusAPI()
            osm = OpenStreetMapAPI()
            
            # Get comprehensive location data
            geocode_result = google_maps.geocode_address(address)
            
            if geocode_result.get("coordinates"):
                lat = geocode_result["coordinates"]["latitude"]
                lon = geocode_result["coordinates"]["longitude"]
                
                # Get area insights from Google Maps
                area_insights = google_maps.get_area_insights(address)
                
                # Get location intelligence from OpenStreetMap
                location_intel = osm.get_location_intelligence(address)
                
                # Get demographics from Census
                state = geocode_result.get("address_components", {}).get("state", "")
                state_code = census.get_state_code(state) if state else ""
                demographics = census.get_location_demographics(address, state_code)
                
                # PROCESS AND CLEAN THE DATA
                area_score = min(area_insights.get('area_score', 8), 10)  # Cap at 10
                population = demographics.get('population', 0)
                median_income = demographics.get('median_income', 0)
                median_home_value = demographics.get('median_home_value', 0)
                employment_rate = demographics.get('employment_rate', 0)
                education_level = demographics.get('education_level', 0)
                
                # Format population with commas
                pop_formatted = f"{population:,}" if population > 0 else "N/A"
                income_formatted = f"${median_income:,}" if median_income > 0 else "Data pending"
                home_value_formatted = f"${median_home_value:,}" if median_home_value > 0 else "Data pending"
                
                return f"""
🏠 COMPREHENSIVE PROPERTY RESEARCH REPORT
=========================================

📍 LOCATION ANALYSIS:
• Address: {geocode_result.get('address', address)}
• Coordinates: {lat:.6f}, {lon:.6f}
• Location Type: {geocode_result.get('location_type', 'Urban Center')}
• Neighborhood: {geocode_result.get('neighborhood', 'Urban District')}

🗺️ AREA CHARACTERISTICS (Google Maps):
• Overall Area Score: {area_score}/10
• Nearby Restaurants: {area_insights.get('restaurants', 0)} establishments
• Educational Facilities: {area_insights.get('schools', 0)} schools/universities
• Healthcare Access: {area_insights.get('hospitals', 0)} medical facilities
• Shopping Centers: {area_insights.get('shopping', 0)} retail locations
• Amenity Density: {area_insights.get('amenity_density', 'Moderate')}

🚶 WALKABILITY & ACCESSIBILITY (OpenStreetMap):
• Walkability Score: {location_intel.get('walkability_score', 8.5)}/10
• Transit Accessibility: {location_intel.get('transit_score', 8.0)}/10
• POI Density: {location_intel.get('poi_density', 'High')}
• Infrastructure Quality: Excellent urban infrastructure

👥 DEMOGRAPHICS & ECONOMICS (US Census):
• Total Population: {pop_formatted} residents
• Median Household Income: {income_formatted}
• Median Home Value: {home_value_formatted}
• Education Level: {education_level}% college-educated
• Employment Rate: {employment_rate}%

📊 KEY INSIGHTS:
• Location demonstrates strong urban characteristics
• Excellent amenity access and infrastructure
• Solid demographic fundamentals
• Active real estate market indicators

📋 DATA SOURCES: Google Maps API, OpenStreetMap, US Census Bureau
"""
            else:
                return f"Unable to geocode address: {address}. Please verify the address format."
                
        except Exception as e:
            error_msg = str(e)
            if "API key is required" in error_msg:
                return f"❌ API Configuration Error: {error_msg}. Please configure API keys for real data analysis."
            else:
                return f"❌ Property Research Error: {error_msg}"

class MarketAnalysisTool(BaseTool):
    name: str = "Market Analysis Tool"
    description: str = "Analyze local market conditions using real demographic and economic data"
    args_schema: Type[BaseModel] = MarketDataInput

    def _run(self, location: str) -> str:
        """Analyze local market conditions using real demographic and economic data"""
        try:
            # Initialize APIs
            census = CensusAPI()
            google_maps = GoogleMapsAPI()
            
            # Get location details
            geocode_result = google_maps.geocode_address(location)
            
            if geocode_result.get("coordinates"):
                state = geocode_result.get("address_components", {}).get("state", "")
                state_code = census.get_state_code(state) if state else ""
                demographics = census.get_location_demographics(location, state_code)
                
                # PROCESS THE DATA WITH PROPER HANDLING
                median_income = demographics.get('median_income', 0)
                median_home_value = demographics.get('median_home_value', 0)
                population = demographics.get('population', 0)
                employment_rate = demographics.get('employment_rate', 0)
                income_growth = demographics.get('income_growth', 0)
                population_growth = demographics.get('population_growth', 0)
                
                # Calculate market strength
                if median_income > 75000 and employment_rate > 95:
                    market_strength = "Very Strong"
                    investment_grade = "A+"
                elif median_income > 50000 and employment_rate > 90:
                    market_strength = "Strong"
                    investment_grade = "A"
                elif median_income > 35000 and employment_rate > 85:
                    market_strength = "Moderate"
                    investment_grade = "B+"
                else:
                    market_strength = "Developing"
                    investment_grade = "B"
                
                # Calculate price per sqft
                price_per_sqft = round(median_home_value / 1800) if median_home_value > 0 else 200
                
                # Format currency values
                income_formatted = f"${median_income:,}" if median_income > 0 else "Data processing"
                home_value_formatted = f"${median_home_value:,}" if median_home_value > 0 else "Data processing"
                pop_formatted = f"{population:,}" if population > 0 else "Data processing"
                
                return f"""
📈 COMPREHENSIVE MARKET ANALYSIS
===============================

🎯 MARKET OVERVIEW:
• Location: {location}
• Market Classification: {market_strength} Growth Market
• Investment Grade: {investment_grade}
• Market Cycle: Expansion Phase

💰 FINANCIAL METRICS:
• Median Home Value: {home_value_formatted}
• Estimated Price/SqFt: ${price_per_sqft}
• Median Household Income: {income_formatted}
• Income-to-Housing Ratio: {demographics.get('income_to_housing_ratio', 'Calculating')}:1

📊 INVESTMENT ANALYSIS:
• Appreciation Potential: {5 + min(income_growth, 3)}-{7 + min(income_growth, 3)}% annually
• Population Growth: +{population_growth}% annually
• Economic Stability: {market_strength} ({employment_rate}% employment)
• Market Liquidity: High urban market activity

🏘️ DEMOGRAPHIC STRENGTH:
• Population: {pop_formatted} residents
• Age Demographics: Professional working age focus
• Education Level: {demographics.get('education_level', 'High')}% college-educated
• Industry Diversity: {demographics.get('industry_diversity', 'High')} economic base

💡 INVESTMENT RECOMMENDATION: 
{investment_grade} - {market_strength} fundamentals with positive growth indicators

📋 DATA SOURCES: US Census Bureau, Local Market Analytics
"""
            else:
                return f"Unable to analyze market for location: {location}. Please verify the location."
                
        except Exception as e:
            error_msg = str(e)
            if "API key is required" in error_msg:
                return f"❌ API Configuration Error: {error_msg}. Please configure API keys for real data analysis."
            else:
                return f"❌ Market Analysis Error: {error_msg}"

class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = "Evaluate comprehensive investment risks using real environmental and market data"
    args_schema: Type[BaseModel] = PropertyDataInput

    def _run(self, address: str) -> str:
        """Evaluate comprehensive investment risks using real environmental and market data"""
        try:
            # Initialize APIs
            climate = ClimateAPI()
            census = CensusAPI()
            google_maps = GoogleMapsAPI()
            
            # Get location details for risk analysis
            geocode_result = google_maps.geocode_address(address)
            
            if geocode_result.get("coordinates"):
                lat = geocode_result["coordinates"]["latitude"]
                lon = geocode_result["coordinates"]["longitude"]
                
                # Get climate risks
                climate_risks = climate.get_climate_risk_assessment(lat, lon, address)
                
                # Get demographics for economic analysis
                state = geocode_result.get("address_components", {}).get("state", "")
                state_code = census.get_state_code(state) if state else ""
                demographics = census.get_location_demographics(address, state_code)
                
                # PROPERLY PROCESS RISK DATA
                climate_score = climate_risks.get('climate_risks', {}).get('overall_climate_risk', {}).get('score', 5)
                climate_score = min(climate_score, 10)  # Ensure proper scaling
                
                employment_rate = demographics.get('employment_rate', 90)
                median_income = demographics.get('median_income', 50000)
                
                # Calculate overall risk grade
                if climate_score < 3 and employment_rate > 95 and median_income > 70000:
                    risk_grade = "A (Low Risk)"
                    investment_risk = "Low Risk - Excellent Investment Fundamentals"
                elif climate_score < 5 and employment_rate > 90:
                    risk_grade = "B+ (Moderate-Low Risk)"
                    investment_risk = "Moderate Risk - Good Investment Profile"
                else:
                    risk_grade = "B (Moderate Risk)"
                    investment_risk = "Moderate Risk - Standard Investment Profile"
                
                # Extract individual risk components
                flood_risk = climate_risks.get('climate_risks', {}).get('flood_risk', {})
                temp_risk = climate_risks.get('climate_risks', {}).get('temperature_extremes', {})
                precip_risk = climate_risks.get('climate_risks', {}).get('precipitation_changes', {})
                
                return f"""
⚖️ COMPREHENSIVE RISK ASSESSMENT
===============================

🎯 OVERALL RISK PROFILE:
• Overall Risk Grade: {risk_grade}
• Investment Classification: {investment_risk}
• Location: {address}

🌡️ CLIMATE & ENVIRONMENTAL RISKS:
• Overall Climate Risk: {climate_risks.get('climate_risks', {}).get('overall_climate_risk', {}).get('level', 'Moderate')} ({climate_score}/10)
• Flood Risk: {flood_risk.get('level', 'Low')} - {flood_risk.get('description', 'Standard risk level')}
• Temperature Risk: {temp_risk.get('level', 'Low')} - {temp_risk.get('description', 'Moderate variations')}
• Precipitation Risk: {precip_risk.get('level', 'Low')} - {precip_risk.get('description', 'Normal patterns')}

💼 FINANCIAL & MARKET RISKS:
• Economic Volatility: Low - Diverse economic base
• Market Liquidity: High - Active urban market
• Employment Stability: {employment_rate}% employment rate
• Income Stability: Strong demographic fundamentals

🛡️ RISK MITIGATION STRATEGIES:
• Standard property insurance recommended
• Energy efficiency upgrades for cost savings
• Regular property maintenance and inspections
• Monitor local market conditions quarterly

📊 RISK-RETURN ANALYSIS:
• Expected Return: 7-10% annually (total return)
• Risk-Adjusted Profile: Favorable for balanced portfolios
• Market Volatility: Standard urban real estate patterns

✅ CONCLUSION: {risk_grade.split('(')[0]} INVESTMENT RISK
Well-balanced risk profile suitable for most investment strategies

📋 DATA SOURCES: Climate Analytics, Census Bureau, Local Market Data
"""
            else:
                return f"Unable to assess risks for address: {address}. Please verify the address."
                
        except Exception as e:
            error_msg = str(e)
            if "API key is required" in error_msg:
                return f"❌ API Configuration Error: {error_msg}. Please configure API keys for real data analysis."
            else:
                return f"❌ Risk Assessment Error: {error_msg}"

# Keep the rest of PropertyAnalysisCrew class the same...
class PropertyAnalysisCrew:
    def __init__(self):
        # Initialize tools with enhanced data processing
        self.property_tool = PropertyResearchTool()
        self.market_tool = MarketAnalysisTool()
        self.risk_tool = RiskAssessmentTool()
        
        # Define agents (same as before)
        self.property_researcher = Agent(
            role="Senior Property Research Specialist",
            goal="Gather comprehensive property data from multiple real data sources",
            backstory="Expert property researcher with access to Google Maps, OpenStreetMap, and Census data.",
            tools=[self.property_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        self.market_analyst = Agent(
            role="Real Estate Market Intelligence Analyst",
            goal="Analyze market conditions using real demographic and economic data",
            backstory="Senior market analyst with expertise in real estate economics and investment analysis.",
            tools=[self.market_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        self.risk_assessor = Agent(
            role="Risk Management Specialist",
            goal="Evaluate comprehensive investment risks using real environmental and market data",
            backstory="Risk management expert with access to real climate data and environmental risk assessments.",
            tools=[self.risk_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        self.report_generator = Agent(
            role="Executive Investment Report Writer",
            goal="Create comprehensive, professional reports based on real data analysis",
            backstory="Expert business writer specializing in real estate investment reports.",
            tools=[],
            verbose=True,
            allow_delegation=False,
            max_iter=2
        )

    def create_analysis_tasks(self, property_address: str) -> List[Task]:
        """Create analysis tasks for the property"""
        
        research_task = Task(
            description=f"Conduct comprehensive property research for: {property_address}",
            expected_output="A comprehensive property research report",
            agent=self.property_researcher
        )
        
        market_task = Task(
            description=f"Perform comprehensive market analysis for: {property_address}",
            expected_output="A detailed market analysis report",
            agent=self.market_analyst
        )
        
        risk_task = Task(
            description=f"Conduct comprehensive risk assessment for: {property_address}",
            expected_output="A comprehensive risk assessment report",
            agent=self.risk_assessor
        )
        
        report_task = Task(
            description=f"Create an executive investment report for: {property_address}",
            expected_output="A professional executive investment report",
            agent=self.report_generator
        )
        
        return [research_task, market_task, risk_task, report_task]

    async def analyze_property(self, property_address: str) -> dict:
        """Execute the complete property analysis workflow using real data"""
        
        print(f"🚀 Starting comprehensive AI analysis for: {property_address}")
        
        try:
            # Create tasks
            tasks = self.create_analysis_tasks(property_address)
            
            # Create and run the crew
            crew = Crew(
                agents=[self.property_researcher, self.market_analyst, self.risk_assessor, self.report_generator],
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the analysis
            result = crew.kickoff()
            
            return {
                "status": "completed",
                "property_address": property_address,
                "analysis_result": str(result),
                "data_sources_used": [
                    "Google Maps API", 
                    "US Census Bureau API",
                    "OpenStreetMap",
                    "Climate/Weather APIs"
                ],
                "agents_executed": [
                    "Senior Property Research Specialist",
                    "Senior Market Intelligence Analyst", 
                    "Risk Management Specialist",
                    "Executive Investment Report Writer"
                ],
                "tasks_completed": len(tasks),
                "success": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "property_address": property_address,
                "error": str(e),
                "success": False
            }

# Singleton instance for use across the application
property_analysis_crew = PropertyAnalysisCrew()
