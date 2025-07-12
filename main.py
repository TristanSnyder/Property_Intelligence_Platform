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

# In-memory storage for demo (replace with database in production)
analysis_results = {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Enhanced root page with agentic AI features"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏠 Property Intelligence AI</title>
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
            <h1>🏠 Property Intelligence AI Platform</h1>
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
                "confidence_score": 94.7
            }
        }
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
