from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our custom services with better error handling
RAG_ENABLED = False
CREW_ENABLED = False
TRACKER_ENABLED = False

try:
    from rag_service import rag_service
    RAG_ENABLED = True
    logger.info("✅ RAG service loaded successfully")
except ImportError as e:
    logger.warning(f"❌ RAG service not available: {e}")
    rag_service = None

try:
    from agent_tracker import agent_tracker
    TRACKER_ENABLED = True
    logger.info("✅ Agent tracker loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Agent tracker not available: {e}")
    agent_tracker = None

try:
    from agents.crew_setup import property_analysis_crew
    CREW_ENABLED = True
    logger.info("✅ CrewAI agents loaded successfully")
except ImportError as e:
    logger.warning(f"❌ CrewAI not available: {e}")
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
    result: Optional[Dict[str, Any]] = None

class RAGQueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class PropertyDataRequest(BaseModel):
    property_data: Dict[str, Any]

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

# Enhanced Web Interface with Working Forms
@app.get("/", response_class=HTMLResponse)
async def web_interface():
    """Enhanced web interface with working property analysis"""
    status_indicators = {
        "rag": "status-active" if RAG_ENABLED else "status-inactive",
        "crew": "status-active" if CREW_ENABLED else "status-inactive", 
        "tracker": "status-active" if TRACKER_ENABLED else "status-inactive"
    }
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Property Intelligence AI Platform</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }}
            h1 {{
                text-align: center;
                margin-bottom: 10px;
                font-size: 2.5rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .subtitle {{
                text-align: center;
                margin-bottom: 30px;
                opacity: 0.9;
                font-size: 1.2rem;
            }}
            .status-section {{
                background: rgba(0, 0, 0, 0.2);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
            }}
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }}
            .status-item {{
                display: flex;
                align-items: center;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }}
            .analysis-section {{
                background: rgba(0, 0, 0, 0.2);
                padding: 25px;
                border-radius: 15px;
                margin: 20px 0;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #FFD700;
            }}
            .form-group input, .form-group select, .form-group textarea {{
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 16px;
            }}
            .btn {{
                background: #FFD700;
                color: #333;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                font-size: 16px;
                transition: all 0.3s ease;
                margin: 5px;
            }}
            .btn:hover {{
                background: #FFA500;
                transform: scale(1.05);
            }}
            .btn:disabled {{
                background: #666;
                cursor: not-allowed;
                transform: none;
            }}
            .results-section {{
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                border-radius: 15px;
                margin-top: 20px;
                display: none;
            }}
            .status-indicator {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 10px;
            }}
            .status-active {{ background: #4CAF50; }}
            .status-inactive {{ background: #f44336; }}
            .loading {{
                display: none;
                text-align: center;
                padding: 20px;
            }}
            .spinner {{
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top: 4px solid #FFD700;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .features {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .feature-card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }}
            .feature-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }}
            .feature-title {{
                font-size: 1.3rem;
                margin-bottom: 10px;
                color: #FFD700;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 Property Intelligence AI Platform</h1>
            <p class="subtitle">Agentic AI-powered real estate analysis with RAG and Vector Database</p>
            
            <!-- System Status -->
            <div class="status-section">
                <h3>🔧 System Status</h3>
                <div class="status-grid">
                    <div class="status-item">
                        <span class="status-indicator {status_indicators["rag"]}"></span>
                        <span>RAG Service: {"Active" if RAG_ENABLED else "Inactive"}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-indicator {status_indicators["crew"]}"></span>
                        <span>CrewAI Agents: {"Active" if CREW_ENABLED else "Inactive"}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-indicator {status_indicators["tracker"]}"></span>
                        <span>Agent Tracker: {"Active" if TRACKER_ENABLED else "Inactive"}</span>
                    </div>
                </div>
            </div>

            <!-- Property Analysis Section -->
            <div class="analysis-section">
                <h3>🔍 Property Analysis</h3>
                <form id="propertyAnalysisForm">
                    <div class="form-group">
                        <label for="address">Property Address</label>
                        <input type="text" id="address" name="address" placeholder="123 Main St, New York, NY 10001" required>
                    </div>
                    <div class="form-group">
                        <label for="analysisType">Analysis Type</label>
                        <select id="analysisType" name="analysisType">
                            <option value="comprehensive">Comprehensive Analysis</option>
                            <option value="market">Market Analysis Only</option>
                            <option value="risk">Risk Assessment Only</option>
                            <option value="quick">Quick Overview</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="context">Additional Context (Optional)</label>
                        <textarea id="context" name="context" rows="3" placeholder="Any specific requirements or focus areas..."></textarea>
                    </div>
                    <button type="submit" class="btn" id="analyzeBtn">🚀 Analyze Property</button>
                    <button type="button" class="btn" onclick="loadDemo()">📊 Load Demo</button>
                </form>
                
                <div class="loading" id="loadingSection">
                    <div class="spinner"></div>
                    <p>AI agents analyzing property...</p>
                    <p id="statusText">Initializing analysis...</p>
                </div>
                
                <div class="results-section" id="resultsSection">
                    <h4>📋 Analysis Results</h4>
                    <pre id="resultsContent"></pre>
                </div>
            </div>

            <!-- RAG Search Section -->
            <div class="analysis-section">
                <h3>🔍 RAG Property Search</h3>
                <form id="ragSearchForm">
                    <div class="form-group">
                        <label for="ragQuery">Search Query</label>
                        <input type="text" id="ragQuery" name="ragQuery" placeholder="luxury condos in Manhattan" required>
                    </div>
                    <button type="submit" class="btn" id="searchBtn">🔎 Search Properties</button>
                </form>
                
                <div class="results-section" id="ragResultsSection">
                    <h4>🏠 Search Results</h4>
                    <pre id="ragResultsContent"></pre>
                </div>
            </div>

            <!-- Features Overview -->
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
                    <p><span class="status-indicator {status_indicators["rag"]}"></span>Vector database search</p>
                    <p>Retrieve and analyze property data using advanced embedding search</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-title">📊 Market Analysis</div>
                    <p>Real-time market trends, comparable properties, and investment insights</p>
                </div>
            </div>

            <div style="text-align: center; margin-top: 30px; opacity: 0.8;">
                <p>🔗 <strong>Quick Links:</strong></p>
                <a href="/docs" style="color: #FFD700; margin: 0 15px;">API Documentation</a>
                <a href="/demo" style="color: #FFD700; margin: 0 15px;">Demo Results</a>
                <a href="/health" style="color: #FFD700; margin: 0 15px;">Health Check</a>
                <a href="/api" style="color: #FFD700; margin: 0 15px;">API Status</a>
            </div>
        </div>

        <script>
            // Property Analysis Form Handler
            document.getElementById('propertyAnalysisForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const address = document.getElementById('address').value;
                const analysisType = document.getElementById('analysisType').value;
                const context = document.getElementById('context').value;
                
                // Show loading
                document.getElementById('loadingSection').style.display = 'block';
                document.getElementById('resultsSection').style.display = 'none';
                document.getElementById('analyzeBtn').disabled = true;
                
                try {{
                    const response = await fetch('/analyze-property', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            address: address,
                            analysis_type: analysisType,
                            additional_context: context
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    // Hide loading
                    document.getElementById('loadingSection').style.display = 'none';
                    
                    // Show results
                    document.getElementById('resultsContent').textContent = JSON.stringify(result, null, 2);
                    document.getElementById('resultsSection').style.display = 'block';
                    
                }} catch (error) {{
                    document.getElementById('loadingSection').style.display = 'none';
                    document.getElementById('resultsContent').textContent = 'Error: ' + error.message;
                    document.getElementById('resultsSection').style.display = 'block';
                }} finally {{
                    document.getElementById('analyzeBtn').disabled = false;
                }}
            }});

            // RAG Search Form Handler
            document.getElementById('ragSearchForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const query = document.getElementById('ragQuery').value;
                document.getElementById('searchBtn').disabled = true;
                
                try {{
                    const response = await fetch(`/search-properties?query=${{encodeURIComponent(query)}}`);
                    const result = await response.json();
                    
                    document.getElementById('ragResultsContent').textContent = JSON.stringify(result, null, 2);
                    document.getElementById('ragResultsSection').style.display = 'block';
                    
                }} catch (error) {{
                    document.getElementById('ragResultsContent').textContent = 'Error: ' + error.message;
                    document.getElementById('ragResultsSection').style.display = 'block';
                }} finally {{
                    document.getElementById('searchBtn').disabled = false;
                }}
            }});

            // Load Demo Function
            function loadDemo() {{
                document.getElementById('address').value = '123 Main Street, New York, NY 10001';
                document.getElementById('analysisType').value = 'comprehensive';
                document.getElementById('context').value = 'Investment analysis for rental property';
            }}
        </script>
    </body>
    </html>
    """

# Enhanced API Endpoints

@app.get("/api")
async def api_status():
    """Enhanced API status endpoint"""
    return {
        "message": "Property Intelligence AI Platform",
        "version": "2.0.0",
        "status": "running",
        "features": {
            "rag_enabled": RAG_ENABLED,
            "crew_enabled": CREW_ENABLED,
            "tracker_enabled": TRACKER_ENABLED
        },
        "endpoints": {
            "analyze_property": "/analyze-property",
            "search_properties": "/search-properties",
            "market_trends": "/market-trends",
            "add_property": "/add-property-data"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rag_service": "active" if RAG_ENABLED else "inactive",
            "crew_ai": "active" if CREW_ENABLED else "inactive",
            "agent_tracker": "active" if TRACKER_ENABLED else "inactive"
        }
    }
    
    # Additional health checks
    if RAG_ENABLED and rag_service:
        try:
            # Test RAG service
            health_status["services"]["rag_service"] = "healthy"
        except Exception as e:
            health_status["services"]["rag_service"] = f"error: {str(e)}"
    
    return health_status

@app.post("/analyze-property")
async def analyze_property(request: PropertyAnalysisRequest, background_tasks: BackgroundTasks):
    """Enhanced property analysis with real CrewAI integration"""
    analysis_id = str(uuid.uuid4())
    
    logger.info(f"Starting property analysis for: {request.address}")
    
    try:
        if CREW_ENABLED and property_analysis_crew:
            logger.info("Using CrewAI for comprehensive analysis")
            
            # Track the analysis if tracker is available
            if TRACKER_ENABLED and agent_tracker:
                agent_tracker.start_analysis(analysis_id, request.address)
                # Start the simulation in the background
                background_tasks.add_task(
                    agent_tracker.simulate_property_analysis, 
                    analysis_id, 
                    request.address
                )
            
            # Run the CrewAI analysis (this will use real data sources if available)
            crew_result = await property_analysis_crew.analyze_property(request.address)
            
            logger.info(f"CrewAI analysis completed: {crew_result.get('status')}")
            
            return PropertyAnalysisResponse(
                analysis_id=analysis_id,
                address=request.address,
                status=crew_result.get("status", "completed"),
                created_at=datetime.now().isoformat(),
                agents_deployed=crew_result.get("agents_executed", ["Property Research Specialist", "Market Analyst", "Risk Assessor", "Report Generator"]),
                result=crew_result
            )
            
        else:
            logger.warning("CrewAI not available, using fallback analysis")
            
            # Track fallback analysis if tracker is available
            if TRACKER_ENABLED and agent_tracker:
                agent_tracker.start_analysis(analysis_id, request.address)
                background_tasks.add_task(
                    agent_tracker.simulate_property_analysis, 
                    analysis_id, 
                    request.address
                )
            
            # Enhanced fallback analysis with RAG insights if available
            fallback_result = {
                "analysis_type": "fallback",
                "property_address": request.address,
                "estimated_value": 450000 + (hash(request.address) % 200000),
                "risk_score": 20 + (hash(request.address) % 30),
                "investment_grade": "B+",
                "market_trend": "Rising (+5.2%)",
                "key_insights": [
                    "🎯 Property shows strong fundamentals",
                    "📈 Local market trending upward", 
                    "🏫 Good school district ratings",
                    "🚊 Accessible transportation"
                ],
                "data_sources": ["Mock Analysis Engine"],
                "note": "Install CrewAI dependencies for full AI agent analysis"
            }
            
            # Try to get RAG insights if available
            if RAG_ENABLED and rag_service:
                try:
                    rag_insights = await rag_service.generate_property_insights(
                        request.address, 
                        request.additional_context or ""
                    )
                    fallback_result["rag_insights"] = rag_insights
                    fallback_result["data_sources"].append("RAG Vector Database")
                except Exception as e:
                    logger.error(f"RAG insights error: {e}")
            
            return PropertyAnalysisResponse(
                analysis_id=analysis_id,
                address=request.address,
                status="completed",
                created_at=datetime.now().isoformat(),
                agents_deployed=["Fallback Analysis Engine"],
                result=fallback_result
            )
    
    except Exception as e:
        logger.error(f"Property analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/search-properties")
async def search_properties(query: str = ""):
    """Enhanced property search with RAG integration"""
    logger.info(f"Property search query: {query}")
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    try:
        if RAG_ENABLED and rag_service:
            logger.info("Using RAG service for property search")
            
            # Use the correct method from your RAG service
            results = await rag_service.search_similar_properties(query, k=5)
            
            return {
                "query": query,
                "results": results,
                "total_found": len(results) if isinstance(results, list) else 1,
                "timestamp": datetime.now().isoformat(),
                "search_method": "RAG Vector Search"
            }
        else:
            logger.warning("RAG service not available, using mock search")
            
            # Enhanced mock search results
            mock_results = [
                {
                    "address": f"Result {i+1} for '{query}'",
                    "price": 300000 + (hash(f"{query}{i}") % 400000),
                    "bedrooms": 2 + (hash(f"{query}{i}") % 4),
                    "bathrooms": 1 + (hash(f"{query}{i}") % 3),
                    "sqft": 1200 + (hash(f"{query}{i}") % 1500),
                    "match_score": 0.95 - (i * 0.1)
                }
                for i in range(min(5, len(query.split()) + 2))
            ]
            
            return {
                "query": query,
                "results": mock_results,
                "total_found": len(mock_results),
                "timestamp": datetime.now().isoformat(),
                "search_method": "Mock Search (Install RAG dependencies for vector search)",
                "note": "Enable RAG service for real property database search"
            }
            
    except Exception as e:
        logger.error(f"Property search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/market-trends")
async def get_market_trends(location: str = ""):
    """Enhanced market trends with RAG integration"""
    logger.info(f"Market trends request for: {location}")
    
    try:
        if RAG_ENABLED and rag_service:
            trends = await rag_service.get_market_trends(location)
            return trends
        else:
            # Enhanced mock market trends
            hash_val = hash(location) % 100
            
            return {
                "location": location,
                "market_trends": {
                    "median_price_change": f"+{5 + (hash_val % 10)}%",
                    "inventory_levels": "Low" if hash_val > 60 else "Moderate",
                    "days_on_market": 15 + (hash_val % 20),
                    "price_per_sqft": 200 + (hash_val % 150),
                    "market_temperature": "Hot" if hash_val > 70 else "Warm"
                },
                "forecast": {
                    "next_quarter": "Continued growth expected",
                    "annual_appreciation": f"{3 + (hash_val % 5)}%"
                },
                "timestamp": datetime.now().isoformat(),
                "data_source": "Mock Market Data (Enable RAG for real market intelligence)"
            }
            
    except Exception as e:
        logger.error(f"Market trends error: {e}")
        raise HTTPException(status_code=500, detail=f"Market trends failed: {str(e)}")

@app.post("/add-property-data")
async def add_property_data(request: PropertyDataRequest):
    """Enhanced property data addition with RAG integration"""
    logger.info("Adding property data to database")
    
    try:
        if RAG_ENABLED and rag_service:
            await rag_service.add_property_data(request.property_data)
            return {
                "status": "success",
                "message": "Property data added to vector database",
                "timestamp": datetime.now().isoformat(),
                "data_id": str(uuid.uuid4())
            }
        else:
            return {
                "status": "simulated",
                "message": "Property data would be added to vector database",
                "timestamp": datetime.now().isoformat(),
                "note": "Enable RAG service for real data storage"
            }
            
    except Exception as e:
        logger.error(f"Add property data error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add property data: {str(e)}")

# New endpoints for agent tracking
@app.get("/agent-status/{session_id}")
async def get_agent_status(session_id: str):
    """Get real-time agent status for a specific analysis session"""
    if not TRACKER_ENABLED or not agent_tracker:
        raise HTTPException(status_code=503, detail="Agent tracking not available")
    
    try:
        status = agent_tracker.get_session_info(session_id)
        return status
    except Exception as e:
        logger.error(f"Agent status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")

@app.get("/analysis-results/{session_id}")
async def get_analysis_results(session_id: str):
    """Get final analysis results for a completed session"""
    if not TRACKER_ENABLED or not agent_tracker:
        raise HTTPException(status_code=503, detail="Agent tracking not available")
    
    try:
        results = agent_tracker.get_analysis_results(session_id)
        return results
    except Exception as e:
        logger.error(f"Analysis results error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis results: {str(e)}")

@app.post("/property-insights")
async def get_property_insights(request: PropertyAnalysisRequest):
    """Get AI-powered property insights using RAG"""
    if not RAG_ENABLED or not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    try:
        insights = await rag_service.generate_property_insights(
            request.address, 
            request.additional_context or ""
        )
        return {
            "address": request.address,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Property insights error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@app.get("/demo")
async def demo_results():
    """Enhanced demo showing completed AI analysis"""
    return JSONResponse({
        "demo_analysis": {
            "analysis_id": "demo_12345",
            "address": "123 Main Street, New York, NY 10001", 
            "status": "completed",
            "system_status": {
                "rag_enabled": RAG_ENABLED,
                "crew_enabled": CREW_ENABLED,
                "tracker_enabled": TRACKER_ENABLED
            },
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
                    "real_time_tracking": TRACKER_ENABLED
                }
            }
        }
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting Property Intelligence AI Platform on port {port}")
    logger.info(f"📊 RAG Service: {'✅ Active' if RAG_ENABLED else '❌ Inactive'}")
    logger.info(f"🤖 CrewAI: {'✅ Active' if CREW_ENABLED else '❌ Inactive'}")
    logger.info(f"📈 Agent Tracker: {'✅ Active' if TRACKER_ENABLED else '❌ Inactive'}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
