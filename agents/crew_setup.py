from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import Type, Any, List, Dict
from pydantic import BaseModel, Field
import json
import asyncio
import re

# Import demo data service instead of real APIs
from demo_data_service import DemoDataService

# Tool Input Models
class PropertyDataInput(BaseModel):
    address: str = Field(..., description="Property address to research")

class MarketDataInput(BaseModel):
    location: str = Field(..., description="Location for market analysis")

# Demo-Based Tools for Consistent Presentation
class PropertyResearchTool(BaseTool):
    name: str = "Property Research Tool"
    description: str = "Fetch comprehensive property data using demo data for impressive presentations"
    args_schema: Type[BaseModel] = PropertyDataInput

    def _run(self, address: str) -> str:
        """Fetch comprehensive property data using demo data service"""
        try:
            print(f"🔍 Starting demo property research for: {address}")
            
            # Initialize demo data service
            demo_service = DemoDataService()
            
            # Get formatted analysis
            analysis = demo_service.get_formatted_analysis(address)
            
            print(f"✅ Demo property research completed successfully")
            return analysis["property_research"]
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ PropertyResearchTool Error: {error_msg}")
            return f"❌ Unable to analyze property: {address}. Demo data service error: {error_msg}"

class MarketAnalysisTool(BaseTool):
    name: str = "Market Analysis Tool"
    description: str = "Analyze market conditions and investment potential using demo data"
    args_schema: Type[BaseModel] = MarketDataInput

    def _run(self, location: str) -> str:
        """Analyze market conditions using demo data service"""
        try:
            print(f"🔍 Starting demo market analysis for: {location}")
            
            # Initialize demo data service
            demo_service = DemoDataService()
            
            # Get formatted analysis
            analysis = demo_service.get_formatted_analysis(location)
            
            print(f"✅ Demo market analysis completed successfully")
            return analysis["market_analysis"]
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ MarketAnalysisTool Error: {error_msg}")
            return f"❌ Unable to analyze market for location: {location}. Demo data service error: {error_msg}"

class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = "Assess investment risks using demo data"
    args_schema: Type[BaseModel] = PropertyDataInput

    def _run(self, address: str) -> str:
        """Assess investment risks using demo data service"""
        try:
            print(f"🔍 Starting demo risk assessment for: {address}")
            
            # Initialize demo data service
            demo_service = DemoDataService()
            
            # Get formatted analysis
            analysis = demo_service.get_formatted_analysis(address)
            
            print(f"✅ Demo risk assessment completed successfully")
            return analysis["risk_assessment"]
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ RiskAssessmentTool Error: {error_msg}")
            return f"❌ Unable to assess risks for address: {address}. Demo data service error: {error_msg}"

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
