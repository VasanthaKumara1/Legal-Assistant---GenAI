"""
Legal Assistant GenAI - Simple Main Application
Working demo version for quick deployment
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Assistant GenAI",
    description="AI-powered legal document analysis and simplification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data models with validation
class SimplificationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Legal text to simplify")
    complexity_level: str = Field(default="high_school", pattern="^(elementary|high_school|college|expert)$")

class TermLookupRequest(BaseModel):
    term: str = Field(..., min_length=1, max_length=100, description="Legal term to look up")
    context: Optional[str] = Field(None, max_length=500, description="Context for the term")

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    data: dict

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "Legal Assistant GenAI"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Legal Assistant GenAI API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "simplify": "/api/simplify",
            "terms": "/api/terms/lookup",
            "upload": "/api/upload"
        }
    }

# API Routes
@app.post("/api/simplify")
async def simplify_text(request: SimplificationRequest):
    """
    Simplify legal text to specified complexity level.
    Demo version - returns mock response.
    """
    try:
        # Mock response for demo
        simplified_text = f"This legal text has been simplified to {request.complexity_level} level: {request.text[:100]}..."
        
        return {
            "success": True,
            "original_text": request.text,
            "simplified_text": simplified_text,
            "complexity_level": request.complexity_level,
            "key_points": [
                "This is a sample key point",
                "Legal terms have been simplified",
                "Complex clauses have been explained"
            ],
            "red_flags": [
                "Sample red flag: Review payment terms",
                "Sample concern: Liability clause needs attention"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simplification failed: {str(e)}")

@app.post("/api/terms/lookup")
async def lookup_term(request: TermLookupRequest):
    """
    Look up legal term definition.
    Demo version - returns mock response.
    """
    try:
        # Mock legal terms database
        sample_terms = {
            "liability": "Responsibility for damages or losses",
            "indemnify": "To compensate for harm or loss",
            "arbitration": "Alternative dispute resolution method",
            "jurisdiction": "Legal authority to make decisions",
            "consideration": "Something of value exchanged in a contract"
        }
        
        definition = sample_terms.get(request.term.lower(), 
                                    f"Legal term definition for '{request.term}' would appear here")
        
        return {
            "success": True,
            "term": request.term,
            "definition": definition,
            "simple_explanation": f"In simple terms: {definition}",
            "examples": [f"Example usage of {request.term} in contracts"],
            "related_terms": ["contract", "agreement", "legal document"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Term lookup failed: {str(e)}")

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and analyze legal document.
    Demo version - returns mock analysis.
    """
    try:
        # Validate filename exists
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
            
        # Validate file type
        allowed_types = ['.pdf', '.docx', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not supported. Allowed: {allowed_types}"
            )
        
        # Read file content (demo)
        content = await file.read()
        
        return {
            "success": True,
            "filename": file.filename,
            "file_size": len(content),
            "analysis": {
                "document_type": "Legal Contract",
                "risk_level": "Medium",
                "key_sections": [
                    "Payment Terms",
                    "Liability Clauses", 
                    "Termination Conditions"
                ],
                "risks_identified": [
                    "Unlimited liability exposure",
                    "Unfavorable payment terms",
                    "Unclear termination clause"
                ],
                "recommendations": [
                    "Review liability limitations",
                    "Negotiate payment schedule",
                    "Clarify termination procedures"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/features")
async def get_features():
    """Get list of available features."""
    return {
        "features": [
            {
                "name": "Text Simplification",
                "endpoint": "/api/simplify",
                "description": "Convert legal jargon to plain English"
            },
            {
                "name": "Legal Terms Lookup",
                "endpoint": "/api/terms/lookup", 
                "description": "Get definitions for legal terms"
            },
            {
                "name": "Document Upload",
                "endpoint": "/api/upload",
                "description": "Upload and analyze legal documents"
            },
            {
                "name": "Risk Assessment",
                "endpoint": "/api/upload",
                "description": "AI-powered risk analysis of contracts"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Railway uses PORT env var)
    port = int(os.getenv("PORT", 8001))
    
    print("🚀 Starting Legal Assistant GenAI...")
    print(f"📡 Server will be available at: http://localhost:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=port)