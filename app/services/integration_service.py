"""
Integration Service - External API Integrations
Handles DocuSign, Microsoft 365, Google Workspace, and webhook integrations
"""

import asyncio
import json
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import httpx

from app.models.schemas import DocuSignRequest, WebhookEvent

logger = logging.getLogger(__name__)

class IntegrationService:
    """Manages external API integrations"""
    
    def __init__(self):
        self.docusign_client = DocuSignClient()
        self.microsoft_client = MicrosoftClient()
        self.google_client = GoogleWorkspaceClient()
        self.webhook_manager = WebhookManager()
        
    async def send_to_docusign(self, document_id: str, recipients: List[str], 
                             user_id: str) -> Dict[str, Any]:
        """Send document to DocuSign for e-signature"""
        try:
            result = await self.docusign_client.send_envelope(
                document_id=document_id,
                recipients=recipients,
                user_id=user_id
            )
            
            # Log integration event
            await self._log_integration_event(
                "docusign_envelope_sent",
                user_id,
                {"document_id": document_id, "envelope_id": result.get("envelope_id")}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"DocuSign integration error: {e}")
            raise
    
    async def sync_with_microsoft365(self, user_id: str, folder_path: str) -> Dict[str, Any]:
        """Sync documents with Microsoft 365"""
        try:
            result = await self.microsoft_client.sync_documents(user_id, folder_path)
            
            await self._log_integration_event(
                "microsoft365_sync",
                user_id,
                {"folder_path": folder_path, "documents_synced": result.get("count", 0)}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Microsoft 365 integration error: {e}")
            raise
    
    async def sync_with_google_workspace(self, user_id: str, drive_folder_id: str) -> Dict[str, Any]:
        """Sync documents with Google Workspace"""
        try:
            result = await self.google_client.sync_documents(user_id, drive_folder_id)
            
            await self._log_integration_event(
                "google_workspace_sync", 
                user_id,
                {"drive_folder_id": drive_folder_id, "documents_synced": result.get("count", 0)}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Google Workspace integration error: {e}")
            raise
    
    async def trigger_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger webhook for external notifications"""
        try:
            webhook_event = WebhookEvent(
                event_type=event_type,
                source="legal_assistant_genai",
                payload=payload,
                timestamp=datetime.utcnow()
            )
            
            result = await self.webhook_manager.send_webhook(webhook_event)
            return result
            
        except Exception as e:
            logger.error(f"Webhook trigger error: {e}")
            raise
    
    async def _log_integration_event(self, event_type: str, user_id: str, data: Dict[str, Any]):
        """Log integration event for monitoring"""
        logger.info(f"Integration event: {event_type} by user {user_id}")
        # In production, save to database for analytics

class DocuSignClient:
    """DocuSign API client for e-signature integration"""
    
    def __init__(self):
        self.base_url = "https://demo.docusign.net/restapi"
        self.account_id = "demo_account"  # Configure from environment
        self.integration_key = "demo_key"  # Configure from environment
        
    async def send_envelope(self, document_id: str, recipients: List[str], 
                          user_id: str) -> Dict[str, Any]:
        """Send document envelope for signature"""
        try:
            # Simulate DocuSign API call
            await asyncio.sleep(1.0)  # Simulate network delay
            
            envelope_id = f"env_{document_id}_{int(datetime.utcnow().timestamp())}"
            
            # Mock envelope creation
            envelope_data = {
                "envelope_id": envelope_id,
                "status": "sent",
                "recipients": [
                    {
                        "email": email,
                        "status": "created",
                        "routing_order": i + 1
                    }
                    for i, email in enumerate(recipients)
                ],
                "documents": [
                    {
                        "document_id": document_id,
                        "name": f"document_{document_id}.pdf"
                    }
                ],
                "sent_datetime": datetime.utcnow().isoformat(),
                "uri": f"/envelopes/{envelope_id}",
                "email_subject": "Please sign: Legal Document",
                "email_blurb": "Please review and sign the attached legal document."
            }
            
            # Simulate webhook notification setup
            await self._setup_envelope_webhooks(envelope_id)
            
            return {
                "success": True,
                "envelope_id": envelope_id,
                "status": "sent",
                "recipients_count": len(recipients),
                "tracking_url": f"https://demo.docusign.net/signing/{envelope_id}",
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"DocuSign envelope creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "created_at": datetime.utcnow().isoformat()
            }
    
    async def get_envelope_status(self, envelope_id: str) -> Dict[str, Any]:
        """Get envelope status from DocuSign"""
        try:
            # Simulate API call
            await asyncio.sleep(0.5)
            
            # Mock status response
            status_data = {
                "envelope_id": envelope_id,
                "status": "completed",  # or "sent", "delivered", "signed", etc.
                "created_datetime": "2024-01-15T10:30:00Z",
                "sent_datetime": "2024-01-15T10:31:00Z",
                "completed_datetime": "2024-01-15T14:22:00Z",
                "recipients": [
                    {
                        "email": "client@company.com",
                        "status": "completed",
                        "signed_datetime": "2024-01-15T14:20:00Z"
                    },
                    {
                        "email": "legal@company.com", 
                        "status": "completed",
                        "signed_datetime": "2024-01-15T14:22:00Z"
                    }
                ]
            }
            
            return status_data
            
        except Exception as e:
            logger.error(f"DocuSign status check failed: {e}")
            raise
    
    async def download_signed_document(self, envelope_id: str, document_id: str) -> bytes:
        """Download signed document from DocuSign"""
        try:
            # Simulate document download
            await asyncio.sleep(1.5)
            
            # Return mock PDF content
            return b"Mock signed PDF content"
            
        except Exception as e:
            logger.error(f"DocuSign document download failed: {e}")
            raise
    
    async def _setup_envelope_webhooks(self, envelope_id: str):
        """Setup webhooks for envelope status updates"""
        # Configure webhook notifications for status changes
        webhook_config = {
            "url": "https://your-app.com/webhooks/docusign",
            "events": ["envelope-sent", "envelope-delivered", "envelope-completed", "envelope-declined"],
            "envelope_id": envelope_id
        }
        
        logger.info(f"Webhook configured for envelope {envelope_id}")

class MicrosoftClient:
    """Microsoft 365 API client"""
    
    def __init__(self):
        self.graph_url = "https://graph.microsoft.com/v1.0"
        self.client_id = "demo_client_id"  # Configure from environment
        self.tenant_id = "demo_tenant_id"  # Configure from environment
        
    async def sync_documents(self, user_id: str, folder_path: str) -> Dict[str, Any]:
        """Sync documents with Microsoft 365"""
        try:
            # Simulate Microsoft Graph API calls
            await asyncio.sleep(1.2)
            
            # Mock document sync
            synced_documents = [
                {
                    "id": "doc_001",
                    "name": "Contract_2024_001.docx",
                    "modified": "2024-01-15T10:30:00Z",
                    "size": 245760,
                    "sync_status": "synced"
                },
                {
                    "id": "doc_002", 
                    "name": "Service_Agreement_Draft.docx",
                    "modified": "2024-01-14T16:45:00Z",
                    "size": 189440,
                    "sync_status": "synced"
                },
                {
                    "id": "doc_003",
                    "name": "NDA_Template.docx",
                    "modified": "2024-01-13T09:15:00Z", 
                    "size": 98304,
                    "sync_status": "synced"
                }
            ]
            
            return {
                "success": True,
                "folder_path": folder_path,
                "documents": synced_documents,
                "count": len(synced_documents),
                "last_sync": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Microsoft 365 sync failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "count": 0
            }
    
    async def create_sharepoint_folder(self, folder_name: str) -> Dict[str, Any]:
        """Create folder in SharePoint"""
        try:
            await asyncio.sleep(0.8)
            
            folder_data = {
                "id": f"folder_{int(datetime.utcnow().timestamp())}",
                "name": folder_name,
                "created": datetime.utcnow().isoformat(),
                "web_url": f"https://tenant.sharepoint.com/sites/legal/Shared%20Documents/{folder_name}",
                "parent_reference": {
                    "drive_id": "b!demo_drive_id",
                    "path": "/drive/root:/Shared Documents"
                }
            }
            
            return {
                "success": True,
                "folder": folder_data
            }
            
        except Exception as e:
            logger.error(f"SharePoint folder creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_teams_notification(self, team_id: str, channel_id: str, 
                                    message: str) -> Dict[str, Any]:
        """Send notification to Microsoft Teams"""
        try:
            await asyncio.sleep(0.5)
            
            notification_data = {
                "id": f"msg_{int(datetime.utcnow().timestamp())}",
                "team_id": team_id,
                "channel_id": channel_id,
                "message": message,
                "sent_datetime": datetime.utcnow().isoformat(),
                "message_type": "message"
            }
            
            return {
                "success": True,
                "notification": notification_data
            }
            
        except Exception as e:
            logger.error(f"Teams notification failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class GoogleWorkspaceClient:
    """Google Workspace API client"""
    
    def __init__(self):
        self.drive_api = "https://www.googleapis.com/drive/v3"
        self.docs_api = "https://docs.googleapis.com/v1"
        self.gmail_api = "https://gmail.googleapis.com/gmail/v1"
        
    async def sync_documents(self, user_id: str, drive_folder_id: str) -> Dict[str, Any]:
        """Sync documents with Google Drive"""
        try:
            # Simulate Google Drive API calls
            await asyncio.sleep(1.0)
            
            # Mock document sync
            synced_documents = [
                {
                    "id": "1abc123def456",
                    "name": "Legal_Agreement_2024.gdoc",
                    "mimeType": "application/vnd.google-apps.document",
                    "modifiedTime": "2024-01-15T10:30:00.000Z",
                    "webViewLink": "https://docs.google.com/document/d/1abc123def456",
                    "sync_status": "synced"
                },
                {
                    "id": "2def456ghi789",
                    "name": "Contract_Template.gdoc", 
                    "mimeType": "application/vnd.google-apps.document",
                    "modifiedTime": "2024-01-14T15:20:00.000Z",
                    "webViewLink": "https://docs.google.com/document/d/2def456ghi789",
                    "sync_status": "synced"
                }
            ]
            
            return {
                "success": True,
                "drive_folder_id": drive_folder_id,
                "documents": synced_documents,
                "count": len(synced_documents),
                "last_sync": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Google Drive sync failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "count": 0
            }
    
    async def create_google_doc(self, title: str, content: str) -> Dict[str, Any]:
        """Create new Google Doc"""
        try:
            await asyncio.sleep(1.0)
            
            doc_data = {
                "documentId": f"doc_{int(datetime.utcnow().timestamp())}",
                "title": title,
                "revisionId": "1",
                "webViewLink": f"https://docs.google.com/document/d/doc_{int(datetime.utcnow().timestamp())}",
                "createdTime": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "document": doc_data
            }
            
        except Exception as e:
            logger.error(f"Google Doc creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_gmail_notification(self, to_email: str, subject: str, 
                                    body: str) -> Dict[str, Any]:
        """Send email notification via Gmail API"""
        try:
            await asyncio.sleep(0.7)
            
            email_data = {
                "id": f"email_{int(datetime.utcnow().timestamp())}",
                "threadId": f"thread_{int(datetime.utcnow().timestamp())}",
                "labelIds": ["SENT"],
                "to": to_email,
                "subject": subject,
                "sent_datetime": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "email": email_data
            }
            
        except Exception as e:
            logger.error(f"Gmail notification failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class WebhookManager:
    """Webhook management for external notifications"""
    
    def __init__(self):
        self.webhook_endpoints = {}
        self.retry_config = {
            "max_retries": 3,
            "retry_delay": 5,  # seconds
            "timeout": 30
        }
    
    async def send_webhook(self, webhook_event: WebhookEvent) -> Dict[str, Any]:
        """Send webhook to registered endpoints"""
        try:
            # Get registered webhooks for this event type
            endpoints = self.webhook_endpoints.get(webhook_event.event_type, [])
            
            if not endpoints:
                logger.info(f"No webhook endpoints registered for event: {webhook_event.event_type}")
                return {"sent": False, "reason": "no_endpoints"}
            
            results = []
            
            for endpoint in endpoints:
                result = await self._send_to_endpoint(endpoint, webhook_event)
                results.append(result)
            
            return {
                "sent": True,
                "event_type": webhook_event.event_type,
                "endpoints_notified": len(endpoints),
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Webhook sending failed: {e}")
            return {
                "sent": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _send_to_endpoint(self, endpoint: Dict[str, Any], 
                              webhook_event: WebhookEvent) -> Dict[str, Any]:
        """Send webhook to specific endpoint with retries"""
        url = endpoint.get("url")
        headers = endpoint.get("headers", {})
        headers["Content-Type"] = "application/json"
        
        payload = {
            "event_type": webhook_event.event_type,
            "source": webhook_event.source,
            "payload": webhook_event.payload,
            "timestamp": webhook_event.timestamp.isoformat(),
            "webhook_id": f"wh_{int(datetime.utcnow().timestamp())}"
        }
        
        for attempt in range(self.retry_config["max_retries"]):
            try:
                async with httpx.AsyncClient(timeout=self.retry_config["timeout"]) as client:
                    response = await client.post(
                        url,
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201, 202]:
                        return {
                            "endpoint": url,
                            "status": "success",
                            "status_code": response.status_code,
                            "attempt": attempt + 1
                        }
                    else:
                        logger.warning(f"Webhook endpoint returned {response.status_code}: {url}")
                        
            except Exception as e:
                logger.warning(f"Webhook attempt {attempt + 1} failed for {url}: {e}")
                
                if attempt < self.retry_config["max_retries"] - 1:
                    await asyncio.sleep(self.retry_config["retry_delay"])
        
        return {
            "endpoint": url,
            "status": "failed",
            "attempts": self.retry_config["max_retries"],
            "last_error": "Max retries exceeded"
        }
    
    async def register_webhook(self, event_type: str, url: str, 
                             headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Register webhook endpoint for event type"""
        try:
            if event_type not in self.webhook_endpoints:
                self.webhook_endpoints[event_type] = []
            
            endpoint_config = {
                "url": url,
                "headers": headers or {},
                "registered_at": datetime.utcnow().isoformat(),
                "active": True
            }
            
            self.webhook_endpoints[event_type].append(endpoint_config)
            
            return {
                "success": True,
                "event_type": event_type,
                "endpoint": url,
                "registered_at": endpoint_config["registered_at"]
            }
            
        except Exception as e:
            logger.error(f"Webhook registration failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def unregister_webhook(self, event_type: str, url: str) -> Dict[str, Any]:
        """Unregister webhook endpoint"""
        try:
            if event_type in self.webhook_endpoints:
                self.webhook_endpoints[event_type] = [
                    endpoint for endpoint in self.webhook_endpoints[event_type]
                    if endpoint["url"] != url
                ]
                
                return {
                    "success": True,
                    "event_type": event_type,
                    "endpoint": url,
                    "unregistered_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Event type not found"
                }
                
        except Exception as e:
            logger.error(f"Webhook unregistration failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_registered_webhooks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all registered webhook endpoints"""
        return self.webhook_endpoints.copy()