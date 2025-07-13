from crewai import Agent, Task, Crew, Process, tool
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

# Enhanced Tools with Real Data
@tool("Property Research Tool")
def property_research_tool(address: str) -> str:
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
            
            # Return comprehensive report
            return f"""Property Research Report for {address}
            
Location: {geocode_result.get('address', address)}
Coordinates: {lat}, {lon}
Area Score: {area_insights.get('area_score', 'N/A')}/10
Demographics: Population {demographics.get('population', 'N/A')}, 
Median Income ${demographics.get('median_income', 'N/A')}"""
        else:
            return f"Unable to geocode address: {address}"
            
    except Exception as e:
        return f"Error researching property: {str(e)}"

@tool("Market Analysis Tool")
def market_analysis_tool(location: str) -> str:
    """Analyze local market conditions using real demographic and economic data"""
    try:
        # Initialize APIs
        google_maps = GoogleMapsAPI()
        census = CensusAPI()
        
        # Get location data
        geocode_result = google_maps.geocode_address(location)
        
        if geocode_result.get("coordinates"):
            state = geocode_result.get("address_components", {}).get("state", "")
            state_code = census.get_state_code(state) if state else ""
            demographics = census.get_location_demographics(location, state_code)
            
            # Simple market analysis
            median_income = demographics.get('median_income', 0)
            median_home_value = demographics.get('median_home_value', 0)
            
            if median_income > 75000:
                market_strength = "Strong"
            elif median_income > 50000:
                market_strength = "Moderate"
            else:
                market_strength = "Developing"
            
            return f"""Market Analysis for {location}
            
Market Strength: {market_strength}
Median Home Value: ${median_home_value}
Median Income: ${median_income}
Population: {demographics.get('population', 'N/A')}"""
        else:
            return f"Unable to analyze market for: {location}"
            
    except Exception as e:
        return f"Error analyzing market: {str(e)}"

@tool("Risk Assessment Tool")
def risk_assessment_tool(address: str) -> str:
    """Evaluate comprehensive investment risks using real environmental and market data"""
    try:
        # Initialize APIs
        google_maps = GoogleMapsAPI()
        census = CensusAPI()
        climate_api = ClimateAPI()
        
        # Get location data
        geocode_result = google_maps.geocode_address(address)
        
        if geocode_result.get("coordinates"):
            lat = geocode_result["coordinates"]["latitude"]
            lon = geocode_result["coordinates"]["longitude"]
            
            # Get climate risks
            climate_risks = climate_api.get_climate_risk_assessment(lat, lon, address)
            
            # Get demographics
            state = geocode_result.get("address_components", {}).get("state", "")
            state_code = census.get_state_code(state) if state else ""
            demographics = census.get_location_demographics(address, state_code)
            
            # Simple risk assessment
            climate_score = climate_risks.get('climate_risks', {}).get('overall_climate_risk', {}).get('score', 5)
            employment_rate = demographics.get('employment_rate', 90)
            
            if climate_score < 3 and employment_rate > 95:
                risk_grade = "Low Risk (A)"
            elif climate_score < 5 and employment_rate > 90:
                risk_grade = "Moderate Risk (B)"
            else:
                risk_grade = "Higher Risk (C)"
            
            return f"""Risk Assessment for {address}
            
Overall Risk Grade: {risk_grade}
Climate Risk Score: {climate_score}/10
Employment Rate: {employment_rate}%
Flood Risk: {climate_risks.get('climate_risks', {}).get('flood_risk', {}).get('level', 'N/A')}"""
        else:
            return f"Unable to assess risks for: {address}"
            
    except Exception as e:
        return f"Error assessing risks: {str(e)}"

class PropertyAnalysisCrew:
    def __init__(self):
        # Initialize tools
        self.property_tool = property_research_tool
        self.market_tool = market_analysis_tool
        self.risk_tool = risk_assessment_tool
        
        # Define agents
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
        try:
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
                    "Property Research Specialist",
                    "Market Intelligence Analyst", 
                    "Risk Management Specialist",
                    "Executive Report Writer"
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
