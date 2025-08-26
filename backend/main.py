"""
Main FastAPI application for the AI Legal Assistant.
"""
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger
import sys

from backend.config.settings import settings
from backend.routers import documents, ai
from backend.models.schemas import HealthCheckResponse

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    settings.log_file,
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="30 days"
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    AI Legal Assistant API for document processing and legal jargon simplification.
    
    ## Features
    
    * **Document Upload**: Upload PDF, Word, and image documents
    * **OCR Processing**: Extract text from documents using Tesseract OCR
    * **AI Simplification**: Simplify legal jargon using OpenAI GPT
    * **Dual View**: Get both original and simplified text
    
    ## Workflow
    
    1. Upload a document using `/documents/upload`
    2. Process the document using `/documents/{id}/process`
    3. Get the simplified content using `/documents/{id}/content`
    
    ## Direct Text Simplification
    
    You can also directly simplify text using `/ai/simplify` without uploading a document.
    """,
    contact={
        "name": "AI Legal Assistant Team",
        "email": "support@ailegalassistant.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(ai.router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthCheckResponse, tags=["system"])
async def health_check():
    """
    Health check endpoint.
    
    Returns application status and metadata.
    """
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.app_name,
        app_version=settings.app_version,
        timestamp=datetime.utcnow()
    )


@app.get("/info", tags=["system"])
async def app_info():
    """
    Get application information and configuration.
    
    Returns non-sensitive configuration details.
    """
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "max_file_size": settings.max_file_size,
        "allowed_extensions": settings.allowed_extensions,
        "ocr_language": settings.ocr_language,
        "openai_model": settings.openai_model,
        "max_tokens": settings.max_tokens,
        "temperature": settings.temperature,
    }


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Upload directory: {settings.upload_directory}")
    logger.info(f"Database URL: {settings.database_url}")
    
    # Check AI service availability
    from backend.services.ai_service import ai_service
    if ai_service.validate_api_key():
        logger.info("AI service is available")
    else:
        logger.warning("AI service is not available - OpenAI API key not configured")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )