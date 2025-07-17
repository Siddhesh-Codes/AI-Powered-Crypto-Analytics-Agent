from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import init_db

# Create FastAPI instance
app = FastAPI(
    title="Crypto Analytics Agent API",
    description="AI-Powered Cryptocurrency Analytics and Forecasting API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    # Initialize database
    await init_db()
    print("🚀 Crypto Analytics Agent API started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Crypto Analytics Agent API shutting down...")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Crypto Analytics Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "features": [
            "Real-time crypto data",
            "AI price predictions",
            "Portfolio management",
            "Technical analysis",
            "Market sentiment"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
