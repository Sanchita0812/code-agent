"""
FastAPI application entry point for the AI coding agent.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.code import router
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(
    title="Backspace Minimal - AI Coding Agent",
    description="An AI coding agent powered by Google Gemini Flash 1.5 that analyzes GitHub repositories and creates pull requests based on natural language prompts",
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

# Mount static files for frontend
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Include the code router with /code prefix
app.include_router(router, prefix="/code")


@app.get("/")
async def root():
    return {"message": "Backspace AI Coding Agent is running", "frontend": "/frontend/", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}