from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ChatCreateRequest(BaseModel):
    """Request to create a new chat"""
    participant_id: UUID = Field(..., description="ID of the other participant")


class ChatResponse(BaseModel):
    """Chat response model"""
    id: UUID
    users: List[UUID] = Field(..., description="Array of user IDs in the chat")
    created_at: datetime
    updated_at: datetime


class ChatListResponse(BaseModel):
    """Response for list of chats"""
    chats: List[ChatResponse]
    total: int


class MessageCreateRequest(BaseModel):
    """Request to create a new message"""
    content: str = Field(..., min_length=1, max_length=1000)


class MessageResponse(BaseModel):
    """Message response model"""
    id: UUID
    chat_id: UUID
    sender_id: UUID
    content: str
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class MessageListResponse(BaseModel):
    """Response for list of messages"""
    messages: List[MessageResponse]
    total: int
    has_more: bool


class ChatMarkReadRequest(BaseModel):
    """Request to mark messages as read"""
    message_ids: List[UUID] = Field(..., description="IDs of messages to mark as read")


class ChatParticipantInfo(BaseModel):
    """Basic participant information"""
    id: UUID
    first_name: str
    last_name: str
    pfp_url: Optional[str]
    phone: Optional[str] = None


class ChatWithParticipantsResponse(BaseModel):
    """Chat with participant information"""
    id: UUID
    users: List[UUID]
    participants: List[ChatParticipantInfo]
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int


class WebSocketChatMessage(BaseModel):
    """WebSocket message for chat updates"""
    type: str = "chat_message"
    chat_id: UUID
    message: MessageResponse


class WebSocketReadReceipt(BaseModel):
    """WebSocket message for read receipts"""
    type: str = "read_receipt"
    chat_id: UUID
    message_ids: List[UUID]
    read_by: UUID
    read_at: datetime
