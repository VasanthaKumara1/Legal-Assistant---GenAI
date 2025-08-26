"""
Pydantic models for API requests and responses.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    upload_timestamp: datetime
    message: str = "Document uploaded successfully"


class DocumentProcessingRequest(BaseModel):
    """Request model for document processing."""
    document_id: int
    process_ocr: bool = True
    process_ai: bool = True


class DocumentProcessingResponse(BaseModel):
    """Response model for document processing status."""
    document_id: int
    ocr_status: str
    ai_status: str
    message: str


class DocumentContentResponse(BaseModel):
    """Response model for document content."""
    document_id: int
    filename: str
    original_text: Optional[str] = None
    simplified_text: Optional[str] = None
    ocr_status: str
    ai_status: str
    processing_time: Optional[float] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None


class SimplifyTextRequest(BaseModel):
    """Request model for text simplification."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to simplify")
    context: Optional[str] = Field(None, description="Additional context for simplification")


class SimplifyTextResponse(BaseModel):
    """Response model for text simplification."""
    original_text: str
    simplified_text: str
    processing_time: float
    tokens_used: int
    model_used: str


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    status: str = "healthy"
    app_name: str
    app_version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)