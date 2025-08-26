"""
Pydantic models for API requests and responses.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentUpload(BaseModel):
    """Document upload request."""
    title: Optional[str] = None
    document_type: Optional[str] = None
    industry: Optional[str] = None
    language: str = "en"


class DocumentResponse(BaseModel):
    """Document response model."""
    id: int
    title: str
    original_filename: str
    file_type: str
    document_type: Optional[str]
    industry: Optional[str]
    upload_date: datetime
    file_size: int
    language: str
    
    class Config:
        from_attributes = True


class SimplificationRequest(BaseModel):
    """Request for document simplification."""
    complexity_level: str = Field(..., description="elementary, high_school, college, expert")
    language: str = "en"
    focus_areas: Optional[List[str]] = None  # specific sections to focus on


class ExplanationResponse(BaseModel):
    """Simplified explanation response."""
    id: int
    complexity_level: str
    simplified_content: str
    key_points: List[str]
    rights_obligations: Dict[str, Any]
    deadlines: List[Dict[str, Any]]
    red_flags: List[str]
    confidence_score: float
    created_date: datetime
    language: str
    
    class Config:
        from_attributes = True


class DocumentSectionResponse(BaseModel):
    """Document section response."""
    id: int
    section_type: str
    title: Optional[str]
    content: str
    importance_level: str
    risk_level: str
    
    class Config:
        from_attributes = True


class SectionExplanationResponse(BaseModel):
    """Section explanation response."""
    id: int
    complexity_level: str
    simplified_text: str
    what_it_means: Optional[str]
    impact_analysis: Optional[str]
    related_terms: List[Dict[str, str]]
    confidence_score: float
    
    class Config:
        from_attributes = True


class LegalTermResponse(BaseModel):
    """Legal term definition response."""
    term: str
    definition: str
    simple_definition: str
    context: Optional[str]
    examples: List[str]
    related_terms: List[str]
    
    class Config:
        from_attributes = True


class TermLookupRequest(BaseModel):
    """Request for legal term lookup."""
    term: str
    context: Optional[str] = None
    complexity_level: str = "high_school"


class UserPreferences(BaseModel):
    """User preferences for document processing."""
    complexity_level: str = "high_school"
    language: str = "en"
    focus_areas: Optional[List[str]] = None
    accessibility_needs: Optional[List[str]] = None


class DocumentAnalysisResponse(BaseModel):
    """Complete document analysis response."""
    document: DocumentResponse
    sections: List[DocumentSectionResponse]
    explanation: ExplanationResponse
    legal_terms: List[LegalTermResponse]
    analysis_summary: Dict[str, Any]


class BookmarkRequest(BaseModel):
    """Request to bookmark a section."""
    section_id: int
    note: Optional[str] = None


class UserSessionResponse(BaseModel):
    """User session response."""
    session_id: str
    document_id: int
    preferred_complexity: str
    preferred_language: str
    bookmarks: List[Dict[str, Any]]
    notes: List[Dict[str, Any]]
    progress: float
    last_activity: datetime
    
    class Config:
        from_attributes = True


class AnalysisJobResponse(BaseModel):
    """Analysis job status response."""
    id: int
    job_type: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_date: datetime
    
    class Config:
        from_attributes = True


class ComparisonRequest(BaseModel):
    """Request to compare documents."""
    document_ids: List[int] = Field(..., min_items=2, max_items=5)
    comparison_type: str = "terms"  # terms, structure, risks


class ComparisonResponse(BaseModel):
    """Document comparison response."""
    documents: List[DocumentResponse]
    similarities: List[Dict[str, Any]]
    differences: List[Dict[str, Any]]
    recommendations: List[str]


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response."""
    overall_risk: str  # low, medium, high
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: float