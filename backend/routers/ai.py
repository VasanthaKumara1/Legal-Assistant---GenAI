"""
API router for AI text simplification endpoints.
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from backend.models.schemas import SimplifyTextRequest, SimplifyTextResponse
from backend.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/simplify", response_model=SimplifyTextResponse)
async def simplify_text(request: SimplifyTextRequest):
    """
    Simplify legal text using AI.
    
    - **text**: Legal text to simplify (max 10,000 characters)
    - **context**: Optional additional context for simplification
    - Returns simplified text with processing metadata
    """
    try:
        # Validate API key
        if not ai_service.validate_api_key():
            raise HTTPException(
                status_code=503, 
                detail="AI service not available. Please configure OpenAI API key."
            )
        
        # Simplify the text
        simplified_text, tokens_used, processing_time = await ai_service.simplify_legal_text(
            legal_text=request.text,
            context=request.context
        )
        
        return SimplifyTextResponse(
            original_text=request.text,
            simplified_text=simplified_text,
            processing_time=processing_time,
            tokens_used=tokens_used,
            model_used=ai_service.settings.openai_model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text simplification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text simplification failed: {str(e)}")


@router.post("/explain-term")
async def explain_legal_term(term: str, context: str = None):
    """
    Explain a legal term in simple language.
    
    - **term**: Legal term to explain
    - **context**: Optional context for the explanation
    - Returns simple explanation of the legal term
    """
    try:
        # Validate API key
        if not ai_service.validate_api_key():
            raise HTTPException(
                status_code=503, 
                detail="AI service not available. Please configure OpenAI API key."
            )
        
        # Get explanation
        explanation = await ai_service.explain_legal_term(term, context)
        
        return {
            "term": term,
            "explanation": explanation,
            "context": context
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Legal term explanation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Legal term explanation failed: {str(e)}")


@router.get("/status")
async def get_ai_service_status():
    """
    Check the status of the AI service.
    
    - Returns AI service availability and configuration
    """
    try:
        is_available = ai_service.validate_api_key()
        
        return {
            "ai_service_available": is_available,
            "model": ai_service.settings.openai_model if is_available else None,
            "max_tokens": ai_service.settings.max_tokens if is_available else None,
            "temperature": ai_service.settings.temperature if is_available else None,
            "message": "AI service is ready" if is_available else "OpenAI API key not configured"
        }
        
    except Exception as e:
        logger.error(f"AI service status check failed: {str(e)}")
        return {
            "ai_service_available": False,
            "message": f"AI service error: {str(e)}"
        }