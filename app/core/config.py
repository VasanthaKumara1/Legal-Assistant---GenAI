"""
Core configuration settings for the Legal Assistant application.
"""

import os
from typing import List, Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Legal Document Demystification AI"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost/legal_assistant"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx", ".txt"]
    UPLOAD_DIR: str = "uploads"
    
    # AI Models
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    LEGAL_MODEL: str = "gpt-4"
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.3
    
    # Complexity Levels
    COMPLEXITY_LEVELS: List[str] = [
        "elementary",
        "high_school", 
        "college",
        "expert"
    ]
    
    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = [
        "en",  # English
        "es",  # Spanish
        "fr",  # French
        "zh",  # Chinese
        "hi",  # Hindi
    ]

    class Config:
        env_file = ".env"


settings = Settings()