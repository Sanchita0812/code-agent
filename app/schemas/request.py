"""
Pydantic schemas for API request validation.
"""
from pydantic import BaseModel, HttpUrl, Field


class CodeRequest(BaseModel):
    """Schema for the code generation request."""
    
    repoUrl: HttpUrl = Field(
        ..., 
        description="Public GitHub repository URL",
        example="https://github.com/username/repository"
    )
    prompt: str = Field(
        ..., 
        min_length=10,
        max_length=2000,
        description="Natural language prompt describing the desired code changes",
        example="Add authentication middleware to the Express.js routes"
    )

    class Config:
        json_encoders = {
            HttpUrl: str
        }