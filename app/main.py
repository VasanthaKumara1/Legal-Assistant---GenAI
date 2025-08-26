"""
Legal Assistant GenAI - Main FastAPI Application
Enhanced AI Legal Assistant with advanced features
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services
from app.services.ai_orchestrator import AIOrchestrator
from app.services.document_processor import DocumentProcessor
from app.services.security_manager import SecurityManager
from app.services.collaboration_manager import CollaborationManager
from app.services.analytics_service import AnalyticsService
from app.services.integration_service import IntegrationService

# Import models
from app.models.schemas import (
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    ContractRiskScore,
    UserModel,
    UserResponse,
    DocuSignRequest,
    VoiceCommand,
    VoiceResponse,
    AnalysisType,
    AIModel
)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Assistant GenAI",
    description="Enhanced AI Legal Assistant with advanced features",
    version="1.5.0",
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

# Security
security = HTTPBearer()

# Initialize services
ai_orchestrator = AIOrchestrator()
document_processor = DocumentProcessor()
security_manager = SecurityManager()
collaboration_manager = CollaborationManager()
analytics_service = AnalyticsService()
integration_service = IntegrationService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Legal Assistant GenAI application...")
    await ai_orchestrator.initialize()
    await document_processor.initialize()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Legal Assistant GenAI application...")
    await ai_orchestrator.cleanup()
    await document_processor.cleanup()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.5.0",
        "services": {
            "ai_orchestrator": "active",
            "document_processor": "active",
            "security_manager": "active",
            "collaboration_manager": "active",
            "analytics_service": "active",
            "integration_service": "active"
        }
    }

# Authentication endpoints
@app.post("/auth/login")
async def login(credentials: dict):
    """Authenticate user and return JWT token"""
    try:
        token = await security_manager.authenticate_user(
            credentials.get("username"),
            credentials.get("password"),
            credentials.get("mfa_code")
        )
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserModel):
    """Register new user"""
    try:
        user = await security_manager.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/enable-mfa")
async def enable_mfa(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Enable multi-factor authentication"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        mfa_setup = await security_manager.enable_mfa(user.id)
        return mfa_setup
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Document processing endpoints
@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload and process legal document"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        result = await document_processor.process_upload(file, user.id)
        
        return {
            "document_id": result.get("document_id"),
            "filename": file.filename,
            "status": "uploaded",
            "processing_status": "completed",
            "extraction_result": result.get("extraction_result")
        }
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Document upload failed")

@app.post("/documents/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    request: DocumentAnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Analyze legal document using AI orchestration"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        
        analysis = await ai_orchestrator.analyze_document(
            document_id=request.document_id,
            analysis_type=request.analysis_type,
            models=request.preferred_models or [AIModel.GPT_4, AIModel.CLAUDE_3_OPUS],
            custom_instructions=request.custom_instructions
        )
        
        return analysis
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Document analysis failed")

@app.get("/documents/{document_id}/risk-score", response_model=ContractRiskScore)
async def get_risk_score(
    document_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get AI-powered contract risk assessment"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        risk_score = await ai_orchestrator.calculate_risk_score(document_id)
        return risk_score
    except Exception as e:
        logger.error(f"Risk score calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Risk score calculation failed")

@app.post("/documents/{document_id}/extract-tables")
async def extract_tables(
    document_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Extract tables from document with advanced formatting"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        # Mock file path for demo
        file_path = f"/tmp/uploads/{document_id}.pdf"
        tables = await document_processor.extract_tables_advanced(file_path)
        return {"document_id": document_id, "tables": tables}
    except Exception as e:
        logger.error(f"Table extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Table extraction failed")

@app.post("/documents/{document_id}/detect-signatures")
async def detect_signatures(
    document_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Detect and validate signatures in document"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        # Mock file path for demo
        file_path = f"/tmp/uploads/{document_id}.pdf"
        signatures = await document_processor.detect_signatures_advanced(file_path)
        return {"document_id": document_id, "signatures": signatures}
    except Exception as e:
        logger.error(f"Signature detection error: {str(e)}")
        raise HTTPException(status_code=500, detail="Signature detection failed")

# Real-time collaboration endpoints
@app.websocket("/ws/collaborate/{document_id}")
async def websocket_collaboration(websocket: WebSocket, document_id: str, token: str):
    """WebSocket endpoint for real-time document collaboration"""
    try:
        user = await security_manager.validate_token(token)
        await collaboration_manager.handle_connection(websocket, document_id, user.id)
    except Exception as e:
        logger.error(f"WebSocket collaboration error: {str(e)}")
        await websocket.close(code=1000)

@app.get("/collaboration/{document_id}/users")
async def get_document_collaborators(
    document_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get list of current collaborators for a document"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        collaborators = await collaboration_manager.get_document_collaborators(document_id)
        return {"document_id": document_id, "collaborators": collaborators}
    except Exception as e:
        logger.error(f"Get collaborators error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get collaborators")

# Analytics endpoints
@app.get("/analytics/dashboard")
async def get_analytics_dashboard(
    time_period: str = "30_days",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get analytics dashboard data"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        dashboard_data = await analytics_service.get_dashboard_data(user.id, time_period)
        return dashboard_data
    except Exception as e:
        logger.error(f"Analytics dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analytics data retrieval failed")

@app.get("/analytics/risk-heatmap")
async def get_risk_heatmap(
    documents: List[str] = [],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate contract risk assessment heatmap"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        if not documents:
            documents = ["Contract_001", "Agreement_002", "NDA_003", "SLA_004"]
        
        heatmap_data = await analytics_service.calculate_contract_risk_heatmap(documents)
        return heatmap_data
    except Exception as e:
        logger.error(f"Risk heatmap error: {str(e)}")
        raise HTTPException(status_code=500, detail="Risk heatmap generation failed")

@app.get("/analytics/negotiation-timeline/{contract_id}")
async def get_negotiation_timeline(
    contract_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get negotiation timeline for contract"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        timeline = await analytics_service.track_negotiation_timeline(contract_id)
        return timeline
    except Exception as e:
        logger.error(f"Negotiation timeline error: {str(e)}")
        raise HTTPException(status_code=500, detail="Timeline retrieval failed")

@app.post("/analytics/find-precedents")
async def find_contract_precedents(
    contract_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Find similar contracts and legal precedents"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        precedents = await analytics_service.find_contract_precedents(
            contract_data.get("text", ""),
            contract_data.get("type", "contract")
        )
        return {"precedents": precedents}
    except Exception as e:
        logger.error(f"Precedent search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Precedent search failed")

@app.post("/analytics/predictive")
async def get_predictive_analytics(
    contract_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate predictive analytics for contract outcomes"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        predictions = await analytics_service.generate_predictive_analytics(contract_data)
        return predictions
    except Exception as e:
        logger.error(f"Predictive analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Predictive analytics failed")

# Integration endpoints
@app.post("/integrations/docusign/send")
async def send_to_docusign(
    request: DocuSignRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Send document to DocuSign for e-signature"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        result = await integration_service.send_to_docusign(
            request.document_id, request.recipients, user.id
        )
        return result
    except Exception as e:
        logger.error(f"DocuSign integration error: {str(e)}")
        raise HTTPException(status_code=500, detail="DocuSign integration failed")

@app.post("/integrations/microsoft365/sync")
async def sync_microsoft365(
    folder_path: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Sync documents with Microsoft 365"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        result = await integration_service.sync_with_microsoft365(user.id, folder_path)
        return result
    except Exception as e:
        logger.error(f"Microsoft 365 sync error: {str(e)}")
        raise HTTPException(status_code=500, detail="Microsoft 365 sync failed")

@app.post("/integrations/google-workspace/sync")
async def sync_google_workspace(
    drive_folder_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Sync documents with Google Workspace"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        result = await integration_service.sync_with_google_workspace(user.id, drive_folder_id)
        return result
    except Exception as e:
        logger.error(f"Google Workspace sync error: {str(e)}")
        raise HTTPException(status_code=500, detail="Google Workspace sync failed")

@app.post("/integrations/webhook")
async def trigger_webhook(
    event_type: str,
    payload: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Trigger webhook for external notifications"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        result = await integration_service.trigger_webhook(event_type, payload)
        return result
    except Exception as e:
        logger.error(f"Webhook trigger error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook trigger failed")

# Voice integration endpoints
@app.post("/voice/command", response_model=VoiceResponse)
async def process_voice_command(
    command: VoiceCommand,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Process voice command for document analysis"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        
        # Mock voice processing
        response_text = f"Processing voice command: {command.command_type}"
        if command.text:
            response_text += f" - '{command.text}'"
        
        return VoiceResponse(
            action_taken=command.command_type,
            result=response_text,
            audio_response=None  # Would generate audio in production
        )
    except Exception as e:
        logger.error(f"Voice command error: {str(e)}")
        raise HTTPException(status_code=500, detail="Voice command processing failed")

# Security endpoints
@app.get("/security/audit-logs")
async def get_audit_logs(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get audit logs for compliance"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        # Only admins can view all audit logs
        if not await security_manager.check_permissions(user.id, "audit:view"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        logs = await security_manager.get_audit_logs()
        return {"audit_logs": logs}
    except Exception as e:
        logger.error(f"Audit logs error: {str(e)}")
        raise HTTPException(status_code=500, detail="Audit logs retrieval failed")

@app.get("/security/events")
async def get_security_events(
    severity: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get security events"""
    try:
        user = await security_manager.validate_token(credentials.credentials)
        if not await security_manager.check_permissions(user.id, "admin:system"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        events = await security_manager.get_security_events(severity)
        return {"security_events": events}
    except Exception as e:
        logger.error(f"Security events error: {str(e)}")
        raise HTTPException(status_code=500, detail="Security events retrieval failed")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Legal Assistant GenAI - Enhanced AI Legal Assistant",
        "version": "1.5.0",
        "features": [
            "Multi-Model AI Integration",
            "Advanced OCR & Document Processing", 
            "Real-time Collaboration",
            "Enhanced Security & Authentication",
            "Advanced Analytics Dashboard",
            "Integration Ecosystem",
            "Voice Integration & Accessibility",
            "Mobile-First Experience"
        ],
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )