"""
Configuration settings for Legal Assistant GenAI
"""

import os
from typing import List
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Legal Assistant GenAI"
    app_version: str = "1.5.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    refresh_token_expire_days: int = 7
    
    # Database
    database_url: str = Field(default="postgresql://user:pass@localhost/legal_assistant", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # AI Services
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    llama_api_key: str = Field(default="", env="LLAMA_API_KEY")
    
    # Document Processing
    max_file_size: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    upload_dir: str = Field(default="/tmp/uploads", env="UPLOAD_DIR")
    processed_dir: str = Field(default="/tmp/processed", env="PROCESSED_DIR")
    
    # OCR Services
    google_vision_credentials: str = Field(default="", env="GOOGLE_VISION_CREDENTIALS")
    azure_form_recognizer_key: str = Field(default="", env="AZURE_FORM_RECOGNIZER_KEY")
    azure_form_recognizer_endpoint: str = Field(default="", env="AZURE_FORM_RECOGNIZER_ENDPOINT")
    
    # External Integrations
    docusign_integration_key: str = Field(default="", env="DOCUSIGN_INTEGRATION_KEY")
    docusign_user_id: str = Field(default="", env="DOCUSIGN_USER_ID")
    docusign_account_id: str = Field(default="", env="DOCUSIGN_ACCOUNT_ID")
    docusign_base_url: str = Field(default="https://demo.docusign.net/restapi", env="DOCUSIGN_BASE_URL")
    
    microsoft_client_id: str = Field(default="", env="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: str = Field(default="", env="MICROSOFT_CLIENT_SECRET")
    microsoft_tenant_id: str = Field(default="", env="MICROSOFT_TENANT_ID")
    
    google_client_id: str = Field(default="", env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", env="GOOGLE_CLIENT_SECRET")
    
    # Monitoring
    sentry_dsn: str = Field(default="", env="SENTRY_DSN")
    prometheus_enabled: bool = Field(default=False, env="PROMETHEUS_ENABLED")
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    # WebSocket
    websocket_max_connections: int = Field(default=100, env="WEBSOCKET_MAX_CONNECTIONS")
    
    # Voice Services
    speech_recognition_service: str = Field(default="google", env="SPEECH_RECOGNITION_SERVICE")
    text_to_speech_service: str = Field(default="google", env="TEXT_TO_SPEECH_SERVICE")
    
    # Analytics
    analytics_retention_days: int = Field(default=365, env="ANALYTICS_RETENTION_DAYS")
    
    # Compliance
    gdpr_enabled: bool = Field(default=True, env="GDPR_ENABLED")
    ccpa_enabled: bool = Field(default=True, env="CCPA_ENABLED")
    audit_log_retention_days: int = Field(default=2555, env="AUDIT_LOG_RETENTION_DAYS")  # 7 years
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()