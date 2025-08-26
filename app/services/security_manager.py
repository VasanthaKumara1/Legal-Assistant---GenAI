"""
Security Manager Service - Enhanced Security & Authentication
Handles MFA, RBAC, audit trails, and encryption
"""

import hashlib
import secrets
import time
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import jwt
from passlib.context import CryptContext

from app.models.schemas import UserModel, UserResponse, UserRole, AuditLogEntry, SecurityEvent

logger = logging.getLogger(__name__)

class SecurityManager:
    """Enhanced security manager with MFA, RBAC, and audit trails"""
    
    def __init__(self):
        self.secret_key = "your-secret-key-change-in-production"  # Should be from environment
        self.algorithm = "HS256"
        self.token_expire_hours = 24
        self.refresh_token_expire_days = 7
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # In-memory storage for demo (use database in production)
        self.users_db = {}
        self.sessions_db = {}
        self.audit_logs = []
        self.security_events = []
        self.mfa_codes = {}
        
        # Role-based permissions
        self.role_permissions = {
            UserRole.ADMIN: [
                "read:all", "write:all", "delete:all", "admin:users", 
                "admin:system", "audit:view"
            ],
            UserRole.LAWYER: [
                "read:documents", "write:documents", "analyze:documents",
                "collaborate:documents", "negotiate:contracts"
            ],
            UserRole.PARALEGAL: [
                "read:documents", "write:documents", "analyze:documents",
                "collaborate:documents"
            ],
            UserRole.CLIENT: [
                "read:own_documents", "write:own_documents", "view:analysis"
            ],
            UserRole.VIEWER: [
                "read:shared_documents", "view:analysis"
            ]
        }
    
    async def create_user(self, user_data: UserModel) -> UserResponse:
        """Create new user with security validation"""
        try:
            # Validate password strength
            await self._validate_password_strength(user_data.password)
            
            # Check if username/email already exists
            if await self._user_exists(user_data.username, user_data.email):
                raise ValueError("Username or email already exists")
            
            # Generate user ID
            user_id = str(uuid.uuid4())
            
            # Hash password
            password_hash = self.pwd_context.hash(user_data.password)
            
            # Create user record
            user_record = {
                'id': user_id,
                'username': user_data.username,
                'email': user_data.email,
                'password_hash': password_hash,
                'full_name': user_data.full_name,
                'role': user_data.role,
                'organization': user_data.organization,
                'created_at': datetime.utcnow(),
                'is_active': True,
                'mfa_enabled': False,
                'failed_login_attempts': 0,
                'last_login': None
            }
            
            self.users_db[user_id] = user_record
            
            # Log security event
            await self._log_security_event(
                event_type="user_created",
                severity="info",
                user_id=user_id,
                details={"username": user_data.username, "role": user_data.role.value}
            )
            
            return UserResponse(
                id=user_id,
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                role=user_data.role,
                organization=user_data.organization,
                created_at=user_record['created_at'],
                is_active=True
            )
            
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str, 
                              mfa_code: str = None, ip_address: str = None) -> str:
        """Authenticate user with optional MFA"""
        try:
            # Find user
            user = await self._find_user_by_username(username)
            if not user:
                await self._log_failed_login(username, ip_address, "user_not_found")
                raise ValueError("Invalid credentials")
            
            # Check if account is locked
            if user['failed_login_attempts'] >= 5:
                await self._log_security_event(
                    event_type="account_locked",
                    severity="warning",
                    user_id=user['id'],
                    details={"reason": "too_many_failed_attempts", "ip_address": ip_address}
                )
                raise ValueError("Account locked due to too many failed attempts")
            
            # Verify password
            if not self.pwd_context.verify(password, user['password_hash']):
                user['failed_login_attempts'] += 1
                await self._log_failed_login(username, ip_address, "invalid_password")
                raise ValueError("Invalid credentials")
            
            # Check MFA if enabled
            if user['mfa_enabled']:
                if not mfa_code:
                    raise ValueError("MFA code required")
                if not await self._verify_mfa_code(user['id'], mfa_code):
                    await self._log_failed_login(username, ip_address, "invalid_mfa")
                    raise ValueError("Invalid MFA code")
            
            # Reset failed attempts on successful login
            user['failed_login_attempts'] = 0
            user['last_login'] = datetime.utcnow()
            
            # Generate JWT token
            token = await self._generate_token(user['id'], user['role'])
            
            # Log successful login
            await self._log_audit_event(
                user_id=user['id'],
                action="login",
                resource="auth",
                details={"ip_address": ip_address, "mfa_used": user['mfa_enabled']},
                ip_address=ip_address or "unknown",
                success=True
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    async def validate_token(self, token: str) -> UserResponse:
        """Validate JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("user_id")
            
            if not user_id:
                raise ValueError("Invalid token")
            
            user = self.users_db.get(user_id)
            if not user or not user['is_active']:
                raise ValueError("User not found or inactive")
            
            return UserResponse(
                id=user['id'],
                username=user['username'],
                email=user['email'],
                full_name=user['full_name'],
                role=UserRole(user['role']),
                organization=user['organization'],
                created_at=user['created_at'],
                is_active=user['is_active']
            )
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.JWTError:
            raise ValueError("Invalid token")
    
    async def enable_mfa(self, user_id: str) -> Dict[str, str]:
        """Enable multi-factor authentication for user"""
        user = self.users_db.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Generate MFA secret (in production, use proper TOTP library)
        mfa_secret = secrets.token_hex(16)
        user['mfa_secret'] = mfa_secret
        user['mfa_enabled'] = True
        
        # Log security event
        await self._log_security_event(
            event_type="mfa_enabled",
            severity="info",
            user_id=user_id,
            details={"method": "totp"}
        )
        
        return {
            "secret": mfa_secret,
            "qr_code_url": f"otpauth://totp/LegalAssistant:{user['username']}?secret={mfa_secret}&issuer=LegalAssistant"
        }
    
    async def check_permissions(self, user_id: str, required_permission: str) -> bool:
        """Check if user has required permission (RBAC)"""
        user = self.users_db.get(user_id)
        if not user:
            return False
        
        user_role = UserRole(user['role'])
        user_permissions = self.role_permissions.get(user_role, [])
        
        # Check for exact permission or wildcard
        return (required_permission in user_permissions or 
                "write:all" in user_permissions or
                "read:all" in user_permissions)
    
    async def log_audit_event(self, user_id: str, action: str, resource: str,
                            details: Dict[str, Any], ip_address: str,
                            user_agent: str = "", success: bool = True):
        """Log audit event for compliance"""
        await self._log_audit_event(user_id, action, resource, details, 
                                   ip_address, user_agent, success)
    
    async def encrypt_document(self, document_content: bytes, user_id: str) -> Dict[str, Any]:
        """Encrypt document with user-specific key"""
        # Simulate encryption (use proper encryption in production)
        key = hashlib.sha256(f"{user_id}{self.secret_key}".encode()).hexdigest()
        
        # In production, use AES encryption
        encrypted_content = document_content  # Placeholder
        
        return {
            "encrypted_content": encrypted_content,
            "encryption_key_id": f"key_{user_id}",
            "algorithm": "AES-256-GCM",
            "encrypted_at": datetime.utcnow().isoformat()
        }
    
    async def decrypt_document(self, encrypted_data: Dict[str, Any], user_id: str) -> bytes:
        """Decrypt document with user-specific key"""
        # Simulate decryption
        return encrypted_data["encrypted_content"]
    
    async def get_audit_logs(self, user_id: str = None, 
                           start_date: datetime = None,
                           end_date: datetime = None) -> List[AuditLogEntry]:
        """Retrieve audit logs with filtering"""
        filtered_logs = []
        
        for log in self.audit_logs:
            # Filter by user if specified
            if user_id and log.user_id != user_id:
                continue
            
            # Filter by date range if specified
            if start_date and log.timestamp < start_date:
                continue
            if end_date and log.timestamp > end_date:
                continue
            
            filtered_logs.append(log)
        
        return filtered_logs[-100:]  # Return last 100 logs
    
    async def get_security_events(self, severity: str = None) -> List[SecurityEvent]:
        """Retrieve security events"""
        if severity:
            return [event for event in self.security_events 
                   if event.severity == severity]
        return self.security_events[-50:]  # Return last 50 events
    
    # Private methods
    async def _validate_password_strength(self, password: str):
        """Validate password meets security requirements"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            raise ValueError("Password must contain at least one special character")
    
    async def _user_exists(self, username: str, email: str) -> bool:
        """Check if user with username or email already exists"""
        for user in self.users_db.values():
            if user['username'] == username or user['email'] == email:
                return True
        return False
    
    async def _find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user by username"""
        for user in self.users_db.values():
            if user['username'] == username:
                return user
        return None
    
    async def _generate_token(self, user_id: str, role: UserRole) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "role": role.value,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def _verify_mfa_code(self, user_id: str, code: str) -> bool:
        """Verify MFA code (simplified for demo)"""
        # In production, use proper TOTP verification
        stored_code = self.mfa_codes.get(user_id)
        return stored_code == code
    
    async def _log_audit_event(self, user_id: str, action: str, resource: str,
                             details: Dict[str, Any], ip_address: str,
                             user_agent: str = "", success: bool = True):
        """Log audit event"""
        audit_entry = AuditLogEntry(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            success=success
        )
        
        self.audit_logs.append(audit_entry)
        logger.info(f"Audit log: {action} on {resource} by {user_id}")
    
    async def _log_security_event(self, event_type: str, severity: str,
                                user_id: str = None, details: Dict[str, Any] = None):
        """Log security event"""
        security_event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            details=details or {},
            timestamp=datetime.utcnow()
        )
        
        self.security_events.append(security_event)
        logger.warning(f"Security event: {event_type} - {severity}")
    
    async def _log_failed_login(self, username: str, ip_address: str, reason: str):
        """Log failed login attempt"""
        await self._log_security_event(
            event_type="failed_login",
            severity="warning",
            details={
                "username": username,
                "ip_address": ip_address,
                "reason": reason
            }
        )