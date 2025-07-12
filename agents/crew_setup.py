from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
from typing import Type, Any, List
from pydantic import BaseModel, Field
import json
import asyncio

# Tool Input Models
class PropertyDataInput(BaseModel):
    address: str = Field(..., description="Property address to research")

class MarketDataInput(BaseModel):
    location: str = Field(..., description="Location for market analysis")

# Custom Tools for Agents
class PropertyResearchTool(BaseTool):
    name: str = "Property Research Tool"
    description: str = "Fetch comprehensive property data including value, details, and history"
    args_schema: Type[BaseModel] = PropertyDataInput

    def _run(self, address: str) -> str:
        """Simulate property data research"""
        # In production, this would call real APIs
        mock_data = {
            "address": address,
            "estimated_value": 450000,
            "bedrooms": 3,
            "bathrooms": 2.5,
            "square_feet": 1850,
            "year_built": 2005,
            "property_type": "Single Family",
            "lot_size": "0.25 acres",
            "price_history": [
                {"date": "2023-08-15", "price": 425000, "event": "Sold"},
                {"date": "2021-05-10", "price": 380000, "event": "Sold"}
            ],
            "tax_assessment": 415000,
            "school_district": "Excellent (9/10)",
            "crime_rate": "Low",
            "walkability_score": 85
        }
        return f"Property Research Results for {address}:\n{json.dumps(mock_data, indent=2)}"

class MarketAnalysisTool(BaseTool):
    name: str = "Market Analysis Tool"
    description: str = "Analyze local market conditions and trends"
    args_schema: Type[BaseModel] = MarketDataInput

    def _run(self, location: str) -> str:
        """Simulate market analysis"""
        mock_data = {
            "location": location,
            "market_trend": "Rising",
            "price_change_1yr": 5.2,
            "price_change_3yr": 18.7,
            "median_home_value": 425000,
            "days_on_market": 18,
            "inventory_level": "Low (2.1 months)",
            "price_per_sqft": 243,
            "comparable_sales": [
                {"address": "125 Main St", "price": 465000, "sqft": 1920, "date": "2024-01-15"},
                {"address": "119 Main St", "price": 435000, "sqft": 1780, "date": "2024-01-08"}
            ],
            "market_temperature": "Hot",
            "appreciation_forecast": "6-8% annual"
        }
        return f"Market Analysis for {location}:\n{json.dumps(mock_data, indent=2)}"

class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = "Evaluate investment and environmental risks"
    args_schema: Type[BaseModel] = PropertyDataInput

    def _run(self, address: str) -> str:
        """Simulate risk assessment"""
        mock_data = {
            "overall_risk_score": 23,
            "risk_grade": "Low",
            "environmental_risks": {
                "flood_risk": "Low (15/100)",
                "earthquake_risk": "Low (10/100)",
                "wildfire_risk": "Very Low (5/100)",
                "climate_change_impact": "Moderate (35/100)"
            },
            "market_risks": {
                "interest_rate_sensitivity": "Medium (40/100)",
                "market_volatility": "Low (25/100)",
                "liquidity_risk": "Low (20/100)"
            },
            "financial_risks": {
                "tax_increase_risk": "Low (18/100)",
                "maintenance_costs": "Standard (30/100)",
                "insurance_costs": "Low (15/100)"
            },
            "mitigation_strategies": [
                "Consider flood insurance for added protection",
                "Monitor local tax policy changes",
                "Regular maintenance schedule recommended"
            ]
        }
        return f"Risk Assessment for {address}:\n{json.dumps(mock_data, indent=2)}"

class PropertyAnalysisCrew:
    def __init__(self):
        # Initialize tools
        self.property_tool = PropertyResearchTool()
        self.market_tool = MarketAnalysisTool()
        self.risk_tool = RiskAssessmentTool()
        
        # Define agents
        self.property_researcher = Agent(
            role="Senior Property Research Specialist",
            goal="Gather comprehensive and accurate property data from multiple sources",
            backstory="""You are an expert property researcher with 15+ years of experience 
            in real estate analysis. You have deep knowledge of property databases, 
            public records, and market data sources. You're meticulous about data accuracy 
            and always verify information from multiple sources. You provide detailed, 
            factual information with clear explanations.""",
            tools=[self.property_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        self.market_analyst = Agent(
            role="Real Estate Market Intelligence Analyst",
            goal="Analyze market conditions, trends, and provide investment insights",
            backstory="""You are a senior market analyst with expertise in real estate 
            economics and investment analysis. You have an MBA in Finance and 12+ years 
            of experience analyzing property markets. You excel at identifying trends, 
            comparable properties, and investment opportunities. You provide actionable 
            insights based on data-driven analysis.""",
            tools=[self.market_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        self.risk_assessor = Agent(
            role="Risk Management Specialist",
            goal="Identify and quantify risks associated with property investments",
            backstory="""You are a risk management expert with extensive experience in 
            real estate risk assessment. You hold certifications in risk management and 
            have worked with major real estate investment firms. You're skilled at 
            identifying environmental, financial, and market risks. You provide clear 
            risk scores and practical mitigation strategies.""",
            tools=[self.risk_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        self.report_generator = Agent(
            role="Executive Investment Report Writer",
            goal="Create comprehensive, professional reports for real estate investment decisions",
            backstory="""You are an expert business writer and consultant specializing 
            in real estate investment reports. You have a talent for synthesizing complex 
            data into clear, actionable insights. Your reports are used by executives, 
            investors, and real estate professionals to make informed decisions. You 
            create executive-level summaries with specific recommendations.""",
            tools=[],  # No tools needed - synthesizes information from other agents
            verbose=True,
            allow_delegation=False,
            max_iter=2
        )

    def create_analysis_tasks(self, property_address: str) -> List[Task]:
        """Create the sequence of tasks for property analysis"""
        
        # Task 1: Property Research
        research_task = Task(
            description=f"""
            Conduct comprehensive property research for: {property_address}
            
            Your research should include:
            1. Basic property details (size, bedrooms, bathrooms, year built, lot size)
            2. Current estimated market value and recent price history
            3. Property type, condition, and unique features
            4. Tax assessment information and property taxes
            5. Neighborhood characteristics and school district quality
            6. Local amenities and accessibility scores
            
            Provide detailed, factual information with clear data points.
            Focus on accuracy and completeness of the property profile.
            """,
            agent=self.property_researcher,
            expected_output="Comprehensive property research report with verified data and property specifications"
        )
        
        # Task 2: Market Analysis
        market_task = Task(
            description=f"""
            Analyze the real estate market conditions for the property location.
            Use the property research findings as context for your analysis.
            
            Your analysis should cover:
            1. Local market trends and recent price movements
            2. Comparable property sales and pricing analysis
            3. Market inventory levels and days on market statistics
            4. Economic indicators affecting the local area
            5. Price appreciation forecasts and market outlook
            6. Investment potential and market timing considerations
            
            Provide data-driven insights with specific numbers and trends.
            """,
            agent=self.market_analyst,
            expected_output="Market analysis report with trends, comparables, and investment outlook",
            context=[research_task]
        )
        
        # Task 3: Risk Assessment
        risk_task = Task(
            description=f"""
            Conduct a comprehensive risk assessment for this property investment.
            Consider both the property research and market analysis findings.
            
            Evaluate and score these risk categories:
            1. Environmental risks (flooding, natural disasters, climate change)
            2. Market risks (volatility, liquidity, interest rate sensitivity)
            3. Financial risks (taxes, maintenance, insurance costs)
            4. Location-specific risks (crime, economic changes)
            
            Provide specific risk scores (0-100 scale) and practical mitigation strategies.
            Calculate an overall risk score and grade (A-F scale).
            """,
            agent=self.risk_assessor,
            expected_output="Risk assessment with specific scores, grades, and mitigation strategies",
            context=[research_task, market_task]
        )
        
        # Task 4: Executive Report
        report_task = Task(
            description=f"""
            Create a comprehensive executive investment report for: {property_address}
            
            Synthesize all findings from the property research, market analysis, and risk assessment into a professional report with:
            
            1. **Executive Summary** (2-3 key insights and recommendation)
            2. **Property Overview** (key specifications and features)
            3. **Market Analysis Summary** (trends, outlook, comparables)
            4. **Risk Assessment Summary** (overall score and key risks)
            5. **Investment Recommendation** (Buy/Hold/Pass with rationale)
            6. **Key Action Items** (next steps for potential investors)
            
            Make the report professional, actionable, and suitable for executive decision-making.
            Include specific numbers, scores, and clear recommendations.
            """,
            agent=self.report_generator,
            expected_output="Executive-level property investment report with clear recommendations and action items",
            context=[research_task, market_task, risk_task]
        )
        
        return [research_task, market_task, risk_task, report_task]

    async def analyze_property(self, property_address: str) -> dict:
        """Execute the complete property analysis workflow"""
        
        print(f"🚀 Starting AI agent analysis for: {property_address}")
        
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
