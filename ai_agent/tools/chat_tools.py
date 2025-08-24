"""
Chat Management MCP Tools
Wraps chat_service functions as MCP tools
"""
from typing import Any, Dict, Optional, List
from uuid import UUID
from .base import BaseMCPTool, ToolSchema, tool_registry
from app.services.chat_service import ChatService
from app.schemas.chat import MessageCreateRequest, ChatMarkReadRequest


class CreateChatTool(BaseMCPTool):
    """Create a new chat between two users"""
    
    def __init__(self, chat_service: ChatService):
        super().__init__("create_chat", "Create a new chat between two users")
        self.chat_service = chat_service
    
    async def execute(self, user_id: str, participant_id: str) -> Dict[str, Any]:
        """Create a new chat"""
        result = await self.chat_service.create_chat(UUID(user_id), UUID(participant_id))
        return {
            "success": True,
            "chat_id": str(result.id),
            "users": [str(uid) for uid in result.users],
            "created_at": result.created_at.isoformat()
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="create_chat",
            description="Create a new chat between two users",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "First user ID"},
                    "participant_id": {"type": "string", "description": "Second user ID"}
                },
                "required": ["user_id", "participant_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "chat_id": {"type": "string"},
                    "users": {"type": "array", "items": {"type": "string"}},
                    "created_at": {"type": "string"}
                }
            }
        )


class GetUserChatsTool(BaseMCPTool):
    """Get all chats for a user"""
    
    def __init__(self, chat_service: ChatService):
        super().__init__("get_user_chats", "Get all chats for a user")
        self.chat_service = chat_service
    
    async def execute(self, user_id: str) -> Dict[str, Any]:
        """Get user chats"""
        result = await self.chat_service.get_user_chats(UUID(user_id))
        
        chats = []
        for chat in result.chats:
            chats.append({
                "id": str(chat.id),
                "users": [str(uid) for uid in chat.users],
                "created_at": chat.created_at.isoformat(),
                "updated_at": chat.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "chats": chats,
            "total": result.total
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_user_chats",
            description="Get all chats for a user",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"}
                },
                "required": ["user_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "chats": {"type": "array", "items": {"type": "object"}},
                    "total": {"type": "integer"}
                }
            }
        )


class SendMessageTool(BaseMCPTool):
    """Send a message in a chat"""
    
    def __init__(self, chat_service: ChatService):
        super().__init__("send_message", "Send a message in a chat")
        self.chat_service = chat_service
    
    async def execute(self, chat_id: str, sender_id: str, content: str) -> Dict[str, Any]:
        """Send a message"""
        request = MessageCreateRequest(content=content)
        result = await self.chat_service.send_message(UUID(chat_id), UUID(sender_id), request)
        
        return {
            "success": True,
            "message_id": str(result.id),
            "chat_id": str(result.chat_id),
            "sender_id": str(result.sender_id),
            "content": result.content,
            "created_at": result.created_at.isoformat()
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="send_message",
            description="Send a message in a chat",
            input_schema={
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string", "description": "Chat ID"},
                    "sender_id": {"type": "string", "description": "Sender user ID"},
                    "content": {"type": "string", "description": "Message content"}
                },
                "required": ["chat_id", "sender_id", "content"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message_id": {"type": "string"},
                    "chat_id": {"type": "string"},
                    "sender_id": {"type": "string"},
                    "content": {"type": "string"},
                    "created_at": {"type": "string"}
                }
            }
        )


class GetChatMessagesTool(BaseMCPTool):
    """Get messages for a specific chat"""
    
    def __init__(self, chat_service: ChatService):
        super().__init__("get_chat_messages", "Get messages for a specific chat")
        self.chat_service = chat_service
    
    async def execute(self, chat_id: str, user_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get chat messages"""
        result = await self.chat_service.get_chat_messages(UUID(chat_id), UUID(user_id), limit, offset)
        
        messages = []
        for msg in result.messages:
            messages.append({
                "id": str(msg.id),
                "sender_id": str(msg.sender_id),
                "content": msg.content,
                "read_at": msg.read_at.isoformat() if msg.read_at else None,
                "created_at": msg.created_at.isoformat()
            })
        
        return {
            "success": True,
            "messages": messages,
            "total": result.total,
            "has_more": result.has_more
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_chat_messages",
            description="Get messages for a specific chat",
            input_schema={
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string", "description": "Chat ID"},
                    "user_id": {"type": "string", "description": "User ID for access control"},
                    "limit": {"type": "integer", "description": "Number of messages to return", "default": 50},
                    "offset": {"type": "integer", "description": "Number of messages to skip", "default": 0}
                },
                "required": ["chat_id", "user_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "messages": {"type": "array", "items": {"type": "object"}},
                    "total": {"type": "integer"},
                    "has_more": {"type": "boolean"}
                }
            }
        )


class MarkMessagesReadTool(BaseMCPTool):
    """Mark messages as read"""
    
    def __init__(self, chat_service: ChatService):
        super().__init__("mark_messages_read", "Mark messages as read")
        self.chat_service = chat_service
    
    async def execute(self, chat_id: str, user_id: str, message_ids: List[str]) -> Dict[str, Any]:
        """Mark messages as read"""
        request = ChatMarkReadRequest(message_ids=[UUID(msg_id) for msg_id in message_ids])
        result = await self.chat_service.mark_messages_read(UUID(chat_id), UUID(user_id), request)
        
        return {
            "success": True,
            "message": result["message"],
            "read_at": result["read_at"]
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="mark_messages_read",
            description="Mark messages as read",
            input_schema={
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string", "description": "Chat ID"},
                    "user_id": {"type": "string", "description": "User ID marking messages as read"},
                    "message_ids": {"type": "array", "items": {"type": "string"}, "description": "List of message IDs to mark as read"}
                },
                "required": ["chat_id", "user_id", "message_ids"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "read_at": {"type": "string"}
                }
            }
        )


class GetChatWithParticipantsTool(BaseMCPTool):
    """Get chat with participant information"""
    
    def __init__(self, chat_service: ChatService):
        super().__init__("get_chat_with_participants", "Get chat with participant information")
        self.chat_service = chat_service
    
    async def execute(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Get chat with participants"""
        result = await self.chat_service.get_chat_with_participants(UUID(chat_id), UUID(user_id))
        
        participants = []
        for participant in result.participants:
            participants.append({
                "id": str(participant.id),
                "first_name": participant.first_name,
                "last_name": participant.last_name,
                "pfp_url": participant.pfp_url,
                "phone": participant.phone
            })
        
        return {
            "success": True,
            "chat": {
                "id": str(result.id),
                "users": [str(uid) for uid in result.users],
                "participants": participants,
                "created_at": result.created_at.isoformat(),
                "updated_at": result.updated_at.isoformat(),
                "last_message": result.last_message,
                "last_message_at": result.last_message_at.isoformat() if result.last_message_at else None,
                "unread_count": result.unread_count
            }
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_chat_with_participants",
            description="Get chat with participant information",
            input_schema={
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string", "description": "Chat ID"},
                    "user_id": {"type": "string", "description": "User ID for access control"}
                },
                "required": ["chat_id", "user_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "chat": {"type": "object"}
                }
            }
        )


def register_chat_tools(chat_service: ChatService):
    """Register all chat tools"""
    tools = [
        CreateChatTool(chat_service),
        GetUserChatsTool(chat_service),
        SendMessageTool(chat_service),
        GetChatMessagesTool(chat_service),
        MarkMessagesReadTool(chat_service),
        GetChatWithParticipantsTool(chat_service)
    ]
    
    for tool in tools:
        tool_registry.register(tool)
    
    return tools
