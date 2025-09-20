from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

# Import routers
from routes.chatbot import router as chatbot_router
from routes.weather import router as weather_router
from routes.dashboard import router as dashboard_router

# Create FastAPI app
app = FastAPI(
    title="ClimateBuddy API",
    description="AI-powered climate science tutor with interactive dashboard",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chatbot_router, prefix="/api/chat", tags=["chatbot"])
app.include_router(weather_router, prefix="/api/weather", tags=["weather"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():

    return HTMLResponse(content="running")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ClimateBuddy API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
