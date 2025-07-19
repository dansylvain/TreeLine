"""Configuration settings for the TreeLine backend."""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://treeline_user:treeline_password@localhost:5432/treeline"
    )
    
    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Application
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # AI Agent
    ai_agent_url: str = os.getenv("AI_AGENT_URL", "http://ai-agent:8001")
    
    # CORS
    allowed_origins: list[str] = [
        "http://localhost:8501",
        "http://streamlit-ui:8501",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
