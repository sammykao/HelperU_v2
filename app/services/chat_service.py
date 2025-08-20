from typing import Optional, List
from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status
from supabase import Client

from app.schemas.chat import (
    ChatCreateRequest,
    ChatResponse,
    ChatListResponse,
    MessageCreateRequest,
    MessageResponse,
    MessageListResponse,
    ChatMarkReadRequest,
    ChatWithParticipantsResponse,
    ChatParticipantInfo
)
from app.services.openphone_service import OpenPhoneService
from app.schemas.openphone import MessageNotification


class ChatService:
    """Service for handling chat and messaging operations"""

    def __init__(self, admin_client: Client, openphone_service: OpenPhoneService = None):
        self.admin_client = admin_client
        self.openphone_service = openphone_service

    async def create_chat(self, user_id: UUID, participant_id: UUID) -> ChatResponse:
        """Create a new chat between two users"""
        try:
            # Check if chat already exists
            existing_chat = await self._get_chat_by_participants(user_id, participant_id)
            if existing_chat:
                return existing_chat

            # Verify both participants exist
            await self._verify_users_exist([user_id, participant_id])

            # Create new chat with users array
            chat_data = {
                "users": [str(user_id), str(participant_id)]
            }

            result = self.admin_client.table("chats").insert(chat_data).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create chat"
                )

            chat = result.data[0]
            return ChatResponse(**chat)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create chat: {str(e)}"
            )

    async def get_user_chats(self, user_id: UUID) -> ChatListResponse:
        """Get all chats for a user"""
        try:
            # Get chats where user is a participant
            query = f"""
                SELECT 
                    c.*,
                    m.content as last_message,
                    m.created_at as last_message_at,
                    COALESCE(
                        (SELECT COUNT(*) FROM messages 
                         WHERE chat_id = c.id 
                         AND sender_id != '{user_id}' 
                         AND read_at IS NULL), 0
                    ) as unread_count
                FROM chats c
                LEFT JOIN LATERAL (
                    SELECT content, created_at 
                    FROM messages 
                    WHERE chat_id = c.id 
                    ORDER BY created_at DESC 
                    LIMIT 1
                ) m ON true
                WHERE '{user_id}' = ANY(c.users)
                ORDER BY COALESCE(m.created_at, c.created_at) DESC
            """

            result = self.admin_client.rpc("exec_sql", {"query": query}).execute()
            
            if not result.data:
                return ChatListResponse(chats=[], total=0)

            chats = []
            for chat_data in result.data:
                # Convert users back to UUID list
                chat_data["users"] = [UUID(uid) for uid in chat_data["users"]]
                chat = ChatResponse(**chat_data)
                chats.append(chat)

            return ChatListResponse(chats=chats, total=len(chats))

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get chats: {str(e)}"
            )

    async def get_chat_with_participants(self, chat_id: UUID, user_id: UUID) -> ChatWithParticipantsResponse:
        """Get chat with participant information"""
        try:
            # Get chat and verify user is participant
            chat_result = self.admin_client.table("chats").select("*").eq("id", str(chat_id)).execute()
            
            if not chat_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )

            chat = chat_result.data[0]
            users = [UUID(uid) for uid in chat["users"]]
            
            # Verify user is participant
            if user_id not in users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this chat"
                )

            # Get participant information
            participants = []
            for participant_id in users:
                participant_info = await self._get_participant_info(str(participant_id))
                participants.append(participant_info)

            # Get last message and unread count
            last_message_data = await self._get_last_message_and_unread_count(chat_id, user_id)

            return ChatWithParticipantsResponse(
                id=chat["id"],
                users=users,
                participants=participants,
                created_at=chat["created_at"],
                updated_at=chat["updated_at"],
                last_message=last_message_data.get("last_message"),
                last_message_at=last_message_data.get("last_message_at"),
                unread_count=last_message_data.get("unread_count", 0)
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get chat: {str(e)}"
            )

    async def send_message(self, chat_id: UUID, sender_id: UUID, request: MessageCreateRequest) -> MessageResponse:
        """Send a new message in a chat"""
        try:
            # Verify user is participant in chat
            chat_result = self.admin_client.table("chats").select("users").eq("id", str(chat_id)).execute()
            
            if not chat_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )

            chat = chat_result.data[0]
            users = [UUID(uid) for uid in chat["users"]]
            
            if sender_id not in users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this chat"
                )

            # Create message
            message_data = {
                "chat_id": str(chat_id),
                "sender_id": str(sender_id),
                "content": request.content
            }

            result = self.admin_client.table("messages").insert(message_data).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send message"
                )

            message = result.data[0]
            
            # Update chat updated_at timestamp
            self.admin_client.table("chats").update({"updated_at": datetime.utcnow().isoformat()}).eq("id", str(chat_id)).execute()

            # Send SMS notification to the other participant
            if self.openphone_service:
                try:
                    # Get the other participant's ID
                    other_participant_id = next(uid for uid in users if uid != sender_id)
                    
                    # Get participant info for the notification
                    other_participant_info = await self._get_participant_info(str(other_participant_id))
                    sender_info = await self._get_participant_info(str(sender_id))
                    
                    # Send SMS notification
                    if other_participant_info.phone:
                        notification = MessageNotification(
                            recipient_phone=other_participant_info.phone,
                            sender_name=f"{sender_info.first_name} {sender_info.last_name}",
                            chat_id=str(chat_id),
                            message_preview=request.content
                        )
                        await self.openphone_service.send_message_notification(notification)
                except Exception as e:
                    # Log error but don't fail the message send
                    print(f"Failed to send SMS notification: {str(e)}")

            return MessageResponse(**message)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {str(e)}"
            )

    async def get_chat_messages(self, chat_id: UUID, user_id: UUID, limit: int = 50, offset: int = 0) -> MessageListResponse:
        """Get messages for a specific chat"""
        try:
            # Verify user is participant in chat
            chat_result = self.admin_client.table("chats").select("users").eq("id", str(chat_id)).execute()
            
            if not chat_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )

            chat = chat_result.data[0]
            users = [UUID(uid) for uid in chat["users"]]
            
            if user_id not in users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this chat"
                )

            # Get messages with pagination
            result = (self.admin_client.table("messages")
                .select("*")
                .eq("chat_id", str(chat_id))
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute())

            if not result.data:
                return MessageListResponse(messages=[], total=0, has_more=False)

            # Get total count
            count_result = (self.admin_client.table("messages")
                .select("id", count="exact")
                .eq("chat_id", str(chat_id))
                .execute())

            total = count_result.count or 0
            has_more = (offset + limit) < total

            # Convert to response models (reverse order for chronological display)
            messages = []
            for message_data in reversed(result.data):
                message = MessageResponse(**message_data)
                messages.append(message)

            return MessageListResponse(
                messages=messages,
                total=total,
                has_more=has_more
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get messages: {str(e)}"
            )

    async def mark_messages_read(self, chat_id: UUID, user_id: UUID, request: ChatMarkReadRequest) -> dict:
        """Mark messages as read"""
        try:
            # Verify user is participant in chat
            chat_result = self.admin_client.table("chats").select("users").eq("id", str(chat_id)).execute()
            
            if not chat_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )

            chat = chat_result.data[0]
            users = [UUID(uid) for uid in chat["users"]]
            
            if user_id not in users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this chat"
                )

            # Mark messages as read
            now = datetime.utcnow().isoformat()
            (self.admin_client.table("messages")
                .update({"read_at": now})
                .in_("id", [str(msg_id) for msg_id in request.message_ids])
                .eq("chat_id", str(chat_id))
                .neq("sender_id", str(user_id))
                .execute())

            return {
                "success": True,
                "message": f"Marked {len(request.message_ids)} messages as read",
                "read_at": now
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark messages as read: {str(e)}"
            )

    async def _get_chat_by_participants(self, user_id: UUID, participant_id: UUID) -> Optional[ChatResponse]:
        """Get existing chat between two users"""
        try:
            # Check if chat exists with both users
            result = (self.admin_client.table("chats")
                .select("*")
                .contains("users", [str(user_id), str(participant_id)])
                .execute())

            if not result.data:
                return None

            chat = result.data[0]
            # Convert users back to UUID list
            chat["users"] = [UUID(uid) for uid in chat["users"]]
            return ChatResponse(**chat)

        except Exception:
            return None

    async def _get_participant_info(self, user_id: str) -> ChatParticipantInfo:
        """Get basic participant information"""
        try:
            # Try to get from clients table first
            result = (self.admin_client.table("clients")
                .select("id, first_name, last_name, pfp_url, phone")
                .eq("id", user_id)
                .execute())

            if result.data:
                user_data = result.data[0]
                return ChatParticipantInfo(**user_data)

            # If not found in clients, try helpers table
            result = (self.admin_client.table("helpers")
                .select("id, first_name, last_name, pfp_url, phone")
                .eq("id", user_id)
                .execute())

            if result.data:
                user_data = result.data[0]
                return ChatParticipantInfo(**user_data)

            # Fallback with minimal info
            return ChatParticipantInfo(
                id=UUID(user_id),
                first_name="Unknown",
                last_name="User",
                pfp_url=None
            )

        except Exception:
            # Fallback with minimal info
            return ChatParticipantInfo(
                id=UUID(user_id),
                first_name="Unknown",
                last_name="User",
                pfp_url=None
            )

    async def _verify_users_exist(self, user_ids: List[UUID]) -> None:
        """Verify that all users exist"""
        try:
            # Check all users exist in either clients or helpers table
            for user_id in user_ids:
                client_exists = (self.admin_client
                    .table("clients")
                    .select("id")
                    .eq("id", str(user_id))
                    .execute())
                
                helper_exists = (self.admin_client
                    .table("helpers")
                    .select("id")
                    .eq("id", str(user_id))
                    .execute())
                
                if not client_exists.data and not helper_exists.data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User {user_id} not found"
                    )
                    
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify users: {str(e)}"
            )

    async def _get_last_message_and_unread_count(self, chat_id: UUID, user_id: UUID) -> dict:
        """Get last message and unread count for a chat"""
        try:
            # Get last message
            last_message_result = (self.admin_client.table("messages")
                .select("content, created_at")
                .eq("chat_id", str(chat_id))
                .order("created_at", desc=True)
                .limit(1)
                .execute())

            last_message = None
            last_message_at = None
            if last_message_result.data:
                last_message = last_message_result.data[0]["content"]
                last_message_at = last_message_result.data[0]["created_at"]

            # Get unread count
            unread_result = (self.admin_client.table("messages")
                .select("id", count="exact")
                .eq("chat_id", str(chat_id))
                .neq("sender_id", str(user_id))
                .is_("read_at", "null")
                .execute())

            unread_count = unread_result.count or 0

            return {
                "last_message": last_message,
                "last_message_at": last_message_at,
                "unread_count": unread_count
            }

        except Exception:
            return {
                "last_message": None,
                "last_message_at": None,
                "unread_count": 0
            }
