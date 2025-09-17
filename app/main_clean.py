"""
Legal Assistant GenAI - Simplified Main Application
A working prototype with core legal document processing features
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Assistant GenAI",
    description="AI-powered legal document simplification and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class DocumentAnalysisRequest(BaseModel):
    text: str
    document_type: Optional[str] = "general"

class DocumentAnalysisResponse(BaseModel):
    simplified_text: str
    key_points: List[str]
    risk_level: str
    risk_factors: List[str]
    recommendations: List[str]
    confidence_score: float

class RiskAssessmentResponse(BaseModel):
    overall_risk: str
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: float

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "Legal Assistant GenAI - AI Legal Document Helper",
        "version": "1.0.0",
        "features": [
            "Document Upload & Processing",
            "Legal Text Simplification", 
            "Risk Assessment Analysis",
            "Document Analysis & Insights"
        ],
        "documentation": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Document upload endpoint
@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a legal document"""
    try:
        # Check file type
        allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        content = await file.read()
        
        # Mock document processing (in real implementation, would extract text from PDF/DOCX)
        extracted_text = f"Mock extracted text from {file.filename}. This would contain the actual document content in a real implementation."
        
        return {
            "document_id": "mock_doc_123",
            "filename": file.filename,
            "size": len(content),
            "text_preview": extracted_text[:200] + "...",
            "status": "processed",
            "message": "Document uploaded and processed successfully"
        }
    
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Document processing failed")

# Text simplification endpoint
@app.post("/ai/simplify", response_model=DocumentAnalysisResponse)
async def simplify_legal_text(request: DocumentAnalysisRequest):
    """Simplify complex legal text into plain language"""
    try:
        # Mock AI simplification (in real implementation, would use OpenAI/Claude/etc.)
        simplified_text = f"""
SIMPLIFIED VERSION:

This document is about {request.document_type or 'legal matters'}. Here's what it means in simple terms:

• The main purpose is to establish rules and agreements between parties
• Important deadlines and obligations are specified
• There are consequences for not following the terms
• Both parties have rights and responsibilities

KEY TAKEAWAYS:
- Read carefully before signing
- Understand your obligations
- Know your rights
- Consider legal advice if unsure
        """.strip()
        
        # Mock analysis results
        return DocumentAnalysisResponse(
            simplified_text=simplified_text,
            key_points=[
                "Main obligations and responsibilities",
                "Important dates and deadlines", 
                "Payment terms and conditions",
                "Termination clauses"
            ],
            risk_level="medium",
            risk_factors=[
                "Binding arbitration clause",
                "Limited liability terms",
                "Automatic renewal provisions"
            ],
            recommendations=[
                "Review all terms carefully",
                "Understand payment obligations",
                "Note termination procedures",
                "Consider legal consultation"
            ],
            confidence_score=0.85
        )
    
    except Exception as e:
        logger.error(f"Text simplification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Text simplification failed")

# Risk assessment endpoint
@app.get("/documents/{document_id}/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(document_id: str):
    """Get detailed risk assessment for a document"""
    try:
        # Mock risk assessment data
        return RiskAssessmentResponse(
            overall_risk="medium",
            risk_factors=[
                {
                    "risk_type": "binding_arbitration",
                    "risk_level": "high",
                    "description": "Disputes must be resolved through arbitration",
                    "recommendation": "Understand that you cannot take disputes to court"
                },
                {
                    "risk_type": "indemnification",
                    "risk_level": "medium", 
                    "description": "You may be required to pay for others' losses",
                    "recommendation": "Consider negotiating liability limitations"
                },
                {
                    "risk_type": "automatic_renewal",
                    "risk_level": "low",
                    "description": "Contract may automatically renew",
                    "recommendation": "Mark calendar for renewal dates"
                }
            ],
            recommendations=[
                "Consider having a lawyer review this document",
                "Understand arbitration process before signing",
                "Review indemnification clauses carefully",
                "Note all important dates and deadlines"
            ],
            confidence_score=0.82
        )
    
    except Exception as e:
        logger.error(f"Risk assessment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Risk assessment failed")

# Document analysis endpoint
@app.get("/documents/{document_id}/analysis")
async def analyze_document(document_id: str):
    """Get comprehensive document analysis"""
    try:
        # Mock document analysis
        return {
            "document_id": document_id,
            "analysis": {
                "document_type": "rental_agreement",
                "parties": ["Landlord", "Tenant"],
                "key_sections": [
                    {"section": "Rent Payment", "importance": "high"},
                    {"section": "Security Deposit", "importance": "high"},
                    {"section": "Termination", "importance": "medium"},
                    {"section": "Maintenance", "importance": "medium"}
                ],
                "important_dates": [
                    {"date": "2024-01-01", "description": "Lease start date"},
                    {"date": "2024-12-31", "description": "Lease end date"},
                    {"date": "Monthly on 1st", "description": "Rent due date"}
                ],
                "financial_terms": {
                    "monthly_rent": "$1,500",
                    "security_deposit": "$3,000",
                    "late_fees": "$50"
                }
            },
            "summary": "This is a standard rental agreement with typical terms and conditions.",
            "confidence_score": 0.88
        }
    
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Document analysis failed")

if __name__ == "__main__":
    uvicorn.run(
        "app.main_clean:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )