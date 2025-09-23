from uuid import UUID
from fastapi import HTTPException, status
from supabase import Client
from httpx import AsyncClient


class NotificationService:
    """Service for handling chat and messaging operations"""

    def __init__(self, admin_client: Client):
        self.admin_client = admin_client

    async def send_msg_notification(self, chat_id: UUID, sender_id: str, message: str):
        try:
            cu_result = (
                self.admin_client.table("chat_users")
                .select("id,user_id")
                .eq("chat_id", str(chat_id))
                .execute()
            )
            if not cu_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
                )
            participant_user_ids = [UUID(row["user_id"]) for row in cu_result.data]
            if UUID(str(sender_id)) not in participant_user_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this chat",
                )
            sender_chat_user_id = None
            for row in cu_result.data:
                if row["user_id"] == str(sender_id):
                    sender_chat_user_id = row["id"]
                    break
            if sender_chat_user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Sender not in chat"
                )

            filtered_ids = [id for id in participant_user_ids if id != str(sender_id)]
            expo_push_tokens = set()

            response = (
                self.admin_client.table("helpers")
                .select("id, push_notification_token")
                .in_("id", filtered_ids)
                .execute()
            )

            print(f"what is expo token result {response}")

            payload = []
            if response.data:
                print(response.data)
                for token_data in response.data:
                    tokens = token_data["push_notification_token"] or []
                    for token in tokens:
                        if token in expo_push_tokens:
                            continue

                        payload.append(
                            {"to": token, "title": "New Message", "body": message}
                        )

                        expo_push_tokens.add(token)

            print(f"Payload: {payload}")

            async with AsyncClient(http2=True) as client:
                headers = {
                    "host": "exp.host",
                    "accept": "application/json",
                    "accept-encoding": "gzip, deflate",
                    "content-type": "application/json",
                }
                response = await client.post(
                    "https://exp.host/--/api/v2/push/send",
                    headers=headers,
                    json=payload,
                )
                print(response)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {str(e)}",
            )
