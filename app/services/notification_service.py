from logging import log
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, requests, status
from supabase import Client
import asyncio

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)

class NotificationService:
    """Service for handling chat and messaging operations"""

    def __init__(self, admin_client: Client):
        self.admin_client = admin_client

    def send_msg_notification(self, chat_id: UUID, sender_id: str, message: str):
        try:
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
            if UUID(str(sender_id)) not in participant_user_ids:
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

            filtered_ids = [id for id in participant_user_ids if id != str(sender_id)]
            
            expo_push_tokens = set()
            response = (
                self.admin_client
                .table("helpers")
                .select("id, push_notification_token")
                .in_("id", filtered_ids)
                .execute()
            )

            payload = []
            if response.data:
                for token_data in response.data: 
                    if token_data.push_notification_token in expo_push_tokens: 
                        continue;

                    payload.append(PushMessage(
                        to=token_data.push_notification_token,
                        title="New Message",
                        body=message,sound="default")
                    )

                    payload.append({ "to": token_data.push_notification_token, "title": "New Message", "message": message })
                    expo_push_tokens.add(token_data.push_notification_token)

            response = PushClient().publish_multiple(payload)
            print(response)
         
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {str(e)}"
            )
