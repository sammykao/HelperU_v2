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

            # Create new chat (no users array dependency)
            result = self.admin_client.table("chats").insert({}).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create chat"
                )

            chat = result.data[0]
            # Insert participants in chat_users (authoritative)
            self.admin_client.table("chat_users").insert([
                {"chat_id": chat["id"], "user_id": str(user_id)},
                {"chat_id": chat["id"], "user_id": str(participant_id)}
            ]).execute()

            chat['users'] = [user_id, participant_id]
            return ChatResponse(**chat)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create chat: {str(e)}"
            )

    async def get_user_chats(self, user_id: UUID) -> ChatListResponse:
        """Get all chats for a user in one query using chat_users join."""
        try:
            result = (self.admin_client.table("chats")
                .select("id,created_at,updated_at, participants:chat_users(user_id), membership:chat_users!inner(user_id)")
                .eq("membership.user_id", str(user_id))
                .order("updated_at", desc=True)
                .execute())

            if not result.data:
                return ChatListResponse(chats=[], total=0)

            chats = []
            for row in result.data:
                chat['users'] = [UUID(p["user_id"]) for p in row.get("participants") or []]
                chats.append(ChatResponse(**chat))

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
            # Single query: fetch chat with embedded participants, verify membership locally
            result = (self.admin_client.table("chats")
                .select("id,created_at,updated_at, participants:chat_users(user_id)")
                .eq("id", str(chat_id))
                .limit(1)
                .execute())
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )

            row = result.data[0]
            users = [UUID(p["user_id"]) for p in (row.get("participants") or [])]
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
                id=row["id"],
                users=users,
                participants=participants,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
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
            # Verify user is participant in chat via chat_users and get sender chat_user id
            cu_result = (self.admin_client.table("chat_users")
                .select("id,user_id")
                .eq("chat_id", str(chat_id))
                .execute())
            if not cu_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )
            participant_user_ids = [UUID(row["user_id"]) for row in cu_result.data]
            if sender_id not in participant_user_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this chat"
                )
            sender_chat_user_id = None
            for row in cu_result.data:
                if row["user_id"] == str(sender_id):
                    sender_chat_user_id = row["id"]
                    break
            if sender_chat_user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Sender not in chat"
                )

            # Create message
            result = self.admin_client.table("messages").insert({
                "chat_id": str(chat_id),
                "sender_id": str(sender_chat_user_id),
                "content": request.content
            }).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send message"
                )

            message = result.data[0]
            # Normalize sender_id back to user_id for API response
            message["sender_id"] = str(sender_id)
            
            # Update chat updated_at timestamp
            self.admin_client.table("chats").update({"updated_at": datetime.utcnow().isoformat()}).eq("id", str(chat_id)).execute()

            # Send SMS notification to the other participant
            if self.openphone_service:
                try:
                    # Get the other participant's ID
                    other_participant_id = next(uid for uid in participant_user_ids if uid != sender_id)
                    
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
            # Verify user is participant in chat via chat_users
            cu_result = (self.admin_client.table("chat_users")
                .select("id,user_id")
                .eq("chat_id", str(chat_id))
                .execute())
            if not cu_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )
            participant_user_ids = [UUID(row["user_id"]) for row in cu_result.data]
            if user_id not in participant_user_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this chat"
                )

            # Get messages with pagination, embed sender user_id, and return total count together
            result = (self.admin_client.table("messages")
                .select("id,chat_id,content,read_at,created_at,updated_at,sender:chat_users(user_id)", count="exact")
                .eq("chat_id", str(chat_id))
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute())

            if not result.data:
                return MessageListResponse(messages=[], total=0, has_more=False)

            total = result.count or 0
            has_more = (offset + limit) < total

            # Convert to response models (reverse order for chronological display)
            messages = []
            for message_data in reversed(result.data):
                adjusted = dict(message_data)
                # Normalize embedded sender object into sender_id
                sender_obj = adjusted.pop("sender", None)
                if sender_obj and sender_obj.get("user_id"):
                    adjusted["sender_id"] = sender_obj["user_id"]
                message = MessageResponse(**adjusted)
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
            # Verify user is participant in chat via chat_users
            cu_result = (self.admin_client.table("chat_users")
                .select("id,user_id")
                .eq("chat_id", str(chat_id))
                .execute())
            if not cu_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )
            participant_user_ids = [UUID(row["user_id"]) for row in cu_result.data]
            if user_id not in participant_user_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this chat"
                )

            # Mark messages as read
            now = datetime.utcnow().isoformat()
            # Determine current user's chat_user id to avoid marking own messages
            current_cu_id = None
            for row in cu_result.data:
                if row["user_id"] == str(user_id):
                    current_cu_id = row["id"]
                    break
            if current_cu_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User not in chat"
                )
            (self.admin_client.table("messages")
                .update({"read_at": now})
                .in_("id", [str(msg_id) for msg_id in request.message_ids])
                .eq("chat_id", str(chat_id))
                .neq("sender_id", str(current_cu_id))
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
        """Get existing chat between two users with a single join on chat_users twice."""
        try:
            # Join chat_users twice (aliases u1, u2) and pull all participants in one call
            result = (self.admin_client.table("chats")
                .select("id,created_at,updated_at, participants:chat_users(user_id), u1:chat_users!inner(user_id), u2:chat_users!inner(user_id)")
                .eq("u1.user_id", str(user_id))
                .eq("u2.user_id", str(participant_id))
                .limit(1)
                .execute())
            if not result.data:
                return None
            chat = result.data[0]
            chat['users'] = [UUID(p["user_id"]) for p in (chat.get("participants") or [])]
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

            # Get current user's chat_user id
            current_cu = (self.admin_client.table("chat_users")
                .select("id")
                .eq("chat_id", str(chat_id))
                .eq("user_id", str(user_id))
                .limit(1)
                .execute())
            current_cu_id = current_cu.data[0]["id"] if current_cu.data else None

            # Get unread count excluding current user's messages
            if current_cu_id is not None:
                unread_result = (self.admin_client.table("messages")
                    .select("id", count="exact")
                    .eq("chat_id", str(chat_id))
                    .is_("read_at", "null")
                    .neq("sender_id", str(current_cu_id))
                    .execute())
                unread_count = unread_result.count or 0
            else:
                unread_count = 0

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
