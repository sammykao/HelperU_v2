from uuid import UUID
from fastapi import HTTPException, status
from supabase import Client
from httpx import AsyncClient
import jwt
import time
import asyncio

from app.core.config import settings


class NotificationService:
    """Service for handling chat and messaging operations"""

    def __init__(self, admin_client: Client):
        self.admin_client = admin_client
        self.url = "https://api.push.apple.com"

    def _get_private_key(self):
        with open("../../PushTokenSecret.p8", "r") as f:
            return f.read()

    def _create_auth_token(self):
        return jwt.encode(
            {
                "iss": settings.HELPER_MOBILE_APP_BUNDLE_ID,
                "iat": int(time.time()),
            },
            self._get_private_key(),
            algorithm="ES256",
            headers={"alg": "ES256", "kid": settings.HELPER_PUSH_NOTIFICATION_P8_ID},
        )

    async def _send_apns_notification(self, msg):
        async with AsyncClient(http2=True) as client:
            response = await client.post(
                f"{self.url}/3/device/{msg.device_token}",
                headers=msg.headers,
                json=msg.payload,
            )
            return {
                "device_token": msg.device_token,
                "status": response.status_code,
                "body": response.text,
            }

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

            # filtered_ids = [id for id in participant_user_ids if id != str(sender_id)]
            # native_push_tokens = set()
            #
            # response = (
            #     self.admin_client.table("helpers")
            #     .select("id, push_notification_token")
            #     .in_("id", filtered_ids)
            #     .execute()
            # )

            headers = {
                "authorization": f"bearer {self._create_auth_token()}",
                "apns-topic": settings.HELPER_MOBILE_APP_BUNDLE_ID,
            }
            payload = {
                "aps": {
                    "alert": {
                        "title": "New Message",
                        "body": message,
                    }
                }
            }

            result = await self._send_apns_notification(
                {
                    "headers": headers,
                    "payload": payload,
                    "device_token": "63ad5950480e411ba03cea6e55f56667b93af214f5f234d2aa6ad35678bbeb1c",
                }
            )

            print(result)

            # msgs = []
            # if response.data:
            #     print(response.data)
            #     for token_data in response.data:
            #         tokens = token_data["push_notification_token"] or []
            #         for token in tokens:
            #             headers = {
            #                 "authorization": f"bearer {self._create_auth_token()}",
            #                 "apns-topic": settings.HELPER_MOBILE_APP_BUNDLE_ID,
            #             }
            #             payload = {
            #                 "aps": {
            #                     "alert": {
            #                         "title": "New Message",
            #                         "body": message,
            #                     }
            #                 }
            #             }
            #             if token in native_push_tokens:
            #                 continue
            #
            #             msgs.append(
            #                 {
            #                     "headers": headers,
            #                     "payload": payload,
            #                     "device_token": "63ad5950480e411ba03cea6e55f56667b93af214f5f234d2aa6ad35678bbeb1c",
            #                 }
            #             )
            #             native_push_tokens.add(token)

            # tasks = [self._send_apns_notification(msg) for msg in msgs]
            # results = await asyncio.gather(*tasks, return_exceptions=True)

            # print(results)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {str(e)}",
            )
