from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse

from app.deps.supabase import get_current_user, get_chat_service
from app.schemas.auth import CurrentUser
from app.schemas.chat import (
    ChatCreateRequest,
    ChatResponse,
    ChatListResponse,
    MessageCreateRequest,
    MessageResponse,
    MessageListResponse,
    ChatMarkReadRequest,
    ChatWithParticipantsResponse,
    WebSocketChatMessage,
    WebSocketReadReceipt
)
from app.services.chat_service import ChatService
from app.services.websocket_manager import WebSocketManager

router = APIRouter()
websocket_manager = WebSocketManager()


@router.post("/create", response_model=ChatResponse)
async def create_chat(
    request: ChatCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Create a new chat between current user and participant"""
    try:
        return await chat_service.create_chat(current_user.id, request.participant_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat: {str(e)}"
        )


@router.get("/list", response_model=ChatListResponse)
async def get_user_chats(
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all chats for the current user"""
    try:
        return await chat_service.get_user_chats(current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chats: {str(e)}"
        )


@router.get("/{chat_id}", response_model=ChatWithParticipantsResponse)
async def get_chat_with_participants(
    chat_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get chat with participant information"""
    try:
        return await chat_service.get_chat_with_participants(chat_id, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat: {str(e)}"
        )


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: UUID,
    request: MessageCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a new message in a chat"""
    try:
        message = await chat_service.send_message(chat_id, current_user.id, request)
        
        # Broadcast message to WebSocket subscribers
        websocket_message = WebSocketChatMessage(
            chat_id=chat_id,
            message=message
        )
        await websocket_manager.broadcast_chat_message(chat_id, websocket_message)
        
        return message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/{chat_id}/messages", response_model=MessageListResponse)
async def get_chat_messages(
    chat_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get messages for a specific chat"""
    try:
        return await chat_service.get_chat_messages(chat_id, current_user.id, limit, offset)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        )


@router.post("/{chat_id}/read")
async def mark_messages_read(
    chat_id: UUID,
    request: ChatMarkReadRequest,
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Mark messages as read"""
    try:
        result = await chat_service.mark_messages_read(chat_id, current_user.id, request)
        
        # Broadcast read receipt to WebSocket subscribers
        read_receipt = WebSocketReadReceipt(
            chat_id=chat_id,
            message_ids=request.message_ids,
            read_by=current_user.id,
            read_at=result["read_at"]
        )
        await websocket_manager.broadcast_read_receipt(chat_id, read_receipt)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark messages as read: {str(e)}"
        )


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: UUID,
    chat_service: ChatService = Depends(get_chat_service)
):
    """WebSocket endpoint for real-time chat communication"""
    await websocket.accept()
    
    try:
        # Subscribe to chat updates
        await websocket_manager.connect(websocket, chat_id)
        
        # Send connection confirmation
        await websocket.send_text("Connected to chat")
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                # Handle incoming WebSocket messages if needed
                # For now, just keep connection alive
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {str(e)}")
                break
                
    except Exception as e:
        print(f"WebSocket connection error: {str(e)}")
    finally:
        # Clean up connection
        await websocket_manager.disconnect(websocket, chat_id)
