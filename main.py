from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import os
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

load_dotenv()

app = FastAPI(
    title="Property Intelligence AI Platform",
    description="Agentic AI-powered real estate analysis with RAG and Vector Database",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class PropertyAnalysisRequest(BaseModel):
    address: str
    additional_context: Optional[str] = ""

class PropertyAnalysisResponse(BaseModel):
    session_id: str
    status: str
    message: str
    agents: Dict[str, Any]

@app.get("/")
async def root():
    return HTMLResponse(f"""
    <html>
        <head>
            <title>Property Intelligence AI Platform v2.0</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                .container {{ max-width: 900px; margin: 0 auto; text-align: center; }}
                .btn {{ background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }}
                .btn:hover {{ background: #218838; }}
                .feature-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
                .feature-card {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; }}
                .status {{ background: {'rgba(40,167,69,0.2)' if RAG_ENABLED else 'rgba(220,53,69,0.2)'}; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏠 Property Intelligence AI Platform v2.0</h1>
                <p>Advanced Agentic AI with RAG + Vector Database Integration</p>
                
                <div class="status">
                    <strong>🤖 AI Services Status:</strong><br>
                    RAG + Vector Database: {'✅ Active' if RAG_ENABLED else '❌ Disabled'}<br>
                    Real-time Agent Tracking: {'✅ Active' if agent_tracker else '❌ Disabled'}<br>
                    OpenAI Integration: {'✅ Ready' if os.getenv('OPENAI_API_KEY') else '⚠️ API Key Required'}
                </div>
                
                <h2>🚀 Available Services</h2>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>📚 API Documentation</h3>
                        <a href="/docs" class="btn">View API Docs</a>
                    </div>
                    <div class="feature-card">
                        <h3>💚 Health Check</h3>
                        <a href="/health" class="btn">Check Status</a>
                    </div>
                    <div class="feature-card">
                        <h3>🔍 Vector Search</h3>
                        <a href="/search-similar?query=luxury+condo" class="btn">Demo Search</a>
                    </div>
                    <div class="feature-card">
                        <h3>📊 Agent Status</h3>
                        <a href="/agents/status" class="btn">View Agents</a>
                    </div>
                </div>
                
                <h2>🤖 AI Agents</h2>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>🔍 Property Researcher</h3>
                        <p>Gathers property data and comparable listings</p>
                    </div>
                    <div class="feature-card">
                        <h3>📊 Market Analyst</h3>
                        <p>Analyzes market trends and pricing with RAG</p>
                    </div>
                    <div class="feature-card">
                        <h3>⚠️ Risk Assessor</h3>
                        <p>Evaluates investment risks using vector database</p>
                    </div>
                    <div class="feature-card">
                        <h3>📝 Report Generator</h3>
                        <p>Compiles AI-powered comprehensive analysis</p>
                    </div>
                </div>
                
                <p><strong>🎯 Enhanced for JLL Demo with RAG + Vector Database!</strong></p>
                <p><em>Use the Streamlit frontend for full interactive experience</em></p>
            </div>
        </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "2.0.0",
        "features": {
            "rag_enabled": RAG_ENABLED,
            "agent_tracking": agent_tracker is not None,
            "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
        },
        "agents": "ready",
        "message": "Property Intelligence AI Platform v2.0 is running!"
    }

@app.post("/analyze-property")
async def analyze_property(
    request: PropertyAnalysisRequest,
    background_tasks: BackgroundTasks
) -> PropertyAnalysisResponse:
    """Start comprehensive property analysis with real-time agent tracking"""
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    if not agent_tracker:
        # Fallback response if agent tracking is disabled
        return PropertyAnalysisResponse(
            session_id=session_id,
            status="started",
            message=f"Basic analysis started for {request.address}",
            agents={}
        )
    
    # Start analysis session
    response = agent_tracker.start_analysis(session_id, request.address)
    
    # Run the analysis in the background
    background_tasks.add_task(
        agent_tracker.simulate_property_analysis,
        session_id,
        request.address
    )
    
    # Add property data to RAG if enabled
    if RAG_ENABLED and rag_service:
        try:
            background_tasks.add_task(
                rag_service.add_property_data,
                {
                    "address": request.address,
                    "session_id": session_id,
                    "analysis_start": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"RAG service error: {e}")
    
    return PropertyAnalysisResponse(
        session_id=session_id,
        status="started",
        message=f"Advanced AI analysis started for {request.address}",
        agents=response.get("agents", {})
    )

@app.get("/agents/status")
async def get_agent_status():
    """Get current status of all AI agents"""
    if not agent_tracker:
        return {"error": "Agent tracking not available"}
    
    return {
        "timestamp": datetime.now().isoformat(),
        "agents": agent_tracker.get_agent_status()
    }

@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific analysis session"""
    if not agent_tracker:
        return {"error": "Agent tracking not available"}
    
    return agent_tracker.get_session_info(session_id)

@app.get("/results/{session_id}")
async def get_analysis_results(session_id: str):
    """Get final analysis results for a session"""
    if not agent_tracker:
        return {"error": "Agent tracking not available"}
    
    results = agent_tracker.get_analysis_results(session_id)
    
    # Enhance with RAG insights if available
    if RAG_ENABLED and rag_service and results.get("analysis_complete"):
        try:
            property_address = results.get("property_address", "")
            rag_insights = await rag_service.generate_property_insights(property_address)
            results["rag_insights"] = rag_insights
        except Exception as e:
            print(f"RAG insights error: {e}")
            results["rag_insights"] = {"error": str(e)}
    
    return results

@app.get("/search-similar")
async def search_similar_properties(query: str, limit: int = 5):
    """Search for similar properties using vector similarity"""
    if not RAG_ENABLED or not rag_service:
        return {
            "error": "RAG service not available",
            "fallback_data": {
                "query": query,
                "message": "Vector search requires RAG service to be enabled"
            }
        }
    
    try:
        results = await rag_service.search_similar_properties(query, limit)
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

# Legacy endpoint for backward compatibility
@app.get("/demo")
async def demo_results():
    """Demo results endpoint - enhanced with RAG insights"""
    base_results = {
        "property_analysis": {
            "estimated_value": 450000,
            "risk_score": 23,
            "investment_grade": "B+",
            "market_trend": "Rising (+5.2%)",
            "ai_insights": [
                "🎯 Property shows strong investment potential",
                "📈 Local market trending upward",
                "🏫 Excellent school district ratings",
                "🚊 Good transportation accessibility"
            ]
        },
        "agents_used": [
            "Property Researcher", 
            "Market Analyst",
            "Risk Assessor", 
            "Report Generator"
        ],
        "processing_time": "2.3 minutes",
        "version": "2.0.0",
        "features_used": {
            "rag_enabled": RAG_ENABLED,
            "vector_search": RAG_ENABLED,
            "real_time_tracking": agent_tracker is not None
        }
    }
    
    return base_results

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
