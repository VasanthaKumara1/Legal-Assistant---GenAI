"""
API routes for the Legal Assistant application.
"""

from fastapi import APIRouter

from app.api.endpoints import documents, analysis, translation, terms

api_router = APIRouter()

# Include all endpoint routes
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(translation.router, prefix="/translation", tags=["translation"])
api_router.include_router(terms.router, prefix="/terms", tags=["legal-terms"])