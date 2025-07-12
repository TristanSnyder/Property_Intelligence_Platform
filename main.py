from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Property Intelligence AI Platform",
    description="Agentic AI-powered real estate analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
        <head>
            <title>Property Intelligence AI</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 800px; margin: 0 auto; text-align: center; }
                .btn { background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
                .btn:hover { background: #218838; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏠 Property Intelligence AI Platform</h1>
                <p>Agentic AI-powered real estate analysis with multi-agent workflows</p>
                
                <h2>🚀 Available Services</h2>
                <a href="/docs" class="btn">📚 API Documentation</a>
                <a href="/health" class="btn">💚 Health Check</a>
                
                <h2>🤖 Demo Features</h2>
                <ul style="text-align: left; max-width: 500px; margin: 20px auto;">
                    <li>🔍 AI Property Research Agent</li>
                    <li>📊 Market Analysis Agent</li>
                    <li>⚠️ Risk Assessment Agent</li>
                    <li>📝 Report Generation Agent</li>
                </ul>
                
                <p><strong>Ready for JLL Demo! 🎯</strong></p>
            </div>
        </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "agents": "ready",
        "version": "1.0.0",
        "message": "Property Intelligence AI Platform is running!"
    }

@app.post("/analyze-property")
async def analyze_property(address: str):
    """Demo endpoint for property analysis"""
    return {
        "address": address,
        "status": "Analysis started",
        "agents_deployed": [
            "🔍 Property Researcher",
            "📊 Market Analyst", 
            "⚠️ Risk Assessor",
            "📝 Report Generator"
        ],
        "estimated_time": "2-3 minutes",
        "analysis_id": "demo-123",
        "message": "AI agents are analyzing the property..."
    }

@app.get("/demo")
async def demo_results():
    """Demo results endpoint"""
    return {
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
        "processing_time": "2.3 minutes"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
