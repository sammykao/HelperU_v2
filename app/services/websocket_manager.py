from typing import Dict, Set
from uuid import UUID
from fastapi import WebSocket
from app.schemas.chat import WebSocketChatMessage, WebSocketReadReceipt


class WebSocketManager:
    """Manages WebSocket connections for real-time chat communication"""
    
    def __init__(self):
        # Map chat_id to set of connected WebSocket connections
        self.chat_connections: Dict[UUID, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, chat_id: UUID):
        """Connect a WebSocket to a specific chat"""
        if chat_id not in self.chat_connections:
            self.chat_connections[chat_id] = set()
        
        self.chat_connections[chat_id].add(websocket)
        print(f"WebSocket connected to chat {chat_id}. Total connections: {len(self.chat_connections[chat_id])}")
    
    async def disconnect(self, websocket: WebSocket, chat_id: UUID):
        """Disconnect a WebSocket from a chat"""
        if chat_id in self.chat_connections:
            self.chat_connections[chat_id].discard(websocket)
            
            # Remove empty chat connections
            if not self.chat_connections[chat_id]:
                del self.chat_connections[chat_id]
            
            print(f"WebSocket disconnected from chat {chat_id}")
    
    async def broadcast_chat_message(self, chat_id: UUID, message: WebSocketChatMessage):
        """Broadcast a chat message to all connected WebSocket clients in a chat"""
        if chat_id not in self.chat_connections:
            return
        
        # Convert message to JSON string
        message_json = message.model_dump_json()
        
        # Send to all connected clients in this chat
        disconnected_websockets = set()
        
        for websocket in self.chat_connections[chat_id]:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                print(f"Failed to send message to WebSocket: {str(e)}")
                disconnected_websockets.add(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected_websockets:
            await self.disconnect(websocket, chat_id)
    
    async def broadcast_read_receipt(self, chat_id: UUID, read_receipt: WebSocketReadReceipt):
        """Broadcast a read receipt to all connected WebSocket clients in a chat"""
        if chat_id not in self.chat_connections:
            return
        
        # Convert read receipt to JSON string
        receipt_json = read_receipt.model_dump_json()
        
        # Send to all connected clients in this chat
        disconnected_websockets = set()
        
        for websocket in self.chat_connections[chat_id]:
            try:
                await websocket.send_text(receipt_json)
            except Exception as e:
                print(f"Failed to send read receipt to WebSocket: {str(e)}")
                disconnected_websockets.add(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected_websockets:
            await self.disconnect(websocket, chat_id)
    
    def get_connection_count(self, chat_id: UUID = None) -> int:
        """Get the number of active connections for a chat or total"""
        if chat_id:
            return len(self.chat_connections.get(chat_id, set()))
        else:
            return sum(len(connections) for connections in self.chat_connections.values())
    
    def get_active_chats(self) -> list:
        """Get list of active chat IDs"""
        return list(self.chat_connections.keys())
