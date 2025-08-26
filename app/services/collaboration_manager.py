"""
Collaboration Manager Service - Real-time Collaboration Features
Handles WebSocket connections, live editing, comments, and user presence
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Set
from datetime import datetime
import logging
from fastapi import WebSocket, WebSocketDisconnect

from app.models.schemas import CollaborationEvent, CommentModel, AnnotationModel

logger = logging.getLogger(__name__)

class CollaborationManager:
    """Manages real-time collaboration features"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.document_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_presence: Dict[str, Dict[str, Any]] = {}
        self.document_locks: Dict[str, str] = {}  # document_id -> user_id
        
    async def handle_connection(self, websocket: WebSocket, document_id: str, user_id: str):
        """Handle new WebSocket connection for collaboration"""
        try:
            await websocket.accept()
            
            # Add to active connections
            if document_id not in self.active_connections:
                self.active_connections[document_id] = []
            self.active_connections[document_id].append(websocket)
            
            # Initialize document session if needed
            if document_id not in self.document_sessions:
                self.document_sessions[document_id] = {
                    'users': set(),
                    'comments': [],
                    'annotations': [],
                    'version': 1,
                    'last_edit': None
                }
            
            # Add user to session
            self.document_sessions[document_id]['users'].add(user_id)
            
            # Update user presence
            self.user_presence[user_id] = {
                'document_id': document_id,
                'last_activity': datetime.utcnow(),
                'status': 'active'
            }
            
            # Notify other users of new connection
            await self._broadcast_user_joined(document_id, user_id)
            
            # Send current document state to new user
            await self._send_document_state(websocket, document_id)
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_collaboration_message(websocket, document_id, user_id, message)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error handling collaboration message: {e}")
                    await websocket.send_text(json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
                    
        except Exception as e:
            logger.error(f"Collaboration connection error: {e}")
        finally:
            await self._handle_disconnect(websocket, document_id, user_id)
    
    async def _handle_collaboration_message(self, websocket: WebSocket, document_id: str, 
                                          user_id: str, message: Dict[str, Any]):
        """Handle incoming collaboration message"""
        message_type = message.get('type')
        
        if message_type == 'text_change':
            await self._handle_text_change(document_id, user_id, message)
        elif message_type == 'comment':
            await self._handle_comment(document_id, user_id, message)
        elif message_type == 'annotation':
            await self._handle_annotation(document_id, user_id, message)
        elif message_type == 'cursor_position':
            await self._handle_cursor_position(document_id, user_id, message)
        elif message_type == 'request_lock':
            await self._handle_lock_request(document_id, user_id, message)
        elif message_type == 'release_lock':
            await self._handle_lock_release(document_id, user_id)
        elif message_type == 'heartbeat':
            await self._handle_heartbeat(user_id)
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def _handle_text_change(self, document_id: str, user_id: str, message: Dict[str, Any]):
        """Handle real-time text changes"""
        try:
            # Update document version
            if document_id in self.document_sessions:
                self.document_sessions[document_id]['version'] += 1
                self.document_sessions[document_id]['last_edit'] = {
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'change': message.get('change', {})
                }
            
            # Broadcast change to other users
            change_event = {
                'type': 'text_change',
                'user_id': user_id,
                'change': message.get('change', {}),
                'version': self.document_sessions[document_id]['version'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self._broadcast_to_document(document_id, change_event, exclude_user=user_id)
            
            # Log collaboration event
            await self._log_collaboration_event(
                event_type="text_change",
                user_id=user_id,
                document_id=document_id,
                data=message.get('change', {})
            )
            
        except Exception as e:
            logger.error(f"Error handling text change: {e}")
    
    async def _handle_comment(self, document_id: str, user_id: str, message: Dict[str, Any]):
        """Handle comment addition"""
        try:
            comment_data = message.get('comment', {})
            
            comment = {
                'id': f"comment_{int(time.time())}_{user_id}",
                'user_id': user_id,
                'text': comment_data.get('text', ''),
                'position': comment_data.get('position', {}),
                'timestamp': datetime.utcnow().isoformat(),
                'resolved': False
            }
            
            # Add to document session
            if document_id in self.document_sessions:
                self.document_sessions[document_id]['comments'].append(comment)
            
            # Broadcast comment to other users
            comment_event = {
                'type': 'new_comment',
                'comment': comment,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self._broadcast_to_document(document_id, comment_event)
            
            # Log collaboration event
            await self._log_collaboration_event(
                event_type="comment_added",
                user_id=user_id,
                document_id=document_id,
                data={'comment_id': comment['id'], 'text': comment['text']}
            )
            
        except Exception as e:
            logger.error(f"Error handling comment: {e}")
    
    async def _handle_annotation(self, document_id: str, user_id: str, message: Dict[str, Any]):
        """Handle annotation addition"""
        try:
            annotation_data = message.get('annotation', {})
            
            annotation = {
                'id': f"annotation_{int(time.time())}_{user_id}",
                'user_id': user_id,
                'type': annotation_data.get('type', 'highlight'),
                'content': annotation_data.get('content', ''),
                'position': annotation_data.get('position', {}),
                'style': annotation_data.get('style', {}),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Add to document session
            if document_id in self.document_sessions:
                self.document_sessions[document_id]['annotations'].append(annotation)
            
            # Broadcast annotation to other users
            annotation_event = {
                'type': 'new_annotation',
                'annotation': annotation,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self._broadcast_to_document(document_id, annotation_event)
            
        except Exception as e:
            logger.error(f"Error handling annotation: {e}")
    
    async def _handle_cursor_position(self, document_id: str, user_id: str, message: Dict[str, Any]):
        """Handle cursor position updates"""
        try:
            cursor_event = {
                'type': 'cursor_position',
                'user_id': user_id,
                'position': message.get('position', {}),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self._broadcast_to_document(document_id, cursor_event, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling cursor position: {e}")
    
    async def _handle_lock_request(self, document_id: str, user_id: str, message: Dict[str, Any]):
        """Handle document section lock request"""
        try:
            section = message.get('section', 'document')
            lock_key = f"{document_id}_{section}"
            
            # Check if section is already locked
            if lock_key in self.document_locks:
                # Deny lock request
                lock_response = {
                    'type': 'lock_denied',
                    'section': section,
                    'locked_by': self.document_locks[lock_key],
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                # Grant lock
                self.document_locks[lock_key] = user_id
                lock_response = {
                    'type': 'lock_granted',
                    'section': section,
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Notify other users about the lock
                await self._broadcast_to_document(document_id, lock_response, exclude_user=user_id)
            
            # Send response to requesting user
            connections = self.active_connections.get(document_id, [])
            user_websocket = None
            # In production, you'd maintain user-websocket mapping
            for websocket in connections:
                await websocket.send_text(json.dumps(lock_response))
                break
            
        except Exception as e:
            logger.error(f"Error handling lock request: {e}")
    
    async def _handle_lock_release(self, document_id: str, user_id: str):
        """Handle lock release"""
        try:
            # Find and release locks held by this user
            locks_to_release = []
            for lock_key, lock_user in self.document_locks.items():
                if lock_user == user_id and lock_key.startswith(document_id):
                    locks_to_release.append(lock_key)
            
            for lock_key in locks_to_release:
                del self.document_locks[lock_key]
                section = lock_key.split(f"{document_id}_")[1]
                
                # Notify other users about lock release
                lock_release_event = {
                    'type': 'lock_released',
                    'section': section,
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await self._broadcast_to_document(document_id, lock_release_event)
            
        except Exception as e:
            logger.error(f"Error handling lock release: {e}")
    
    async def _handle_heartbeat(self, user_id: str):
        """Handle user heartbeat to maintain presence"""
        if user_id in self.user_presence:
            self.user_presence[user_id]['last_activity'] = datetime.utcnow()
            self.user_presence[user_id]['status'] = 'active'
    
    async def _broadcast_user_joined(self, document_id: str, user_id: str):
        """Broadcast user joined event"""
        join_event = {
            'type': 'user_joined',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_document(document_id, join_event, exclude_user=user_id)
    
    async def _send_document_state(self, websocket: WebSocket, document_id: str):
        """Send current document state to user"""
        try:
            if document_id in self.document_sessions:
                session = self.document_sessions[document_id]
                
                state = {
                    'type': 'document_state',
                    'version': session.get('version', 1),
                    'comments': session.get('comments', []),
                    'annotations': session.get('annotations', []),
                    'active_users': list(session.get('users', set())),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await websocket.send_text(json.dumps(state))
            
        except Exception as e:
            logger.error(f"Error sending document state: {e}")
    
    async def _broadcast_to_document(self, document_id: str, message: Dict[str, Any], 
                                   exclude_user: str = None):
        """Broadcast message to all users in document session"""
        try:
            if document_id in self.active_connections:
                message_str = json.dumps(message)
                
                # Send to all connected websockets for this document
                disconnected_websockets = []
                for websocket in self.active_connections[document_id]:
                    try:
                        await websocket.send_text(message_str)
                    except Exception as e:
                        logger.warning(f"Failed to send message to websocket: {e}")
                        disconnected_websockets.append(websocket)
                
                # Remove disconnected websockets
                for websocket in disconnected_websockets:
                    self.active_connections[document_id].remove(websocket)
            
        except Exception as e:
            logger.error(f"Error broadcasting to document: {e}")
    
    async def _handle_disconnect(self, websocket: WebSocket, document_id: str, user_id: str):
        """Handle user disconnect"""
        try:
            # Remove from active connections
            if document_id in self.active_connections:
                if websocket in self.active_connections[document_id]:
                    self.active_connections[document_id].remove(websocket)
                
                # Remove document session if no more connections
                if not self.active_connections[document_id]:
                    del self.active_connections[document_id]
            
            # Remove from document session
            if document_id in self.document_sessions:
                self.document_sessions[document_id]['users'].discard(user_id)
                
                # Clean up session if no more users
                if not self.document_sessions[document_id]['users']:
                    del self.document_sessions[document_id]
            
            # Release any locks held by this user
            await self._handle_lock_release(document_id, user_id)
            
            # Update user presence
            if user_id in self.user_presence:
                self.user_presence[user_id]['status'] = 'offline'
            
            # Notify other users
            disconnect_event = {
                'type': 'user_left',
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self._broadcast_to_document(document_id, disconnect_event)
            
            logger.info(f"User {user_id} disconnected from document {document_id}")
            
        except Exception as e:
            logger.error(f"Error handling disconnect: {e}")
    
    async def _log_collaboration_event(self, event_type: str, user_id: str, 
                                     document_id: str, data: Dict[str, Any]):
        """Log collaboration event for analytics"""
        event = CollaborationEvent(
            event_type=event_type,
            user_id=user_id,
            document_id=document_id,
            data=data,
            timestamp=datetime.utcnow()
        )
        
        # In production, save to database
        logger.info(f"Collaboration event: {event_type} by {user_id} on {document_id}")
    
    async def get_document_collaborators(self, document_id: str) -> List[Dict[str, Any]]:
        """Get list of current collaborators for a document"""
        if document_id in self.document_sessions:
            users = self.document_sessions[document_id]['users']
            collaborators = []
            
            for user_id in users:
                presence = self.user_presence.get(user_id, {})
                collaborators.append({
                    'user_id': user_id,
                    'status': presence.get('status', 'unknown'),
                    'last_activity': presence.get('last_activity', '').isoformat() if presence.get('last_activity') else None
                })
            
            return collaborators
        
        return []
    
    async def resolve_version_conflict(self, document_id: str, conflicting_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve version conflicts using operational transformation"""
        try:
            # Simple conflict resolution (in production, use sophisticated OT algorithms)
            resolved_changes = []
            
            # Sort changes by timestamp
            sorted_changes = sorted(conflicting_changes, key=lambda x: x.get('timestamp', ''))
            
            for change in sorted_changes:
                # Apply basic transformation
                transformed_change = self._transform_change(change, resolved_changes)
                resolved_changes.append(transformed_change)
            
            return {
                'status': 'resolved',
                'resolved_changes': resolved_changes,
                'resolution_strategy': 'chronological_ordering',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error resolving version conflict: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _transform_change(self, change: Dict[str, Any], previous_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform change based on previous changes (simplified OT)"""
        # Simplified operational transformation
        # In production, implement proper OT algorithms
        
        transformed_change = change.copy()
        
        # Adjust position based on previous insertions/deletions
        position = change.get('position', 0)
        for prev_change in previous_changes:
            prev_position = prev_change.get('position', 0)
            if prev_position <= position:
                if prev_change.get('type') == 'insert':
                    position += len(prev_change.get('text', ''))
                elif prev_change.get('type') == 'delete':
                    position -= prev_change.get('length', 0)
        
        transformed_change['position'] = max(0, position)
        return transformed_change