"""
Legal text translation and simplification endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.pydantic_models import SimplificationRequest, ExplanationResponse
from app.services.translation_service import LegalTranslationEngine

router = APIRouter()
translation_engine = LegalTranslationEngine()


@router.post("/simplify")
async def simplify_text(request: SimplificationRequest, text: str):
    """
    Simplify legal text to the specified complexity level.
    
    Complexity levels:
    - elementary: 5th grade level
    - high_school: High school level (default)
    - college: College level
    - expert: Professional level with legal precision
    """
    try:
        result = await translation_engine.translate_legal_text(
            text=text,
            complexity_level=request.complexity_level,
            context=None
        )
        
        return {
            "original_text": text,
            "simplified_text": result.get("simplified_text"),
            "complexity_level": request.complexity_level,
            "key_points": result.get("key_points", []),
            "what_it_means": result.get("what_it_means"),
            "red_flags": result.get("red_flags", []),
            "confidence_score": result.get("confidence_score", 0.0),
            "legal_terms": result.get("legal_terms_used", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simplification failed: {str(e)}"
        )


@router.post("/{document_id}/simplify")
async def simplify_document(
    document_id: int,
    request: SimplificationRequest
):
    """Simplify an entire document to the specified complexity level."""
    try:
        # In a real app, fetch document from database
        # Using sample content for demo
        sample_document = """
        TERMS AND CONDITIONS
        
        By accessing and using this service, you agree to be bound by these Terms and Conditions.
        
        1. ACCEPTANCE OF TERMS: Your access to and use of the Service is conditioned on your acceptance of and compliance with these Terms.
        
        2. LIMITATION OF LIABILITY: In no event shall the Company be liable for any indirect, incidental, special, consequential, or punitive damages.
        
        3. INDEMNIFICATION: You agree to defend, indemnify, and hold harmless the Company from and against any and all claims, damages, obligations, losses, liabilities, costs or debt, and expenses.
        
        4. TERMINATION: We may terminate or suspend your account immediately, without prior notice or liability, for any reason whatsoever.
        """
        
        result = await translation_engine.translate_legal_text(
            text=sample_document,
            complexity_level=request.complexity_level,
            context=f"This is a legal document of type: terms and conditions"
        )
        
        return {
            "document_id": document_id,
            "complexity_level": request.complexity_level,
            "language": request.language,
            "simplified_content": result.get("simplified_text"),
            "key_points": result.get("key_points", []),
            "rights_obligations": {
                "your_rights": [
                    "Right to access the service",
                    "Right to terminate your account"
                ],
                "your_obligations": [
                    "Follow the terms and conditions",
                    "Pay for any damages you cause to the company"
                ],
                "company_rights": [
                    "Right to terminate your account at any time",
                    "Right to limit their liability"
                ]
            },
            "red_flags": result.get("red_flags", []),
            "confidence_score": result.get("confidence_score", 0.0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document simplification failed: {str(e)}"
        )


@router.post("/compare-complexity")
async def compare_complexity_levels(text: str):
    """
    Show the same text at different complexity levels for comparison.
    """
    try:
        levels = ["elementary", "high_school", "college", "expert"]
        comparisons = {}
        
        for level in levels:
            result = await translation_engine.translate_legal_text(
                text=text,
                complexity_level=level
            )
            
            comparisons[level] = {
                "simplified_text": result.get("simplified_text"),
                "confidence_score": result.get("confidence_score", 0.0)
            }
        
        return {
            "original_text": text,
            "complexity_comparisons": comparisons,
            "recommendation": "high_school"  # Default recommendation
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Complexity comparison failed: {str(e)}"
        )


@router.post("/explain-section")
async def explain_section(
    section_text: str,
    complexity_level: str = "high_school",
    document_type: Optional[str] = None
):
    """
    Provide detailed explanation of a specific document section.
    """
    try:
        result = await translation_engine.translate_legal_text(
            text=section_text,
            complexity_level=complexity_level,
            context=f"Document section explanation for {document_type or 'legal document'}"
        )
        
        return {
            "section_text": section_text,
            "simplified_explanation": result.get("simplified_text"),
            "what_it_means_for_you": result.get("what_it_means"),
            "key_points": result.get("key_points", []),
            "potential_risks": result.get("red_flags", []),
            "related_terms": result.get("legal_terms_used", []),
            "confidence_score": result.get("confidence_score", 0.0),
            "complexity_level": complexity_level
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Section explanation failed: {str(e)}"
        )


@router.get("/reading-levels")
async def get_reading_levels():
    """Get information about available reading/complexity levels."""
    return {
        "complexity_levels": [
            {
                "level": "elementary",
                "description": "5th grade reading level - very simple language",
                "target_audience": "Children, basic literacy",
                "example": "You must pay money every month."
            },
            {
                "level": "high_school",
                "description": "High school reading level - clear, accessible language",
                "target_audience": "General public, most adults",
                "example": "You are required to make monthly payments as agreed."
            },
            {
                "level": "college",
                "description": "College reading level - more detailed explanations",
                "target_audience": "Educated adults, business contexts",
                "example": "The agreement obligates you to remit monthly payments according to the specified terms."
            },
            {
                "level": "expert",
                "description": "Professional level - maintains legal precision",
                "target_audience": "Legal professionals, detailed analysis needed",
                "example": "The contractual obligation requires timely payment of monthly installments per the agreed schedule."
            }
        ],
        "recommendation": "Start with 'high_school' level for most users"
    }