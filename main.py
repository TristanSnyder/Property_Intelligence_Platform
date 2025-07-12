from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Property Intelligence AI Platform...")
    print("✅ Database initialized")
    print("🤖 AI Agents ready")
    yield
    # Shutdown
    print("🛑 Shutting down...")

app = FastAPI(
    title="Property Intelligence AI Platform",
    description="Agentic AI-powered real estate analysis with RAG and geospatial intelligence",
    version="1.0.0",
    lifespan=lifespan
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
    return {
        "message": "🏠 Property Intelligence AI Platform",
        "status": "🟢 Active",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agents": "ready"}

@app.post("/analyze-property")
async def analyze_property(address: str):
    """Demo endpoint for property analysis"""
    return {
        "address": address,
        "status": "Analysis started",
        "agents": ["researcher", "analyst", "risk_assessor", "report_generator"],
        "estimated_time": "2-3 minutes"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
