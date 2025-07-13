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

@app.get("/")
async def root():
    """Root endpoint"""
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

# Add this endpoint to your main.py file

@app.get("/", response_class=HTMLResponse)
async def web_interface():
    """Web interface for the Property Intelligence AI Platform"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Property Intelligence AI Platform</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            h1 {
                text-align: center;
                margin-bottom: 10px;
                font-size: 2.5rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .subtitle {
                text-align: center;
                margin-bottom: 30px;
                opacity: 0.9;
                font-size: 1.2rem;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }
            .feature-title {
                font-size: 1.3rem;
                margin-bottom: 10px;
                color: #FFD700;
            }
            .api-section {
                margin-top: 40px;
                background: rgba(0, 0, 0, 0.2);
                padding: 20px;
                border-radius: 15px;
            }
            .endpoint {
                background: rgba(255, 255, 255, 0.1);
                margin: 10px 0;
                padding: 15px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
            }
            .method {
                background: #4CAF50;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8rem;
                margin-right: 10px;
            }
            .method.post { background: #2196F3; }
            .try-button {
                background: #FFD700;
                color: #333;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                margin-top: 10px;
                transition: all 0.3s ease;
            }
            .try-button:hover {
                background: #FFA500;
                transform: scale(1.05);
            }
            .status-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-active { background: #4CAF50; }
            .status-inactive { background: #f44336; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 Property Intelligence AI Platform</h1>
            <p class="subtitle">Agentic AI-powered real estate analysis with RAG and Vector Database</p>
            
            <div class="features">
                <div class="feature-card">
                    <div class="feature-title">🤖 AI Agents</div>
                    <p>Multi-agent system with specialized roles:</p>
                    <ul>
                        <li>Property Researcher</li>
                        <li>Market Analyst</li>
                        <li>Risk Assessor</li>
                        <li>Report Generator</li>
                    </ul>
                </div>
                
                <div class="feature-card">
                    <div class="feature-title">🔍 RAG Search</div>
                    <p><span class="status-indicator status-active"></span>Vector database search enabled</p>
                    <p>Retrieve and analyze property data using advanced embedding search</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-title">📊 Market Analysis</div>
                    <p>Real-time market trends, comparable properties, and investment insights</p>
                </div>
            </div>

            <div class="api-section">
                <h2>🚀 API Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method">GET</span>/demo
                    <p>View demo property analysis results</p>
                    <button class="try-button" onclick="window.open('/demo', '_blank')">Try Demo</button>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>/docs
                    <p>Interactive API documentation (Swagger UI)</p>
                    <button class="try-button" onclick="window.open('/docs', '_blank')">Open API Docs</button>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>/analyze-property
                    <p>Analyze a property using AI agents</p>
                    <p><strong>Example:</strong> {"address": "123 Main St, New York, NY"}</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>/search-properties?query=...
                    <p>Search properties using RAG vector database</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>/market-trends?location=...
                    <p>Get market trends for a specific location</p>
                </div>
            </div>

            <div style="text-align: center; margin-top: 30px; opacity: 0.8;">
                <p>🔗 <strong>Quick Links:</strong></p>
                <a href="/docs" style="color: #FFD700; margin: 0 15px;">API Documentation</a>
                <a href="/demo" style="color: #FFD700; margin: 0 15px;">Demo Results</a>
                <a href="/health" style="color: #FFD700; margin: 0 15px;">Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """

# Update your existing root endpoint to be the API endpoint
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
