import asyncio
import json
import time
from typing import Dict, List, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

class PropertyAgent:
    def __init__(self, name: str, icon: str, description: str):
        self.name = name
        self.icon = icon
        self.description = description
        self.status = AgentStatus.IDLE
        self.progress = 0
        self.current_task = ""
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.logs = []
    
    def start_task(self, task: str):
        self.status = AgentStatus.RUNNING
        self.current_task = task
        self.progress = 0
        self.start_time = datetime.now()
        self.logs.append(f"Started: {task}")
    
    def update_progress(self, progress: int, message: str = ""):
        self.progress = min(100, max(0, progress))
        if message:
            self.logs.append(f"Progress {progress}%: {message}")
    
    def complete_task(self, results: Dict[str, Any]):
        self.status = AgentStatus.COMPLETED
        self.progress = 100
        self.end_time = datetime.now()
        self.results = results
        self.logs.append("Task completed successfully")
    
    def error_task(self, error: str):
        self.status = AgentStatus.ERROR
        self.logs.append(f"Error: {error}")
    
    def reset(self):
        self.status = AgentStatus.IDLE
        self.progress = 0
        self.current_task = ""
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.logs = []

class AgentTracker:
    def __init__(self):
        self.agents = {
            "researcher": PropertyAgent(
                name="🔍 Property Researcher",
                icon="🔍",
                description="Gathers property data and comparable listings"
            ),
            "market_analyst": PropertyAgent(
                name="📊 Market Analyst",
                icon="📊", 
                description="Analyzes market trends and pricing"
            ),
            "risk_assessor": PropertyAgent(
                name="⚠️ Risk Assessor",
                icon="⚠️",
                description="Evaluates investment risks and factors"
            ),
            "report_generator": PropertyAgent(
                name="📝 Report Generator",
                icon="📝",
                description="Compiles comprehensive analysis report"
            )
        }
        self.active_sessions = {}
    
    def start_analysis(self, session_id: str, property_address: str) -> Dict[str, Any]:
        """Start a new property analysis session"""
        # Reset all agents
        for agent in self.agents.values():
            agent.reset()
        
        # Store session info
        self.active_sessions[session_id] = {
            "property_address": property_address,
            "start_time": datetime.now(),
            "status": "running"
        }
        
        return {
            "session_id": session_id,
            "status": "started",
            "agents": self.get_agent_status(),
            "message": f"Analysis started for {property_address}"
        }
    
    async def simulate_property_analysis(self, session_id: str, property_address: str):
        """Simulate the property analysis workflow with realistic timing"""
        try:
            # Phase 1: Property Research
            researcher = self.agents["researcher"]
            researcher.start_task("Gathering property data and comparables")
            
            await asyncio.sleep(0.5)
            researcher.update_progress(25, "Searching property databases")
            
            await asyncio.sleep(0.3)
            researcher.update_progress(50, "Found 12 comparable properties")
            
            await asyncio.sleep(0.4)
            researcher.update_progress(75, "Analyzing property features")
            
            await asyncio.sleep(0.3)
            researcher.update_progress(100, "Property research complete")
            researcher.complete_task({
                "property_type": "Single Family Home",
                "bedrooms": 4,
                "bathrooms": 2.5,
                "square_feet": 2100,
                "lot_size": 0.25,
                "year_built": 2018,
                "comparables_found": 12
            })
            
            # Phase 2: Market Analysis
            market_analyst = self.agents["market_analyst"]
            market_analyst.start_task("Analyzing market trends and pricing")
            
            await asyncio.sleep(0.4)
            market_analyst.update_progress(30, "Analyzing recent sales data")
            
            await asyncio.sleep(0.3)
            market_analyst.update_progress(60, "Calculating market trends")
            
            await asyncio.sleep(0.3)
            market_analyst.update_progress(90, "Generating price estimates")
            
            await asyncio.sleep(0.2)
            market_analyst.complete_task({
                "estimated_value": 450000,
                "market_trend": "Rising (+5.2%)",
                "price_per_sqft": 214,
                "days_on_market_avg": 28,
                "appreciation_rate": 6.8
            })
            
            # Phase 3: Risk Assessment
            risk_assessor = self.agents["risk_assessor"]
            risk_assessor.start_task("Evaluating investment risks")
            
            await asyncio.sleep(0.3)
            risk_assessor.update_progress(40, "Checking flood zones and climate data")
            
            await asyncio.sleep(0.3)
            risk_assessor.update_progress(70, "Analyzing market volatility")
            
            await asyncio.sleep(0.2)
            risk_assessor.update_progress(100, "Risk assessment complete")
            risk_assessor.complete_task({
                "risk_score": 23,
                "risk_level": "Low",
                "flood_risk": "Minimal",
                "market_volatility": "Low",
                "investment_grade": "B+"
            })
            
            # Phase 4: Report Generation
            report_generator = self.agents["report_generator"]
            report_generator.start_task("Compiling comprehensive analysis")
            
            await asyncio.sleep(0.2)
            report_generator.update_progress(50, "Generating insights and recommendations")
            
            await asyncio.sleep(0.3)
            report_generator.update_progress(100, "Report generation complete")
            report_generator.complete_task({
                "report_id": f"RPT-{session_id[:8]}",
                "insights": [
                    "🎯 Strong investment potential with growing market",
                    "📈 Property value trending upward (+5.2% annually)",
                    "🏫 Excellent school district supports long-term value",
                    "🚊 Good transportation access increases demand"
                ],
                "recommendations": [
                    "Consider making competitive offer",
                    "Negotiate based on recent comparable sales",
                    "Property shows good rental potential if investment property"
                ]
            })
            
            # Mark session as complete
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["status"] = "completed"
                self.active_sessions[session_id]["end_time"] = datetime.now()
                
        except Exception as e:
            logger.error(f"Error in property analysis simulation: {e}")
            # Mark all running agents as error
            for agent in self.agents.values():
                if agent.status == AgentStatus.RUNNING:
                    agent.error_task(str(e))
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all agents"""
        status = {}
        for agent_id, agent in self.agents.items():
            status[agent_id] = {
                "name": agent.name,
                "icon": agent.icon,
                "description": agent.description,
                "status": agent.status.value,
                "progress": agent.progress,
                "current_task": agent.current_task,
                "results": agent.results,
                "logs": agent.logs[-5:] if agent.logs else []  # Last 5 logs
            }
        return status
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a specific session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        return {
            "session_id": session_id,
            "property_address": session["property_address"],
            "start_time": session["start_time"].isoformat(),
            "end_time": session.get("end_time", {}).isoformat() if session.get("end_time") else None,
            "status": session["status"],
            "agents": self.get_agent_status()
        }
    
    def get_analysis_results(self, session_id: str) -> Dict[str, Any]:
        """Get final analysis results for a session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        # Compile results from all agents
        results = {
            "session_id": session_id,
            "property_address": self.active_sessions[session_id]["property_address"],
            "analysis_complete": all(agent.status == AgentStatus.COMPLETED for agent in self.agents.values()),
            "results": {}
        }
        
        for agent_id, agent in self.agents.items():
            if agent.status == AgentStatus.COMPLETED:
                results["results"][agent_id] = agent.results
        
        return results

# Global agent tracker instance
agent_tracker = AgentTracker()