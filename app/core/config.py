"""
Configuration management using pydantic-settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable validation."""
    
    # GitHub Configuration
    GITHUB_TOKEN: str
    
    # Gemini AI Configuration  
    GEMINI_API_KEY: str
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Redis (optional for session storage)
    REDIS_URL: Optional[str] = None
    
    # Demo users (in production, use proper user management)
    DEMO_USERNAME: str = "admin"
    DEMO_PASSWORD: str = "password123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()