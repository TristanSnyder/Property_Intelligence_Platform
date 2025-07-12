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
=======
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import asyncio
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Import our agentic AI
from agents.crew_setup import property_analysis_crew


load_dotenv()

# Request/Response Models
class PropertyAnalysisRequest(BaseModel):
    address: str
    analysis_type: str = "comprehensive"

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
    description="Agentic AI-powered real estate analysis with multi-agent workflows",
    version="1.0.0"
)

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
                <h1>Property Intelligence AI Platform v2.0</h1>
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
=======
# In-memory storage for demo (replace with database in production)
analysis_results = {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Enhanced root page with agentic AI features"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Property Intelligence AI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                margin: 0; padding: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; min-height: 100vh;
            }
            .container { max-width: 1000px; margin: 0 auto; text-align: center; }
            .card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 20px 0; backdrop-filter: blur(10px); }
            .btn { 
                background: #28a745; color: white; padding: 15px 25px; 
                text-decoration: none; border-radius: 8px; margin: 10px; 
                display: inline-block; font-weight: bold; transition: all 0.3s;
            }
            .btn:hover { background: #218838; transform: translateY(-2px); }
            .btn-primary { background: #007bff; }
            .btn-primary:hover { background: #0056b3; }
            .agent-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
            .agent-card { background: rgba(255,255,255,0.15); padding: 20px; border-radius: 10px; }
            .status { color: #90EE90; font-size: 18px; margin: 20px 0; }
            .demo-form { background: rgba(0,0,0,0.2); padding: 25px; border-radius: 12px; margin: 20px 0; }
            input { padding: 12px; border: none; border-radius: 6px; width: 300px; margin: 10px; }
            button { padding: 12px 25px; background: #ff6b35; color: white; border: none; border-radius: 6px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Property Intelligence AI Platform</h1>
            <div class="status">🤖 Agentic AI System - Fully Operational</div>
            
            <div class="card">
                <h2>🚀 Multi-Agent AI Analysis</h2>
                <div class="agent-grid">
                    <div class="agent-card">
                        <h3>🔍 Property Researcher</h3>
                        <p>Gathers comprehensive property data, valuations, and specifications</p>
                    </div>
                    <div class="agent-card">
                        <h3>📊 Market Analyst</h3>
                        <p>Analyzes trends, comparables, and market conditions</p>
                    </div>
                    <div class="agent-card">
                        <h3>⚠️ Risk Assessor</h3>
                        <p>Evaluates investment, environmental, and financial risks</p>
                    </div>
                    <div class="agent-card">
                        <h3>📝 Report Generator</h3>
                        <p>Creates executive-level investment reports</p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Live Demo - Try the AI Agents</h2>
                <div class="demo-form">
                    <h3>Analyze Any Property with AI</h3>
                    <input type="text" id="addressInput" placeholder="Enter property address (e.g., 123 Main St, New York, NY)" />
                    <br>
                    <button onclick="analyzeProperty()">🚀 Start AI Analysis</button>
                    <div id="result" style="margin-top: 20px;"></div>
                </div>
            </div>
            
            <div class="card">
                <h2>🔗 API Access</h2>
                <a href="/docs" class="btn btn-primary">📚 Interactive API Docs</a>
                <a href="/health" class="btn">💚 Health Check</a>
                <a href="/demo" class="btn">🎯 Demo Results</a>
            </div>
        </div>
        
        <script>
            async function analyzeProperty() {
                const address = document.getElementById('addressInput').value;
                const resultDiv = document.getElementById('result');
                
                if (!address) {
                    resultDiv.innerHTML = '<p style="color: #ff6b6b;">Please enter a property address</p>';
                    return;
                }
                
                resultDiv.innerHTML = '<p>🤖 AI Agents starting analysis...</p>';
                
                try {
                    const response = await fetch('/analyze-property-ai', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({address: address})
                    });
                    
                    const result = await response.json();
                    
                    if (result.analysis_id) {
                        resultDiv.innerHTML = `
                            <div style="background: rgba(40, 167, 69, 0.2); padding: 15px; border-radius: 8px;">
                                <h4>✅ Analysis Started!</h4>
                                <p><strong>Analysis ID:</strong> ${result.analysis_id}</p>
                                <p><strong>Status:</strong> ${result.status}</p>
                                <p><strong>Agents Deployed:</strong> ${result.agents_deployed.length}</p>
                                <a href="/analysis/${result.analysis_id}" class="btn">📊 View Results</a>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = '<p style="color: #ff6b6b;">Error starting analysis</p>';
                    }
                } catch (error) {
                    resultDiv.innerHTML = '<p style="color: #ff6b6b;">Error: ' + error.message + '</p>';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/analyze-property-ai", response_model=PropertyAnalysisResponse)
async def analyze_property_ai(
    request: PropertyAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Start AI agent property analysis"""
    analysis_id = str(uuid.uuid4())
    
    # Store initial analysis record
    analysis_results[analysis_id] = {
        "id": analysis_id,
        "address": request.address,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "agents_deployed": [
            "Property Research Specialist",
            "Market Intelligence Analyst", 
            "Risk Management Specialist",
            "Executive Report Writer"
        ],
        "result": None,
        "error": None
    }
    
    # Start background processing
    background_tasks.add_task(process_ai_analysis, analysis_id, request.address)
    
    return PropertyAnalysisResponse(
        analysis_id=analysis_id,
        address=request.address,
        status="processing",
        created_at=datetime.now().isoformat(),
        agents_deployed=analysis_results[analysis_id]["agents_deployed"]
    )

async def process_ai_analysis(analysis_id: str, address: str):
    """Background task to run AI agent analysis"""
    try:
        print(f"🤖 Starting AI analysis for {address}")
        
        # Run the agentic AI crew
        result = await property_analysis_crew.analyze_property(address)
        
        # Update results
        analysis_results[analysis_id].update({
            "status": "completed" if result["success"] else "error",
            "result": result,
            "completed_at": datetime.now().isoformat()
        })
        
        print(f"✅ AI analysis completed for {address}")
        
    except Exception as e:
        print(f"❌ AI analysis failed for {address}: {str(e)}")
        analysis_results[analysis_id].update({
            "status": "error",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })

@app.get("/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get analysis results by ID"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_results[analysis_id]
    
    if analysis["status"] == "processing":
        return JSONResponse({
            "analysis_id": analysis_id,
            "status": "processing",
            "message": "🤖 AI agents are still working on your analysis...",
            "agents_deployed": analysis["agents_deployed"],
            "created_at": analysis["created_at"]
        })
    
    return JSONResponse(analysis)

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
=======
    """Health check with AI agent status"""
    return JSONResponse({
        "status": "healthy",
        "service": "Property Intelligence AI Platform",
        "version": "1.0.0",
        "ai_agents": {
            "property_researcher": "✅ Ready",
            "market_analyst": "✅ Ready", 
            "risk_assessor": "✅ Ready",
            "report_generator": "✅ Ready"
        },
        "capabilities": [
            "Multi-agent property analysis",
            "Real-time market intelligence", 
            "Risk assessment and scoring",
            "Executive report generation"
        ],
        "active_analyses": len([a for a in analysis_results.values() if a["status"] == "processing"]),
        "total_analyses": len(analysis_results)
    })

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
=======
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
                "confidence_score": 94.7
            }
        }
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
