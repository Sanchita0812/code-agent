"""
FastAPI application entry point for the AI coding agent.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.code import router as code_router
from app.api.auth import router as auth_router
from app.core.config import settings


app = FastAPI(
    title="CodeAssist Minimal - AI Coding Agent",
    description="An AI coding agent powered by Google Gemini Flash 1.5 that analyzes GitHub repositories and creates pull requests based on natural language prompts",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(code_router, prefix="/code", tags=["code-generation"])


@app.get("/")
async def root():
    return {
        "message": "CodeAssist AI Coding Agent is running", 
        "frontend": "/frontend/", 
        "login": "/frontend/login.html",
        "docs": "/docs",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "auth_enabled": True
    }