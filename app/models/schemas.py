"""
Pydantic schemas for Legal Assistant GenAI
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    LAWYER = "lawyer"
    PARALEGAL = "paralegal"
    CLIENT = "client"
    VIEWER = "viewer"

class DocumentType(str, Enum):
    """Supported document types"""
    CONTRACT = "contract"
    AGREEMENT = "agreement"
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    LEGAL_BRIEF = "legal_brief"
    COMPLIANCE_DOCUMENT = "compliance_document"

class AIModel(str, Enum):
    """Supported AI models"""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    LLAMA_2_70B = "llama-2-70b"
    LLAMA_3_70B = "llama-3-70b"

class AnalysisType(str, Enum):
    """Types of document analysis"""
    RISK_ASSESSMENT = "risk_assessment"
    CLAUSE_EXTRACTION = "clause_extraction"
    COMPLIANCE_CHECK = "compliance_check"
    COMPARISON = "comparison"
    SUMMARIZATION = "summarization"
    NEGOTIATION_POINTS = "negotiation_points"

# User Models
class UserModel(BaseModel):
    """User model for registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.CLIENT
    organization: Optional[str] = None

class UserResponse(BaseModel):
    """User response model"""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    organization: Optional[str]
    created_at: datetime
    is_active: bool

# Document Models
class DocumentUploadRequest(BaseModel):
    """Document upload request"""
    filename: str
    document_type: DocumentType
    description: Optional[str] = None
    tags: List[str] = []

class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    document_id: str
    filename: str
    document_type: DocumentType
    upload_status: str
    processing_status: str
    uploaded_at: datetime

class DocumentAnalysisRequest(BaseModel):
    """Document analysis request"""
    document_id: str
    analysis_type: AnalysisType
    preferred_models: Optional[List[AIModel]] = None
    custom_instructions: Optional[str] = None
    include_confidence_scores: bool = True

class AIModelResponse(BaseModel):
    """Response from individual AI model"""
    model: AIModel
    response: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    processing_time: float
    tokens_used: int

class DocumentAnalysisResponse(BaseModel):
    """Document analysis response with multi-model results"""
    document_id: str
    analysis_type: AnalysisType
    model_responses: List[AIModelResponse]
    consensus_result: str
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    risk_indicators: List[str] = []
    key_clauses: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    processing_time: float
    timestamp: datetime

# Risk Assessment Models
class RiskLevel(str, Enum):
    """Risk levels for contract assessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskFactor(BaseModel):
    """Individual risk factor"""
    category: str
    description: str
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    suggested_action: str

class ContractRiskScore(BaseModel):
    """Contract risk assessment"""
    document_id: str
    overall_risk_level: RiskLevel
    overall_score: float = Field(..., ge=0.0, le=100.0)
    risk_factors: List[RiskFactor]
    compliance_issues: List[str] = []
    legal_concerns: List[str] = []
    financial_risks: List[str] = []
    recommendations: List[str] = []
    assessed_at: datetime

# Collaboration Models
class CommentModel(BaseModel):
    """Comment on document"""
    text: str
    position: Optional[Dict[str, Any]] = None  # Position in document
    document_section: Optional[str] = None

class AnnotationModel(BaseModel):
    """Document annotation"""
    type: str  # highlight, note, suggestion, etc.
    content: str
    position: Dict[str, Any]
    style: Optional[Dict[str, str]] = None

class CollaborationEvent(BaseModel):
    """Real-time collaboration event"""
    event_type: str
    user_id: str
    document_id: str
    data: Dict[str, Any]
    timestamp: datetime

# Analytics Models
class DocumentMetrics(BaseModel):
    """Document processing metrics"""
    total_documents: int
    documents_by_type: Dict[DocumentType, int]
    average_processing_time: float
    success_rate: float

class UserActivity(BaseModel):
    """User activity metrics"""
    documents_processed: int
    time_spent: float  # in hours
    most_used_features: List[str]
    collaboration_events: int

class AnalyticsDashboard(BaseModel):
    """Analytics dashboard data"""
    user_id: str
    time_period: str
    document_metrics: DocumentMetrics
    user_activity: UserActivity
    risk_trends: List[Dict[str, Any]]
    collaboration_stats: Dict[str, Any]
    generated_at: datetime

# Integration Models
class DocuSignRequest(BaseModel):
    """DocuSign integration request"""
    document_id: str
    recipients: List[EmailStr]
    subject: str
    message: Optional[str] = None
    signing_order: Optional[List[str]] = None

class WebhookEvent(BaseModel):
    """Webhook event payload"""
    event_type: str
    source: str
    payload: Dict[str, Any]
    timestamp: datetime

# Voice Integration Models
class VoiceCommand(BaseModel):
    """Voice command for document processing"""
    command_type: str
    audio_data: Optional[str] = None  # Base64 encoded audio
    text: Optional[str] = None  # Transcribed text
    language: str = "en-US"

class VoiceResponse(BaseModel):
    """Voice command response"""
    action_taken: str
    result: str
    audio_response: Optional[str] = None  # Base64 encoded audio response

# Security Models
class AuditLogEntry(BaseModel):
    """Audit log entry"""
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool

class SecurityEvent(BaseModel):
    """Security event for monitoring"""
    event_type: str
    severity: str
    user_id: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime