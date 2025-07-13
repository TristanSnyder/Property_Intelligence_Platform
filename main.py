from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import our custom services
try:
    from rag_service import rag_service
    from agent_tracker import agent_tracker
    RAG_ENABLED = True
except ImportError as e:
    print(f"RAG services not available: {e}")
    RAG_ENABLED = False
    rag_service = None
    agent_tracker = None

# Import our agentic AI
try:
    from agents.crew_setup import property_analysis_crew
    CREW_ENABLED = True
except ImportError as e:
    print(f"CrewAI not available: {e}")
    CREW_ENABLED = False
    property_analysis_crew = None

load_dotenv()

# Request/Response Models
class PropertyAnalysisRequest(BaseModel):
    address: str
    analysis_type: str = "comprehensive"
    additional_context: Optional[str] = ""

class PropertyAnalysisResponse(BaseModel):
    analysis_id: str
    address: str
    status: str
    created_at: str
    agents_deployed: list

# FastAPI app
app = FastAPI(
    title="Property Intelligence AI Platform",
    description="Agentic AI-powered real estate analysis with RAG and Vector Database",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
async def api_status():
    """API status endpoint"""
    return {
        "message": "Property Intelligence AI Platform",
        "version": "2.0.0",
        "status": "running",
        "features": {
            "rag_enabled": RAG_ENABLED,
            "crew_enabled": CREW_ENABLED
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/analyze-property")
async def analyze_property(request: PropertyAnalysisRequest):
    """Analyze a property using AI agents"""
    analysis_id = str(uuid.uuid4())
    
    try:
        if CREW_ENABLED and property_analysis_crew:
            # Use CrewAI for analysis
            result = await property_analysis_crew.analyze(request.address)
            agents_used = ["Property Researcher", "Market Analyst", "Risk Assessor", "Report Generator"]
        else:
            # Fallback mock analysis
            result = {
                "estimated_value": 450000,
                "risk_score": 23,
                "investment_grade": "B+",
                "market_trend": "Rising (+5.2%)"
            }
            agents_used = ["Mock Agent"]
        
        return PropertyAnalysisResponse(
            analysis_id=analysis_id,
            address=request.address,
            status="completed",
            created_at=datetime.now().isoformat(),
            agents_deployed=agents_used
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-properties")
async def search_properties(query: str = ""):
    """Search properties using RAG"""
    if not RAG_ENABLED or not rag_service:
        return {
            "error": "RAG service not available",
            "fallback_data": {
                "query": query,
                "message": "Property search requires RAG service"
            }
        }
    
    try:
        results = await rag_service.search_properties(query)
        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "query": query}

@app.get("/market-trends")
async def get_market_trends(location: str = ""):
    """Get market trends for a specific location using RAG"""
    if not RAG_ENABLED or not rag_service:
        return {
            "error": "RAG service not available",
            "fallback_data": {
                "location": location,
                "message": "Market trends analysis requires RAG service"
            }
        }
    
    try:
        trends = await rag_service.get_market_trends(location)
        return trends
    except Exception as e:
        return {"error": str(e), "location": location}

@app.post("/add-property-data")
async def add_property_data(property_data: Dict[str, Any]):
    """Add property data to the vector database"""
    if not RAG_ENABLED or not rag_service:
        return {"error": "RAG service not available"}
    
    try:
        await rag_service.add_property_data(property_data)
        return {
            "status": "success",
            "message": "Property data added to vector database",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/demo")
async def demo_results():
    """Demo showing completed AI analysis"""
    return JSONResponse({
        "demo_analysis": {
            "analysis_id": "demo_12345",
            "address": "123 Main Street, New York, NY 10001", 
            "status": "completed",
            "ai_agents_results": {
                "property_researcher": {
                    "estimated_value": 450000,
                    "bedrooms": 3,
                    "bathrooms": 2.5,
                    "square_feet": 1850,
                    "year_built": 2005,
                    "lot_size": "0.25 acres",
                    "school_district": "Excellent (9/10)"
                },
                "market_analyst": {
                    "market_trend": "Rising (+5.2%)",
                    "days_on_market": 18,
                    "price_per_sqft": 243,
                    "comparables_found": 5,
                    "investment_outlook": "Positive"
                },
                "risk_assessor": {
                    "overall_risk_score": 23,
                    "risk_grade": "Low",
                    "environmental_risk": 15,
                    "market_risk": 35,
                    "financial_risk": 20
                },
                "report_generator": {
                    "investment_recommendation": "BUY",
                    "confidence_level": "High (94%)",
                    "key_insights": [
                        "🎯 Property undervalued by ~6% vs market",
                        "📈 Strong appreciation potential (6-8% annually)", 
                        "🏫 Top-tier school district adds value",
                        "⚠️ Monitor interest rate changes"
                    ]
                }
            },
            "processing_summary": {
                "total_agents": 4,
                "processing_time": "2.7 minutes",
                "data_sources": 12,
                "confidence_score": 94.7,
                "features_used": {
                    "rag_enabled": RAG_ENABLED,
                    "crew_enabled": CREW_ENABLED,
                    "vector_search": RAG_ENABLED,
                    "real_time_tracking": agent_tracker is not None
                }
            }
        }
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
