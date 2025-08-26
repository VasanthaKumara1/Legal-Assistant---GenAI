"""
Document analysis endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.pydantic_models import DocumentAnalysisResponse, RiskAssessmentResponse
from app.services.document_service import DocumentAnalysisService

router = APIRouter()
document_service = DocumentAnalysisService()


@router.post("/{document_id}/analyze")
async def analyze_document(
    document_id: int,
    document_type: Optional[str] = None
):
    """
    Perform comprehensive analysis on a document.
    
    Includes:
    - Structure analysis
    - Readability assessment
    - Key section identification
    - Risk assessment
    - Legal terms extraction
    """
    try:
        # In a real app, fetch document content from database
        # For demo, using sample content
        sample_content = """
        RENTAL AGREEMENT
        
        This Rental Agreement is entered into between the Landlord and Tenant.
        
        1. RENT: Tenant agrees to pay monthly rent of $1,500 due on the 1st of each month.
        
        2. SECURITY DEPOSIT: Tenant will pay a security deposit of $3,000.
        
        3. TERMINATION: Either party may terminate this agreement with 30 days written notice.
        
        4. LIABILITY: Tenant shall indemnify and hold harmless the Landlord from any claims.
        
        5. ARBITRATION: Any disputes shall be resolved through binding arbitration.
        
        6. GOVERNING LAW: This agreement shall be governed by the laws of California.
        """
        
        analysis_result = await document_service.analyze_document(
            sample_content,
            document_type or "lease"
        )
        
        return {
            "document_id": document_id,
            "analysis": analysis_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{document_id}/risk-assessment")
async def get_risk_assessment(document_id: int):
    """Get detailed risk assessment for a document."""
    try:
        # Sample risk assessment data
        return {
            "document_id": document_id,
            "overall_risk": "medium",
            "risk_factors": [
                {
                    "risk_type": "binding_arbitration",
                    "risk_level": "high",
                    "description": "Disputes must be resolved through arbitration",
                    "recommendation": "Understand that you cannot take disputes to court"
                },
                {
                    "risk_type": "indemnification",
                    "risk_level": "medium",
                    "description": "Requires you to pay for others' losses",
                    "recommendation": "Consider negotiating liability limitations"
                }
            ],
            "recommendations": [
                "Consider having a lawyer review this document",
                "Understand arbitration process before signing",
                "Review indemnification clauses carefully"
            ],
            "confidence_score": 0.85
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk assessment failed: {str(e)}"
        )


@router.get("/{document_id}/sections")
async def get_document_sections(document_id: int):
    """Get identified key sections of a document."""
    try:
        # Sample sections data
        return {
            "document_id": document_id,
            "sections": [
                {
                    "id": 1,
                    "section_type": "payment",
                    "title": "Rent Payment Terms",
                    "content": "Tenant agrees to pay monthly rent of $1,500 due on the 1st of each month.",
                    "importance_level": "critical",
                    "risk_level": "low"
                },
                {
                    "id": 2,
                    "section_type": "liability",
                    "title": "Liability and Indemnification",
                    "content": "Tenant shall indemnify and hold harmless the Landlord from any claims.",
                    "importance_level": "high",
                    "risk_level": "medium"
                },
                {
                    "id": 3,
                    "section_type": "dispute",
                    "title": "Dispute Resolution",
                    "content": "Any disputes shall be resolved through binding arbitration.",
                    "importance_level": "high",
                    "risk_level": "high"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Section analysis failed: {str(e)}"
        )


@router.get("/{document_id}/timeline")
async def get_document_timeline(document_id: int):
    """Get important dates and deadlines from a document."""
    try:
        return {
            "document_id": document_id,
            "important_dates": [
                {
                    "date": "1st of each month",
                    "description": "Monthly rent payment due",
                    "type": "recurring_payment",
                    "importance": "critical"
                },
                {
                    "date": "30 days before termination",
                    "description": "Written notice required for termination",
                    "type": "notice_period",
                    "importance": "high"
                }
            ],
            "upcoming_deadlines": [],
            "renewal_dates": []
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Timeline extraction failed: {str(e)}"
        )