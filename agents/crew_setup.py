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
            
            # Compile comprehensive property research
            return f"""
            COMPREHENSIVE PROPERTY RESEARCH REPORT
            =====================================
            
            LOCATION DETAILS:
            - Address: {geocode_result.get('address', address)}
            - Coordinates: {lat}, {lon}
            - Location Type: {geocode_result.get('location_type', 'N/A')}
            
            AREA INSIGHTS (Google Maps):
            - Area Score: {area_insights.get('area_score', 'N/A')}/10
            - Restaurants: {area_insights.get('restaurants', 0)} nearby
            - Schools: {area_insights.get('schools', 0)} nearby
            - Hospitals: {area_insights.get('hospitals', 0)} nearby
            - Shopping: {area_insights.get('shopping', 0)} nearby
            
            LOCATION INTELLIGENCE (OpenStreetMap):
            - POI Density: {location_intel.get('poi_density', 'N/A')}
            - Walkability Score: {location_intel.get('walkability_score', 'N/A')}/10
            - Transit Accessibility: {location_intel.get('transit_score', 'N/A')}/10
            - Amenities: {location_intel.get('amenities', 'N/A')}
            
            DEMOGRAPHICS (US Census):
            - Population: {demographics.get('population', 'N/A')}
            - Median Income: ${demographics.get('median_income', 'N/A')}
            - Median Home Value: ${demographics.get('median_home_value', 'N/A')}
            - Education Level: {demographics.get('education_level', 'N/A')}
            - Employment Rate: {demographics.get('employment_rate', 'N/A')}%
            
            DATA SOURCES: Google Maps API, OpenStreetMap, US Census Bureau
            """
        else:
            return f"Unable to geocode address: {address}. Please verify the address."
            
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
            
            # Perform market analysis
            market_strength = _assess_market_strength(demographics)
            market_trend = _determine_market_trend(demographics)
            appreciation_potential = _assess_appreciation_potential(demographics)
            rental_market = _assess_rental_market(demographics)
            economic_stability = _assess_economic_stability(demographics)
            price_per_sqft = _estimate_price_per_sqft(demographics)
            market_position = _determine_market_position(demographics)
            growth_forecast = _forecast_growth(demographics)
            
            return f"""
            COMPREHENSIVE MARKET ANALYSIS
            ============================
            
            MARKET OVERVIEW:
            - Location: {location}
            - Market Strength: {market_strength}
            - Current Trend: {market_trend}
            - Market Position: {market_position}
            
            FINANCIAL METRICS:
            - Estimated Price/SqFt: ${price_per_sqft}
            - Median Home Value: ${demographics.get('median_home_value', 'N/A')}
            - Median Rent: ${demographics.get('median_rent', 'N/A')}
            - Income-to-Housing Ratio: {demographics.get('income_to_housing_ratio', 'N/A')}
            
            INVESTMENT ANALYSIS:
            - Appreciation Potential: {appreciation_potential}
            - Rental Market: {rental_market}
            - Economic Stability: {economic_stability}
            - Growth Forecast: {growth_forecast}
            
            DEMOGRAPHICS:
            - Population: {demographics.get('population', 'N/A')}
            - Median Income: ${demographics.get('median_income', 'N/A')}
            - Employment Rate: {demographics.get('employment_rate', 'N/A')}%
            - Education Level: {demographics.get('education_level', 'N/A')}
            
            DATA SOURCES: US Census Bureau, Google Maps API
            """
        else:
            return f"Unable to analyze market for location: {location}. Please verify the location."
            
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
            
            # Get demographics for economic analysis
            state = geocode_result.get("address_components", {}).get("state", "")
            state_code = census.get_state_code(state) if state else None
            demographics = census.get_location_demographics(address, state_code)
            
            # Calculate risk assessments
            overall_risk_grade = _calculate_overall_risk_grade(climate_risks, demographics)
            investment_risk_level = _determine_investment_risk_level(climate_risks, demographics)
            economic_volatility = _assess_economic_volatility(demographics)
            market_liquidity = _assess_market_liquidity(demographics)
            demographic_stability = _assess_demographic_stability(demographics)
            tax_risk = _assess_tax_risk(demographics)
            maintenance_risk = _assess_maintenance_risk(climate_risks)
            insurance_risk = _assess_insurance_risk(climate_risks)
            mitigation_strategies = _generate_mitigation_strategies(climate_risks, demographics)
            
            return f"""
            COMPREHENSIVE RISK ASSESSMENT
            ============================
            
            OVERALL RISK PROFILE:
            - Risk Grade: {overall_risk_grade}
            - Investment Risk Level: {investment_risk_level}
            - Location: {address}
            
            CLIMATE & ENVIRONMENTAL RISKS:
            - Overall Climate Risk: {climate_risks.get('climate_risks', {}).get('overall_climate_risk', {}).get('level', 'N/A')}
            - Flood Risk: {climate_risks.get('climate_risks', {}).get('flood_risk', {}).get('level', 'N/A')}
            - Temperature Risk: {climate_risks.get('climate_risks', {}).get('temperature_extremes', {}).get('level', 'N/A')}
            - Precipitation Risk: {climate_risks.get('climate_risks', {}).get('precipitation_changes', {}).get('level', 'N/A')}
            
            FINANCIAL RISKS:
            - Economic Volatility: {economic_volatility.get('level', 'N/A')}
            - Market Liquidity: {market_liquidity.get('level', 'N/A')}
            - Tax Risk: {tax_risk.get('level', 'N/A')}
            
            OPERATIONAL RISKS:
            - Maintenance Risk: {maintenance_risk.get('level', 'N/A')}
            - Insurance Risk: {insurance_risk.get('level', 'N/A')}
            - Demographic Stability: {demographic_stability.get('level', 'N/A')}
            
            MITIGATION STRATEGIES:
            {chr(10).join(f"• {strategy}" for strategy in mitigation_strategies)}
            
            DATA SOURCES: Climate APIs, US Census Bureau, Google Maps API
            """
        else:
            return f"Unable to assess risks for address: {address}. Please verify the address."
            
    except Exception as e:
        return f"Error assessing risks: {str(e)}"

# Helper functions for market analysis
def _assess_market_strength(demographics: Dict[str, Any]) -> str:
    """Assess market strength based on demographics"""
    median_income = demographics.get('median_income', 0)
    employment_rate = demographics.get('employment_rate', 0)
    population = demographics.get('population', 0)
    
    if median_income > 75000 and employment_rate > 95 and population > 10000:
        return "Very Strong"
    elif median_income > 50000 and employment_rate > 90:
        return "Strong"
    elif median_income > 35000 and employment_rate > 85:
        return "Moderate"
    else:
        return "Weak"

def _determine_market_trend(demographics: Dict[str, Any]) -> str:
    """Determine market trend based on demographics"""
    income_growth = demographics.get('income_growth', 0)
    population_growth = demographics.get('population_growth', 0)
    
    if income_growth > 3 and population_growth > 2:
        return "Strong Growth"
    elif income_growth > 1 and population_growth > 0:
        return "Moderate Growth"
    elif income_growth > -1 and population_growth > -1:
        return "Stable"
    else:
        return "Declining"

def _assess_appreciation_potential(demographics: Dict[str, Any]) -> str:
    """Assess property appreciation potential"""
    median_income = demographics.get('median_income', 0)
    education_level = demographics.get('education_level', 0)
    
    if median_income > 70000 and education_level > 80:
        return "High - Strong economic fundamentals"
    elif median_income > 50000 and education_level > 60:
        return "Moderate - Stable growth expected"
    else:
        return "Low - Limited appreciation expected"

def _assess_rental_market(demographics: Dict[str, Any]) -> str:
    """Assess rental market conditions"""
    median_rent = demographics.get('median_rent', 0)
    rental_vacancy = demographics.get('rental_vacancy', 10)
    
    if median_rent > 1500 and rental_vacancy < 5:
        return "Strong - High demand, low vacancy"
    elif median_rent > 1000 and rental_vacancy < 8:
        return "Moderate - Balanced market"
    else:
        return "Weak - High vacancy or low rents"

def _assess_economic_stability(demographics: Dict[str, Any]) -> str:
    """Assess economic stability"""
    employment_rate = demographics.get('employment_rate', 0)
    industry_diversity = demographics.get('industry_diversity', 50)
    
    if employment_rate > 95 and industry_diversity > 70:
        return "Very Stable"
    elif employment_rate > 90 and industry_diversity > 50:
        return "Stable"
    else:
        return "Moderate Risk"

def _estimate_price_per_sqft(demographics: Dict[str, Any]) -> int:
    """Estimate price per square foot"""
    median_home_value = demographics.get('median_home_value', 200000)
    median_income = demographics.get('median_income', 50000)
    
    # Simple estimation based on median values
    base_price = median_home_value / 2000  # Assume 2000 sqft average
    income_multiplier = min(median_income / 50000, 2.0)
    
    return int(base_price * income_multiplier)

def _determine_market_position(demographics: Dict[str, Any]) -> str:
    """Determine market position"""
    median_home_value = demographics.get('median_home_value', 200000)
    
    if median_home_value > 500000:
        return "Premium Market"
    elif median_home_value > 300000:
        return "Mid-Range Market"
    else:
        return "Affordable Market"

def _forecast_growth(demographics: Dict[str, Any]) -> str:
    """Forecast market growth"""
    population_growth = demographics.get('population_growth', 0)
    income_growth = demographics.get('income_growth', 0)
    
    if population_growth > 2 and income_growth > 3:
        return "Strong Growth Expected (5-7% annually)"
    elif population_growth > 1 and income_growth > 1:
        return "Moderate Growth Expected (3-5% annually)"
    else:
        return "Stable Growth Expected (1-3% annually)"

# Helper functions for risk assessment
def _calculate_overall_risk_grade(climate_risks: Dict, demographics: Dict) -> str:
    """Calculate overall risk grade"""
    climate_score = climate_risks.get('climate_risks', {}).get('overall_climate_risk', {}).get('score', 5)
    economic_stability = demographics.get('employment_rate', 90)
    
    if climate_score < 3 and economic_stability > 95:
        return "A (Low Risk)"
    elif climate_score < 5 and economic_stability > 90:
        return "B (Moderate Risk)"
    elif climate_score < 7 and economic_stability > 85:
        return "C (Medium Risk)"
    else:
        return "D (High Risk)"

def _determine_investment_risk_level(climate_risks: Dict, demographics: Dict) -> str:
    """Determine investment risk level"""
    climate_score = climate_risks.get('climate_risks', {}).get('overall_climate_risk', {}).get('score', 5)
    median_income = demographics.get('median_income', 50000)
    
    if climate_score < 4 and median_income > 60000:
        return "Low Risk"
    elif climate_score < 6 and median_income > 40000:
        return "Moderate Risk"
    else:
        return "High Risk"

def _assess_economic_volatility(demographics: Dict) -> Dict[str, Any]:
    """Assess economic volatility"""
    employment_rate = demographics.get('employment_rate', 90)
    industry_diversity = demographics.get('industry_diversity', 50)
    
    if employment_rate > 95 and industry_diversity > 70:
        return {"level": "Low", "description": "Stable employment and diverse economy"}
    elif employment_rate > 90:
        return {"level": "Moderate", "description": "Generally stable with some volatility"}
    else:
        return {"level": "High", "description": "Economic instability concerns"}

def _assess_market_liquidity(demographics: Dict) -> Dict[str, Any]:
    """Assess market liquidity"""
    population = demographics.get('population', 10000)
    median_home_value = demographics.get('median_home_value', 200000)
    
    if population > 50000 and median_home_value < 400000:
        return {"level": "High", "description": "Large market with accessible prices"}
    elif population > 20000:
        return {"level": "Moderate", "description": "Moderate market size"}
    else:
        return {"level": "Low", "description": "Small market, limited liquidity"}

def _assess_demographic_stability(demographics: Dict) -> Dict[str, Any]:
    """Assess demographic stability"""
    population_growth = demographics.get('population_growth', 0)
    age_median = demographics.get('age_median', 35)
    
    if population_growth > 1 and 25 < age_median < 45:
        return {"level": "Stable", "description": "Growing population with working-age residents"}
    elif population_growth > -1:
        return {"level": "Moderate", "description": "Stable population"}
    else:
        return {"level": "Declining", "description": "Population decline concerns"}

def _assess_tax_risk(demographics: Dict) -> Dict[str, Any]:
    """Assess tax risk"""
    # Simplified tax risk assessment
    median_home_value = demographics.get('median_home_value', 200000)
    
    if median_home_value > 500000:
        return {"level": "High", "description": "High property values may indicate high property taxes"}
    elif median_home_value > 300000:
        return {"level": "Moderate", "description": "Moderate property tax burden expected"}
    else:
        return {"level": "Low", "description": "Lower property tax burden expected"}

def _assess_maintenance_risk(climate_risks: Dict) -> Dict[str, Any]:
    """Assess maintenance risk based on climate"""
    climate_score = climate_risks.get('climate_risks', {}).get('overall_climate_risk', {}).get('score', 5)
    
    if climate_score > 7:
        return {"level": "High", "description": "High climate risk increases maintenance needs"}
    elif climate_score > 4:
        return {"level": "Moderate", "description": "Moderate climate-related maintenance expected"}
    else:
        return {"level": "Low", "description": "Low climate-related maintenance risk"}

def _assess_insurance_risk(climate_risks: Dict) -> Dict[str, Any]:
    """Assess insurance risk"""
    flood_risk = climate_risks.get('climate_risks', {}).get('flood_risk', {}).get('score', 5)
    
    if flood_risk > 7:
        return {"level": "High", "description": "High flood risk may increase insurance costs"}
    elif flood_risk > 4:
        return {"level": "Moderate", "description": "Moderate insurance risk"}
    else:
        return {"level": "Low", "description": "Low insurance risk"}

def _generate_mitigation_strategies(climate_risks: Dict, demographics: Dict) -> List[str]:
    """Generate risk mitigation strategies"""
    strategies = []
    
    # Climate-based strategies
    climate_score = climate_risks.get('climate_risks', {}).get('overall_climate_risk', {}).get('score', 5)
    if climate_score > 6:
        strategies.append("Consider climate-resilient building materials and designs")
        strategies.append("Evaluate flood insurance and emergency preparedness")
    
    # Economic-based strategies
    employment_rate = demographics.get('employment_rate', 90)
    if employment_rate < 90:
        strategies.append("Diversify investment portfolio to reduce regional economic risk")
        strategies.append("Consider shorter-term investment horizons")
    
    # Market-based strategies
    median_home_value = demographics.get('median_home_value', 200000)
    if median_home_value > 500000:
        strategies.append("Monitor market cycles closely due to high property values")
        strategies.append("Consider rental income to offset carrying costs")
    
    if not strategies:
        strategies.append("Maintain regular property inspections and maintenance")
        strategies.append("Stay informed about local market conditions")
    
    return strategies

class PropertyAnalysisCrew:
    def __init__(self):
        # Initialize tools
        self.property_tool = property_research_tool
        self.market_tool = market_analysis_tool
        self.risk_tool = risk_assessment_tool
        
        # Define agents (using function-based tools)
        self.property_researcher = Agent(
            role="Senior Property Research Specialist",
            goal="Gather comprehensive and accurate property data from multiple real data sources",
            backstory="""You are an expert property researcher with 15+ years of experience 
            in real estate analysis. You have access to the latest data from Google Maps, 
            OpenStreetMap, and US Census Bureau. You're meticulous about data accuracy 
            and always verify information from multiple sources. You provide detailed, 
            factual information with clear explanations of data sources.""",
            tools=[self.property_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        self.market_analyst = Agent(
            role="Real Estate Market Intelligence Analyst",
            goal="Analyze market conditions using real demographic and economic data",
            backstory="""You are a senior market analyst with expertise in real estate 
            economics and investment analysis. You have access to comprehensive Census Bureau 
            demographic data and Google Maps market intelligence. You excel at identifying 
            trends, market positioning, and investment opportunities using real-world data. 
            You provide actionable insights based on factual analysis.""",
            tools=[self.market_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        self.risk_assessor = Agent(
            role="Risk Management Specialist",
            goal="Evaluate comprehensive investment risks using real environmental and market data",
            backstory="""You are a risk management expert with access to real climate data 
            and environmental risk assessments. You use actual weather patterns, flood risk 
            data, and demographic stability indicators to provide accurate risk evaluations. 
            You're skilled at identifying environmental, financial, and market risks using 
            multiple real data sources. You provide clear risk scores and practical mitigation strategies.""",
            tools=[self.risk_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        self.report_generator = Agent(
            role="Executive Investment Report Writer",
            goal="Create comprehensive, professional reports based on real data analysis",
            backstory="""You are an expert business writer and consultant specializing 
            in real estate investment reports. You synthesize real data from multiple sources 
            including Census Bureau demographics, Google Maps intelligence, OpenStreetMap 
            location data, and climate risk assessments. Your reports are used by executives, 
            investors, and real estate professionals to make informed decisions. You create 
            executive-level summaries with specific recommendations based on factual analysis.""",
            tools=[],  # No tools needed - synthesizes information from other agents
            verbose=True,
            allow_delegation=False,
            max_iter=2
        )

    def create_analysis_tasks(self, property_address: str) -> List[Task]:
        """Create analysis tasks for the property"""
        
        research_task = Task(
            description=f"""
            Conduct comprehensive property research for: {property_address}
            
            Use the Property Research Tool to gather:
            1. Precise location details and coordinates
            2. Area insights from Google Maps (restaurants, schools, hospitals, shopping)
            3. Location intelligence from OpenStreetMap (walkability, transit, amenities)
            4. Demographic data from US Census Bureau
            
            Provide a detailed research report with all findings and data sources.
            """,
            expected_output="A comprehensive property research report with location details, area insights, and demographic data",
            agent=self.property_researcher
        )
        
        market_task = Task(
            description=f"""
            Perform comprehensive market analysis for: {property_address}
            
            Use the Market Analysis Tool to analyze:
            1. Current market strength and trends
            2. Financial metrics (price per sqft, median values, rent prices)
            3. Investment potential and appreciation forecasts
            4. Economic stability and growth prospects
            
            Base your analysis on real demographic and economic data.
            """,
            expected_output="A detailed market analysis report with investment recommendations",
            agent=self.market_analyst
        )
        
        risk_task = Task(
            description=f"""
            Conduct comprehensive risk assessment for: {property_address}
            
            Use the Risk Assessment Tool to evaluate:
            1. Climate and environmental risks (flood, temperature, precipitation)
            2. Financial risks (economic volatility, market liquidity, tax risks)
            3. Operational risks (maintenance, insurance, demographic stability)
            4. Mitigation strategies and recommendations
            
            Provide an overall risk grade and specific mitigation strategies.
            """,
            expected_output="A comprehensive risk assessment with risk grades and mitigation strategies",
            agent=self.risk_assessor
        )
        
        report_task = Task(
            description=f"""
            Create an executive investment report for: {property_address}
            
            Synthesize the findings from:
            1. Property research analysis
            2. Market analysis insights
            3. Risk assessment results
            
            Create a professional executive summary with:
            - Investment recommendation (Buy/Hold/Avoid)
            - Key findings and insights
            - Risk assessment summary
            - Specific action items
            - Data sources and methodology
            
            The report should be suitable for executive decision-making.
            """,
            expected_output="A professional executive investment report with clear recommendations",
            agent=self.report_generator
        )
        
        return [research_task, market_task, risk_task, report_task]

    async def analyze_property(self, property_address: str) -> dict:
        """Execute the complete property analysis workflow using real data"""
        
        print(f"🚀 Starting comprehensive AI analysis with real data for: {property_address}")
        
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
                    "Property Research Specialist (Real Data)",
                    "Market Intelligence Analyst (Census Data)", 
                    "Risk Management Specialist (Climate Data)",
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
