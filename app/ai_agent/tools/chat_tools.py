"""Chat tools for AI agents"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from app.ai_agent.base import BaseTool
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatCreateRequest,
    MessageCreateRequest,
    ChatMarkReadRequest
)

class ChatTools(BaseTool):
    """Tools for chat and messaging operations"""
    
    def __init__(self, chat_service: ChatService):
        super().__init__("chat_tools", "Tools for managing chats and messages")
        self.chat_service = chat_service
    
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute chat tool action"""
        try:
            if action == "create_chat":
                return await self._create_chat(**kwargs)
            elif action == "get_user_chats":
                return await self._get_user_chats(**kwargs)
            elif action == "get_chat_messages":
                return await self._get_chat_messages(**kwargs)
            elif action == "send_message":
                return await self._send_message(**kwargs)
            elif action == "mark_chat_read":
                return await self._mark_chat_read(**kwargs)
            elif action == "get_chat_with_participants":
                return await self._get_chat_with_participants(**kwargs)
            else:
                raise ValueError(f"Unknown chat action: {action}")
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _create_chat(self, user_id: str, participant_id: str) -> Dict[str, Any]:
        """Create a new chat between two users"""
        try:
            user_uuid = UUID(user_id)
            participant_uuid = UUID(participant_id)
            result = await self.chat_service.create_chat(user_uuid, participant_uuid)
            return {
                "success": True,
                "chat_id": str(result.id),
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "users": [str(uid) for uid in result.users] if result.users else []
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_user_chats(self, user_id: str) -> Dict[str, Any]:
        """Get all chats for a user"""
        try:
            user_uuid = UUID(user_id)
            result = await self.chat_service.get_user_chats(user_uuid)
            return {
                "success": True,
                "chats": [
                    {
                        "id": str(chat.id),
                        "created_at": chat.created_at.isoformat() if chat.created_at else None,
                        "updated_at": chat.updated_at.isoformat() if chat.updated_at else None,
                        "users": [str(uid) for uid in chat.users] if chat.users else []
                    }
                    for chat in result.chats
                ],
                "total": result.total
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_chat_messages(self, chat_id: str, user_id: str, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get messages for a specific chat"""
        try:
            chat_uuid = UUID(chat_id)
            user_uuid = UUID(user_id)
            result = await self.chat_service.get_chat_messages(chat_uuid, user_uuid, page, limit)
            return {
                "success": True,
                "messages": [
                    {
                        "id": str(msg.id),
                        "content": msg.content,
                        "sender_id": str(msg.sender_id),
                        "created_at": msg.created_at.isoformat() if msg.created_at else None,
                        "is_read": msg.is_read
                    }
                    for msg in result.messages
                ],
                "total": result.total,
                "page": page,
                "limit": limit
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _send_message(self, chat_id: str, sender_id: str, content: str) -> Dict[str, Any]:
        """Send a message in a chat"""
        try:
            chat_uuid = UUID(chat_id)
            sender_uuid = UUID(sender_id)
            request = MessageCreateRequest(content=content)
            result = await self.chat_service.send_message(chat_uuid, sender_uuid, request)
            return {
                "success": True,
                "message_id": str(result.id),
                "content": result.content,
                "sender_id": str(result.sender_id),
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "is_read": result.is_read
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _mark_chat_read(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Mark a chat as read for a user"""
        try:
            chat_uuid = UUID(chat_id)
            user_uuid = UUID(user_id)
            request = ChatMarkReadRequest(chat_id=str(chat_uuid), user_id=str(user_uuid))
            result = await self.chat_service.mark_chat_read(request)
            return {
                "success": result.success,
                "message": result.message
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_chat_with_participants(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Get chat with participant information"""
        try:
            chat_uuid = UUID(chat_id)
            user_uuid = UUID(user_id)
            result = await self.chat_service.get_chat_with_participants(chat_uuid, user_uuid)
            return {
                "success": True,
                "chat_id": str(result.id),
                "participants": [
                    {
                        "user_id": str(p.user_id),
                        "first_name": p.first_name,
                        "last_name": p.last_name,
                        "email": p.email,
                        "phone": p.phone
                    }
                    for p in result.participants
                ]
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema for chat tools"""
        return {
            "actions": {
                "create_chat": {
                    "user_id": "string - User ID initiating the chat",
                    "participant_id": "string - Participant ID to chat with"
                },
                "get_user_chats": {
                    "user_id": "string - User ID to get chats for"
                },
                "get_chat_messages": {
                    "chat_id": "string - Chat ID",
                    "user_id": "string - User ID requesting messages",
                    "page": "integer - Page number (optional, default 1)",
                    "limit": "integer - Messages per page (optional, default 50)"
                },
                "send_message": {
                    "chat_id": "string - Chat ID",
                    "sender_id": "string - Sender user ID",
                    "content": "string - Message content"
                },
                "mark_chat_read": {
                    "chat_id": "string - Chat ID",
                    "user_id": "string - User ID marking as read"
                },
                "get_chat_with_participants": {
                    "chat_id": "string - Chat ID",
                    "user_id": "string - User ID requesting chat info"
                }
            }
        }

