from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
from typing import Type, Any, List
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

# Enhanced Tools with Real Data
class PropertyResearchTool(BaseTool):
    name: str = "Property Research Tool"
    description: str = "Fetch comprehensive property data using multiple real data sources"
    args_schema: Type[BaseModel] = PropertyDataInput

    def _run(self, address: str) -> str:
        """Research property using real data sources"""
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
                state_code = census.get_state_code(state) if state else None
                demographics = census.get_location_demographics(address, state_code)
                
                # Compile comprehensive property research
                research_data = {
                    "address_analysis": {
                        "formatted_address": geocode_result.get("address", address),
                        "coordinates": geocode_result.get("coordinates"),
                        "location_type": geocode_result.get("location_type", "Approximate"),
                        "address_components": geocode_result.get("address_components", {})
                    },
                    "area_characteristics": {
                        "walkability_score": location_intel.get("scores", {}).get("walkability", 0),
                        "transit_score": location_intel.get("scores", {}).get("transit_access", 0),
                        "lifestyle_score": location_intel.get("scores", {}).get("lifestyle", 0),
                        "overall_location_score": location_intel.get("scores", {}).get("overall_location", 0)
                    },
                    "demographics": demographics,
                    "nearby_amenities": {
                        "restaurants": area_insights.get("nearby_amenities", {}).get("restaurants", 0),
                        "schools": area_insights.get("nearby_amenities", {}).get("schools", 0),
                        "hospitals": area_insights.get("nearby_amenities", {}).get("hospitals", 0),
                        "shopping": area_insights.get("nearby_amenities", {}).get("shopping_centers", 0)
                    },
                    "location_highlights": location_intel.get("location_highlights", []),
                    "data_sources": ["Google Maps API", "OpenStreetMap", "US Census Bureau"]
                }
                
                return f"COMPREHENSIVE PROPERTY RESEARCH for {address}:\n\n{json.dumps(research_data, indent=2)}"
            
            else:
                return f"Could not geocode address: {address}. Please verify the address format."
                
        except Exception as e:
            return f"Property research error for {address}: {str(e)}"

class MarketAnalysisTool(BaseTool):
    name: str = "Market Analysis Tool"
    description: str = "Analyze local market conditions using real demographic and economic data"
    args_schema: Type[BaseModel] = MarketDataInput

    def _run(self, location: str) -> str:
        """Analyze market using real data sources"""
        try:
            # Initialize APIs
            census = CensusAPI()
            google_maps = GoogleMapsAPI()
            
            # Get location details
            geocode_result = google_maps.geocode_address(location)
            
            if geocode_result.get("coordinates"):
                # Extract state for census data
                state = geocode_result.get("address_components", {}).get("state", "")
                state_code = census.get_state_code(state) if state else None
                
                # Get demographic and economic data
                demographics = census.get_location_demographics(location, state_code)
                
                # Analyze market conditions based on real data
                market_analysis = {
                    "location_summary": {
                        "analyzed_location": geocode_result.get("address", location),
                        "market_type": demographics.get("population", {}).get("density_category", "Unknown"),
                        "economic_tier": demographics.get("economics", {}).get("income_category", "Unknown")
                    },
                    "demographic_indicators": {
                        "population": demographics.get("population", {}).get("total", 0),
                        "median_household_income": demographics.get("economics", {}).get("median_household_income", 0),
                        "education_level": demographics.get("education", {}).get("bachelor_plus_rate", 0),
                        "homeownership_rate": demographics.get("housing", {}).get("homeownership_rate", 0)
                    },
                    "housing_market": {
                        "median_home_value": demographics.get("housing", {}).get("median_home_value", 0),
                        "median_rent": demographics.get("housing", {}).get("median_rent", 0),
                        "housing_units": demographics.get("housing", {}).get("total_units", 0),
                        "market_strength": self._assess_market_strength(demographics)
                    },
                    "investment_indicators": {
                        "market_trend": self._determine_market_trend(demographics),
                        "appreciation_potential": self._assess_appreciation_potential(demographics),
                        "rental_market": self._assess_rental_market(demographics),
                        "economic_stability": self._assess_economic_stability(demographics)
                    },
                    "comparable_analysis": {
                        "price_per_sqft_estimate": self._estimate_price_per_sqft(demographics),
                        "market_position": self._determine_market_position(demographics),
                        "growth_forecast": self._forecast_growth(demographics)
                    },
                    "data_sources": ["US Census Bureau", "Google Maps API"]
                }
                
                return f"MARKET ANALYSIS for {location}:\n\n{json.dumps(market_analysis, indent=2)}"
            
            else:
                return f"Could not analyze market for: {location}. Please verify the location."
                
        except Exception as e:
            return f"Market analysis error for {location}: {str(e)}"
    
    def _assess_market_strength(self, demographics: Dict[str, Any]) -> str:
        """Assess market strength based on demographics"""
        income = demographics.get("economics", {}).get("median_household_income", 0)
        home_value = demographics.get("housing", {}).get("median_home_value", 0)
        education = demographics.get("education", {}).get("bachelor_plus_rate", 0)
        
        score = 0
        if income > 75000: score += 1
        if home_value > 300000: score += 1
        if education > 35: score += 1
        
        if score >= 3: return "Strong"
        elif score >= 2: return "Moderate"
        else: return "Developing"
    
    def _determine_market_trend(self, demographics: Dict[str, Any]) -> str:
        """Determine market trend based on indicators"""
        education = demographics.get("education", {}).get("bachelor_plus_rate", 0)
        income = demographics.get("economics", {}).get("median_household_income", 0)
        
        if education > 40 and income > 70000:
            return "Rising"
        elif education > 25 and income > 50000:
            return "Stable"
        else:
            return "Variable"
    
    def _assess_appreciation_potential(self, demographics: Dict[str, Any]) -> str:
        """Assess property appreciation potential"""
        income_cat = demographics.get("economics", {}).get("income_category", "")
        education_level = demographics.get("education", {}).get("education_level", "")
        
        if "High" in income_cat and "Highly" in education_level:
            return "High (6-8% annually)"
        elif "Upper" in income_cat or "Well" in education_level:
            return "Moderate (4-6% annually)"
        else:
            return "Conservative (2-4% annually)"
    
    def _assess_rental_market(self, demographics: Dict[str, Any]) -> str:
        """Assess rental market conditions"""
        homeownership = demographics.get("housing", {}).get("homeownership_rate", 0)
        
        if homeownership < 50:
            return "Strong rental demand"
        elif homeownership < 70:
            return "Moderate rental market"
        else:
            return "Owner-dominated market"
    
    def _assess_economic_stability(self, demographics: Dict[str, Any]) -> str:
        """Assess economic stability"""
        income = demographics.get("economics", {}).get("median_household_income", 0)
        education = demographics.get("education", {}).get("bachelor_plus_rate", 0)
        
        if income > 60000 and education > 30:
            return "High stability"
        elif income > 45000 and education > 20:
            return "Moderate stability"
        else:
            return "Variable stability"
    
    def _estimate_price_per_sqft(self, demographics: Dict[str, Any]) -> int:
        """Estimate price per square foot"""
        home_value = demographics.get("housing", {}).get("median_home_value", 0)
        # Rough estimate: median home value / average home size (1800 sqft)
        return round(home_value / 1800) if home_value > 0 else 200
    
    def _determine_market_position(self, demographics: Dict[str, Any]) -> str:
        """Determine market position"""
        income_cat = demographics.get("economics", {}).get("income_category", "")
        
        if "High" in income_cat:
            return "Premium market"
        elif "Upper" in income_cat:
            return "Upper-mid market"
        elif "Middle" in income_cat:
            return "Mid market"
        else:
            return "Value market"
    
    def _forecast_growth(self, demographics: Dict[str, Any]) -> str:
        """Forecast market growth"""
        population = demographics.get("population", {}).get("total", 0)
        density = demographics.get("population", {}).get("density_category", "")
        
        if population > 100000 and "Urban" in density:
            return "Strong growth expected"
        elif population > 50000:
            return "Moderate growth expected"
        else:
            return "Stable growth expected"

class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = "Evaluate comprehensive investment risks using real environmental and market data"
    args_schema: Type[BaseModel] = PropertyDataInput

    def _run(self, address: str) -> str:
        """Assess risks using real data sources"""
        try:
            # Initialize APIs
            google_maps = GoogleMapsAPI()
            climate = ClimateAPI()
            census = CensusAPI()
            
            # Get location coordinates
            geocode_result = google_maps.geocode_address(address)
            
            if geocode_result.get("coordinates"):
                lat = geocode_result["coordinates"]["latitude"]
                lon = geocode_result["coordinates"]["longitude"]
                
                # Get climate risk assessment
                climate_risks = climate.get_climate_risk_assessment(lat, lon, address)
                
                # Get demographic data for market risk assessment
                state = geocode_result.get("address_components", {}).get("state", "")
                state_code = census.get_state_code(state) if state else None
                demographics = census.get_location_demographics(address, state_code)
                
                # Comprehensive risk assessment
                risk_assessment = {
                    "overall_risk_summary": {
                        "address": address,
                        "risk_grade": self._calculate_overall_risk_grade(climate_risks, demographics),
                        "investment_risk_level": self._determine_investment_risk_level(climate_risks, demographics)
                    },
                    "environmental_risks": {
                        "climate_risk_score": climate_risks.get("climate_risks", {}).get("overall_climate_risk", {}).get("score", 0),
                        "flood_risk": climate_risks.get("climate_risks", {}).get("flood_risk", {}),
                        "temperature_risk": climate_risks.get("climate_risks", {}).get("temperature_extremes", {}),
                        "precipitation_risk": climate_risks.get("climate_risks", {}).get("precipitation_changes", {})
                    },
                    "market_risks": {
                        "economic_volatility": self._assess_economic_volatility(demographics),
                        "market_liquidity": self._assess_market_liquidity(demographics),
                        "demographic_stability": self._assess_demographic_stability(demographics)
                    },
                    "financial_risks": {
                        "property_tax_risk": self._assess_tax_risk(demographics),
                        "maintenance_cost_risk": self._assess_maintenance_risk(climate_risks),
                        "insurance_cost_risk": self._assess_insurance_risk(climate_risks)
                    },
                    "mitigation_strategies": self._generate_mitigation_strategies(climate_risks, demographics),
                    "data_sources": ["Climate APIs", "US Census Bureau", "Google Maps"]
                }
                
                return f"COMPREHENSIVE RISK ASSESSMENT for {address}:\n\n{json.dumps(risk_assessment, indent=2)}"
            
            else:
                return f"Could not assess risks for: {address}. Please verify the address."
                
        except Exception as e:
            return f"Risk assessment error for {address}: {str(e)}"
    
    def _calculate_overall_risk_grade(self, climate_risks: Dict, demographics: Dict) -> str:
        """Calculate overall risk grade"""
        climate_score = climate_risks.get("climate_risks", {}).get("overall_climate_risk", {}).get("score", 50)
        
        # Market risk based on income stability
        income = demographics.get("economics", {}).get("median_household_income", 50000)
        market_risk = 30 if income > 75000 else 50 if income > 50000 else 70
        
        # Combined risk score
        overall_score = (climate_score + market_risk) / 2
        
        if overall_score >= 70: return "High Risk (C-D)"
        elif overall_score >= 40: return "Moderate Risk (B)"
        else: return "Low Risk (A)"
    
    def _determine_investment_risk_level(self, climate_risks: Dict, demographics: Dict) -> str:
        """Determine investment risk level"""
        climate_level = climate_risks.get("climate_risks", {}).get("overall_climate_risk", {}).get("level", "Moderate")
        income_cat = demographics.get("economics", {}).get("income_category", "Middle Income")
        
        if climate_level == "High" or "Lower" in income_cat:
            return "Higher Risk Investment"
        elif climate_level == "Moderate" and "Middle" in income_cat:
            return "Moderate Risk Investment"
        else:
            return "Lower Risk Investment"
    
    def _assess_economic_volatility(self, demographics: Dict) -> Dict[str, Any]:
        """Assess economic volatility risk"""
        income = demographics.get("economics", {}).get("median_household_income", 0)
        education = demographics.get("education", {}).get("bachelor_plus_rate", 0)
        
        if income > 75000 and education > 40:
            return {"score": 20, "level": "Low", "description": "Stable, educated workforce"}
        elif income > 50000 and education > 25:
            return {"score": 35, "level": "Moderate", "description": "Generally stable economy"}
        else:
            return {"score": 55, "level": "Higher", "description": "Economic volatility possible"}
    
    def _assess_market_liquidity(self, demographics: Dict) -> Dict[str, Any]:
        """Assess market liquidity risk"""
        population = demographics.get("population", {}).get("total", 0)
        density = demographics.get("population", {}).get("density_category", "")
        
        if population > 100000 and "Urban" in density:
            return {"score": 15, "level": "Low", "description": "High liquidity market"}
        elif population > 50000:
            return {"score": 30, "level": "Moderate", "description": "Moderate liquidity"}
        else:
            return {"score": 50, "level": "Higher", "description": "Limited market liquidity"}
    
    def _assess_demographic_stability(self, demographics: Dict) -> Dict[str, Any]:
        """Assess demographic stability"""
        education = demographics.get("education", {}).get("bachelor_plus_rate", 0)
        homeownership = demographics.get("housing", {}).get("homeownership_rate", 0)
        
        if education > 35 and homeownership > 60:
            return {"score": 18, "level": "Low", "description": "Stable, educated community"}
        elif education > 25 and homeownership > 50:
            return {"score": 32, "level": "Moderate", "description": "Generally stable demographics"}
        else:
            return {"score": 48, "level": "Higher", "description": "Demographic changes possible"}
    
    def _assess_tax_risk(self, demographics: Dict) -> Dict[str, Any]:
        """Assess property tax risk"""
        home_value = demographics.get("housing", {}).get("median_home_value", 0)
        
        if home_value > 500000:
            return {"score": 45, "level": "Higher", "description": "High-value area, tax increase risk"}
        elif home_value > 300000:
            return {"score": 30, "level": "Moderate", "description": "Moderate tax risk"}
        else:
            return {"score": 20, "level": "Low", "description": "Lower tax burden area"}
    
    def _assess_maintenance_risk(self, climate_risks: Dict) -> Dict[str, Any]:
        """Assess maintenance cost risk based on climate"""
        climate_score = climate_risks.get("climate_risks", {}).get("overall_climate_risk", {}).get("score", 25)
        
        if climate_score > 50:
            return {"score": 45, "level": "Higher", "description": "Climate-related maintenance costs"}
        elif climate_score > 30:
            return {"score": 30, "level": "Moderate", "description": "Standard maintenance expected"}
        else:
            return {"score": 20, "level": "Low", "description": "Favorable climate conditions"}
    
    def _assess_insurance_risk(self, climate_risks: Dict) -> Dict[str, Any]:
        """Assess insurance cost risk"""
        flood_score = climate_risks.get("climate_risks", {}).get("flood_risk", {}).get("score", 25)
        
        if flood_score > 40:
            return {"score": 50, "level": "Higher", "description": "Flood insurance may be required"}
        elif flood_score > 25:
            return {"score": 30, "level": "Moderate", "description": "Standard insurance rates"}
        else:
            return {"score": 20, "level": "Low", "description": "Lower insurance risk area"}
    
    def _generate_mitigation_strategies(self, climate_risks: Dict, demographics: Dict) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = []
        
        # Climate-based strategies
        climate_recommendations = climate_risks.get("recommendations", [])
        strategies.extend(climate_recommendations)
        
        # Market-based strategies
        income_cat = demographics.get("economics", {}).get("income_category", "")
        if "Lower" in income_cat:
            strategies.append("💰 Consider long-term financing options")
            strategies.append("📊 Monitor local economic development")
        
        # Location-based strategies
        population = demographics.get("population", {}).get("total", 0)
        if population < 50000:
            strategies.append("🏘️ Diversify within broader regional market")
        
        return strategies

# Enhanced PropertyAnalysisCrew with real data integration
class PropertyAnalysisCrew:
    def __init__(self):
        # Initialize tools with real data sources
        self.property_tool = PropertyResearchTool()
        self.market_tool = MarketAnalysisTool()
        self.risk_tool = RiskAssessmentTool()
        
        # Define agents (same as before but now using real data)
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
        """Create enhanced analysis tasks using real data"""
        
        # Task 1: Property Research with Real Data
        research_task = Task(
            description=f"""
            Conduct comprehensive property research for: {property_address}
            
            Use real data sources to gather:
            1. Precise geocoding and address verification using Google Maps API
            2. Neighborhood walkability, transit, and lifestyle scores from OpenStreetMap
            3. Demographic analysis using US Census Bureau data including:
               - Population characteristics and density
               - Median household income and economic indicators
               - Education levels and employment data
               - Housing market characteristics
            4. Nearby amenities analysis including restaurants, schools, healthcare, shopping
            5. Location highlights and area characteristics
            
            Provide detailed, factual information with data sources clearly identified.
            Focus on accuracy using real-world data rather than estimates.
            """,
            agent=self.property_researcher,
            expected_output="Comprehensive property research report with verified real data from multiple sources"
        )
        
        # Task 2: Market Analysis with Real Demographics
        market_task = Task(
            description=f"""
            Analyze the real estate market conditions using actual demographic and economic data.
            Use the property research findings as context for your analysis.
            
            Your analysis should include:
            1. Market strength assessment based on real income and education data
            2. Housing market analysis using actual median home values and rental rates
            3. Investment indicators derived from real demographic trends
            4. Market positioning based on actual economic characteristics
            5. Growth forecasts using population and economic data
            6. Appreciation potential based on area education and income levels
            
            Base all analysis on real data from Census Bureau and other verified sources.
            Provide specific numbers and trends rather than general estimates.
            """,
            agent=self.market_analyst,
            expected_output="Market analysis report based on real demographic and economic data with specific metrics",
            context=[research_task]
        )
        
        # Task 3: Risk Assessment with Real Environmental Data
        risk_task = Task(
            description=f"""
            Conduct comprehensive risk assessment using real environmental and market data.
            Consider both the property research and market analysis findings.
            
            Use real data sources to evaluate:
            1. Environmental risks using actual climate data and weather patterns
            2. Flood risk assessment based on geographic location
            3. Market risks using real demographic stability indicators
            4. Economic volatility based on actual income and employment data
            5. Insurance and maintenance risks based on climate conditions
            
            Provide specific risk scores and practical mitigation strategies based on real data.
            Calculate overall risk grades using factual information rather than estimates.
            """,
            agent=self.risk_assessor,
            expected_output="Risk assessment with specific scores and mitigation strategies based on real environmental and market data",
            context=[research_task, market_task]
        )
        
        # Task 4: Executive Report with Real Data Synthesis
        report_task = Task(
            description=f"""
            Create a comprehensive executive investment report for: {property_address}
            
            Synthesize all real data findings into a professional report with:
            
            1. **Executive Summary** (3-4 key insights and clear recommendation)
            2. **Property Intelligence** (real data from Google Maps, OpenStreetMap, Census)
            3. **Market Analysis** (actual demographics, income, education, housing data)
            4. **Risk Assessment** (real environmental and market risk scores)
            5. **Investment Recommendation** (Buy/Hold/Pass with specific rationale)
            6. **Action Items** (next steps based on real data insights)
            
            Base all recommendations on the actual data collected from verified sources.
            Include specific numbers, percentages, and data points throughout.
            Make the report professional and suitable for executive decision-making.
            """,
            agent=self.report_generator,
            expected_output="Executive-level property investment report with clear recommendations based on comprehensive real data analysis",
            context=[research_task, market_task, risk_task]
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
