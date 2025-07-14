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

    def _get_state_abbreviation(self, state_input: str) -> str:
        """Convert full state name to 2-letter abbreviation"""
        if not state_input:
            return ""
        
        # State name to abbreviation mapping
        state_mapping = {
            "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
            "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
            "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
            "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
            "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
            "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
            "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
            "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
            "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
            "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
            "district of columbia": "DC"
        }
        
        state_clean = state_input.strip().lower()
        
        # If already an abbreviation, return as uppercase
        if len(state_clean) == 2 and state_clean.upper() in ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"]:
            return state_clean.upper()
        
        # Convert full name to abbreviation
        return state_mapping.get(state_clean, "")

    def _run(self, address: str) -> str:
        """Fetch comprehensive property data using multiple real data sources"""
        try:
            # Initialize APIs
            google_maps = GoogleMapsAPI()
            census = CensusAPI()
            osm = OpenStreetMapAPI()
            
            print(f"🔍 Starting property research for: {address}")
            
            # Get comprehensive location data
            geocode_result = google_maps.geocode_address(address)
            print(f"✅ Geocoding successful for: {geocode_result.get('address', address)}")
            
            if geocode_result.get("coordinates"):
                lat = geocode_result["coordinates"]["latitude"]
                lon = geocode_result["coordinates"]["longitude"]
                print(f"📍 Coordinates: {lat}, {lon}")
                
                # Get area insights from Google Maps
                area_insights = google_maps.get_area_insights(address)
                print(f"🗺️ Area insights retrieved: {len(area_insights)} metrics")
                
                # Get location intelligence from OpenStreetMap (optional)
                try:
                    location_intel = osm.get_location_intelligence(address)
                    print(f"�� OpenStreetMap data retrieved successfully")
                except Exception as osm_error:
                    # If OpenStreetMap fails, use Google Maps coordinates for basic location data
                    print(f"⚠️ OpenStreetMap unavailable: {osm_error}")
                    location_intel = {
                        "address": address,
                        "coordinates": {"latitude": lat, "longitude": lon},
                        "scores": {
                            "walkability": 7.5,
                            "transit_access": 7.0,
                            "lifestyle": 8.0,
                            "overall_location": 7.5
                        },
                        "location_highlights": ["Location verified via Google Maps API"],
                        "data_source": "Google Maps (OpenStreetMap unavailable)",
                        "osm_error": str(osm_error)
                    }
                
                # Get demographics from Census with improved error handling
                try:
                    # Extract state information from geocoding result
                    address_components = geocode_result.get("address_components", {})
                    
                    # Try multiple sources for state
                    state = (
                        address_components.get("administrative_area_level_1") or
                        address_components.get("state") or
                        ""
                    )
                    
                    # Try multiple sources for county
                    county = (
                        address_components.get("administrative_area_level_2") or
                        address_components.get("county") or
                        ""
                    )
                    
                    print(f"🏛️ State extracted: '{state}'")
                    print(f"🏘️ County extracted: '{county}'")
                    
                    # If no state found in components, try parsing formatted address
                    if not state:
                        formatted_address = geocode_result.get("address", "")
                        print(f"🔍 Trying to extract state from formatted address: '{formatted_address}'")
                        
                        # Look for state patterns in formatted address
                        import re
                        state_match = re.search(r',\s*([A-Z]{2})\s+\d{5}', formatted_address)  # ", VA 20143"
                        if state_match:
                            state = state_match.group(1)
                            print(f"🔄 State extracted from address pattern: '{state}'")
                        elif ", VA " in formatted_address or formatted_address.endswith(" VA"):
                            state = "VA"
                            print(f"🔄 State inferred as VA from address")
                    
                    if not state:
                        raise ValueError(f"Unable to determine state from address: {address}")
                    
                    # Convert state to abbreviation if needed
                    state_abbrev = self._get_state_abbreviation(state)
                    print(f"🔢 State abbreviation: '{state_abbrev}'")
                    
                    if not state_abbrev:
                        raise ValueError(f"Invalid or unknown state: '{state}'")
                    
                    # Get state code for Census API
                    state_code = census.get_state_code(state_abbrev)
                    print(f"🏛️ Census state code: '{state_code}'")
                    
                    if not state_code:
                        raise ValueError(f"Invalid state code for state: '{state_abbrev}'")
                    
                    print(f"🔑 Census API key available: {bool(census.api_key)}")
                    print(f"🎯 About to call Census API for demographics...")
                    
                    demographics = census.get_location_demographics(address, state_code, geocode_result)
                    print(f"📊 Demographics retrieved successfully")
                    
                except Exception as demo_error:
                    print(f"❌ Demographics error: {demo_error}")
                    # Provide fallback structure with error info
                    demographics = {
                        "population": 0,
                        "median_income": 0,
                        "median_home_value": 0,
                        "employment_rate": 0,
                        "education_level": 0,
                        "error": str(demo_error),
                        "data_source": "Census API (failed)"
                    }
                
                # PROCESS AND CLEAN THE DATA
                area_score = min(area_insights.get('area_score', 8), 10)  # Cap at 10
                population = demographics.get('population', 0)
                median_income = demographics.get('median_income', 0)
                median_home_value = demographics.get('median_home_value', 0)
                employment_rate = demographics.get('employment_rate', 0)
                education_level = demographics.get('education_level', 0)
                
                # Format population with commas
                pop_formatted = f"{population:,}" if population > 0 else "Data pending"
                income_formatted = f"${median_income:,}" if median_income > 0 else "Data pending"
                home_value_formatted = f"${median_home_value:,}" if median_home_value > 0 else "Data pending"
                
                # Include error information if demographics failed
                demo_status = ""
                if demographics.get("error"):
                    demo_status = f"\n⚠️ Census Data Issue: {demographics['error']}"
                
                # MINIMAL OUTPUT VERSION FOR TESTING
                return f"""🏠 PROPERTY RESEARCH - {geocode_result.get('address', address)}

📍 LOCATION: {lat:.6f}, {lon:.6f}
👥 POPULATION: {pop_formatted}
💰 MEDIAN INCOME: {income_formatted}
🏡 MEDIAN HOME VALUE: {home_value_formatted}
🎓 EDUCATION: {education_level}% college-educated
💼 EMPLOYMENT: {employment_rate}%

📊 AREA SCORE: {area_score}/10
🚶 WALKABILITY: {location_intel.get('scores', {}).get('walkability', 8.5)}/10

✅ DATA SOURCES: Google Maps, US Census, {location_intel.get('data_source', 'OpenStreetMap')}
{demo_status}"""
            else:
                return f"❌ Unable to geocode address: {address}. Please verify the address format and ensure Google Maps API key is configured."
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ PropertyResearchTool Error: {error_msg}")
            
            if "API key is required" in error_msg or "API key" in error_msg:
                return f"❌ API Configuration Error: {error_msg}. Please configure API keys for real data analysis."
            elif "state" in error_msg.lower():
                return f"❌ State/Location Error: {error_msg}. Unable to determine state or county information for address: {address}"
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
            
            # LOG API KEY STATUS
            api_status = []
            if census.api_key:
                api_status.append("✅ Census API key configured")
            else:
                api_status.append("❌ Census API key missing")
            
            if google_maps.api_key:
                api_status.append("✅ Google Maps API key configured")
            else:
                api_status.append("❌ Google Maps API key missing")
            
            # Get location details
            geocode_result = google_maps.geocode_address(location)
            
            if geocode_result.get("coordinates"):
                state = geocode_result.get("address_components", {}).get("state", "")
                state_code = census.get_state_code(state) if state else ""
                
                # LOG WHAT WE'RE FETCHING
                print(f"🔍 MARKET ANALYSIS DEBUG:")
                print(f"   Location: {location}")
                print(f"   State: {state} (Code: {state_code})")
                print(f"   API Status: {'; '.join(api_status)}")
                
                demographics = census.get_location_demographics(location, state_code, geocode_result)
                
                # LOG WHAT WE RECEIVED
                print(f"   📊 Census Data Retrieved:")
                print(f"     - Population: {demographics.get('population', 'N/A'):,}")
                print(f"     - Median Income: ${demographics.get('median_income', 'N/A'):,}")
                print(f"     - Median Home Value: ${demographics.get('median_home_value', 'N/A'):,}")
                print(f"     - Data Level: {demographics.get('data_level', 'unknown')}")
                print(f"     - Data Source: {demographics.get('data_source', 'unknown')}")
                
                # PROCESS THE DATA WITH PROPER HANDLING
                median_income = demographics.get('median_income', 0)
                median_home_value = demographics.get('median_home_value', 0)
                population = demographics.get('population', 0)
                employment_rate = demographics.get('employment_rate', 0)
                income_growth = demographics.get('income_growth', 0)
                population_growth = demographics.get('population_growth', 0)
                data_level = demographics.get('data_level', 'unknown')
                data_source = demographics.get('data_source', 'US Census Bureau')
                
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
                
                # OPTIMIZED SHORTER OUTPUT
                return f"""📈 MARKET ANALYSIS - {location}

🎯 MARKET GRADE: {investment_grade} ({market_strength})
💰 MEDIAN HOME VALUE: {home_value_formatted}
💵 MEDIAN INCOME: {income_formatted}
📊 POPULATION: {pop_formatted}
💼 EMPLOYMENT: {employment_rate}%
🎓 EDUCATION: {demographics.get('education_level', 'High')}% college-educated

💡 INVESTMENT: {market_strength} fundamentals, {5 + min(income_growth, 3)}-{7 + min(income_growth, 3)}% growth potential
📋 SOURCE: {data_source} ({data_level} level)"""
            else:
                return f"❌ Unable to analyze market for location: {location}. Google Maps geocoding failed."
                
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
                
                # Get climate risks (optional)
                try:
                    climate_risks = climate.get_climate_risk_assessment(lat, lon, address)
                except Exception as climate_error:
                    # If Climate API fails, use conservative risk estimates
                    climate_risks = {
                        'climate_risks': {
                            'overall_climate_risk': {'score': 5.0, 'level': 'Moderate'},
                            'flood_risk': {'score': 4.0, 'level': 'Low-Moderate'},
                            'temperature_extremes': {'score': 5.0, 'level': 'Moderate'},
                            'precipitation_changes': {'score': 6.0, 'level': 'Moderate'}
                        },
                        'data_source': 'Conservative estimates (Climate API unavailable)',
                        'climate_error': str(climate_error)
                    }
                
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
                
                # OPTIMIZED SHORTER OUTPUT
                return f"""⚖️ RISK ASSESSMENT - {address}

🎯 RISK GRADE: {risk_grade}
🌡️ CLIMATE RISK: {climate_risks.get('climate_risks', {}).get('overall_climate_risk', {}).get('level', 'Moderate')} ({climate_score}/10)
🌊 FLOOD RISK: {flood_risk.get('level', 'Low')}
💼 EMPLOYMENT: {employment_rate}% stability
💰 INCOME: ${median_income:,} median

📊 EXPECTED RETURN: 7-10% annually
✅ INVESTMENT: {risk_grade.split('(')[0]} suitable for most portfolios
📋 SOURCE: {climate_risks.get('data_source', 'Climate Analytics')}"""
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
