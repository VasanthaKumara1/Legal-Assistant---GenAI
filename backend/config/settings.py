"""
Configuration settings for the AI Legal Assistant application.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    app_name: str = "AI Legal Assistant"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    max_tokens: int = 1500
    temperature: float = 0.3
    
    # File Upload Settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_directory: str = "uploads"
    allowed_extensions: list[str] = [".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg"]
    
    # OCR Settings
    tesseract_cmd: Optional[str] = None  # Path to tesseract executable
    ocr_language: str = "eng"
    
    # Database Settings
    database_url: str = "sqlite:///./legal_assistant.db"
    
    # CORS Settings
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


# Ensure upload directory exists
def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        settings.upload_directory,
        "logs",
        "data"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Initialize directories on import
ensure_directories()