from typing import Optional
from supabase import Client
from fastapi import HTTPException

from app.schemas.profile import (
    UserProfileStatusResponse,
    ProfileUpdateResponse,
    ClientProfileData,
    HelperProfileData,
    ProfileUpdateData,
)


class ProfileService:
    """Service for handling user profile operations"""

    def __init__(self, admin_client: Client):
        self.admin_client = admin_client

    async def get_user_profile_status(self, user_id: str) -> UserProfileStatusResponse:
        """Get user's profile completion status"""
        try:
            # Check if user is client or helper
            client_result = (
                self.admin_client.table("clients")
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            helper_result = (
                self.admin_client.table("helpers")
                .select("*")
                .eq("id", user_id)
                .execute()
            )

            print("helper")
            print(helper_result)

            # Check if user exists in both tables (shared auth)
            if client_result.data and helper_result.data:
                client_data = ClientProfileData(**client_result.data[0])
                helper_data = HelperProfileData(**helper_result.data[0])
                return UserProfileStatusResponse(
                    user_type="both",
                    profile_completed=True,
                    email_verified=True,
                    phone_verified=True,
                    profile_data={
                        "client": client_data.model_dump(),
                        "helper": helper_data.model_dump(),
                    },
                )

            # Check if user is only a clientT
            if client_result.data:
                client_data = ClientProfileData(**client_result.data[0])
                return UserProfileStatusResponse(
                    user_type="client",
                    profile_completed=bool(
                        client_data.first_name and client_data.last_name
                    ),
                    email_verified=False,  # Clients don't have email
                    phone_verified=True,  # If they're in the table, phone is verified
                    profile_data={
                        "client": client_data.model_dump(),
                    },
                )

            if helper_result.data:
                helper_data = HelperProfileData(**helper_result.data[0])
                return UserProfileStatusResponse(
                    user_type="helper",
                    profile_completed=bool(
                        helper_data.first_name and helper_data.last_name
                    ),
                    email_verified=True,  # If they're in the table, email is verified
                    phone_verified=True,  # If they're in the table, phone is verified
                    profile_data={
                        "helper": helper_data.model_dump(),
                    },
                )

            # User exists in auth but not in profile tables
            return UserProfileStatusResponse(
                user_type="unknown",
                profile_completed=False,
                email_verified=False,
                phone_verified=False,
                profile_data=None,
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to get profile status: {str(exc)}"
            )

    async def get_client_profile(self, user_id: str) -> Optional[ClientProfileData]:
        """Get client profile by user ID"""
        try:
            result = (
                self.admin_client.table("clients")
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            if result.data:
                return ClientProfileData(**result.data[0])
            return None
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to get client profile: {str(exc)}"
            )

    async def get_helper_profile(self, user_id: str) -> Optional[HelperProfileData]:
        """Get helper profile by user ID"""
        try:
            result = (
                self.admin_client.table("helpers")
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            if result.data:
                return HelperProfileData(**result.data[0])
            return None
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to get helper profile: {str(exc)}"
            )

    async def update_client_profile(
        self, user_id: str, profile_data: ProfileUpdateData
    ) -> ProfileUpdateResponse:
        """Update client profile"""
        try:
            # Convert Pydantic model to dict, excluding None values
            update_data = profile_data.model_dump(exclude_unset=True)
            result = (
                self.admin_client.table("clients")
                .update(update_data)
                .eq("id", user_id)
                .execute()
            )

            if result.data:
                updated_profile = ClientProfileData(**result.data[0])
                return ProfileUpdateResponse(
                    success=True,
                    message="Client profile updated successfully",
                    profile_data=updated_profile.model_dump(),
                )
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to update client profile"
                )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to update client profile: {str(exc)}"
            )

    async def update_helper_profile(
        self, user_id: str, profile_data: ProfileUpdateData
    ) -> ProfileUpdateResponse:
        """Update helper profile"""
        try:
            # Convert Pydantic model to dict, excluding None values
            update_data = profile_data.model_dump(exclude_unset=True)
            result = (
                self.admin_client.table("helpers")
                .update(update_data)
                .eq("id", user_id)
                .execute()
            )

            if result.data:
                updated_profile = HelperProfileData(**result.data[0])
                return ProfileUpdateResponse(
                    success=True,
                    message="Helper profile updated successfully",
                    profile_data=updated_profile.model_dump(),
                )
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to update helper profile"
                )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to update helper profile: {str(exc)}"
            )

    async def delete_profile(self, user_id: str):
        try:
            result = self.admin_client.auth.admin.delete_user(user_id)
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to update helper profile: {str(exc)}"
            )

    async def register_device(self, user_id: str, expo_token: str):

        try:
            client_result = (
                self.admin_client.table("clients")
                .select("*")
                .eq("id", user_id)
                .execute()
            )

            if not client_result.count and client_result.data:
                tokens = client_result.data[0].get("push_notification_token") or []
                if expo_token not in tokens:
                    updated_tokens = tokens + [expo_token]
                    self.admin_client.table("clients").update(
                        {"push_notification_token": updated_tokens}
                    ).eq("id", user_id).execute()
                return

            helper_result = (
                self.admin_client.table("helpers")
                .select("id, push_notification_token")
                .eq("id", user_id)
                .execute()
            )

            if helper_result.data:
                tokens = helper_result.data[0].get("push_notification_token") or []
                if expo_token not in tokens:
                    updated_tokens = tokens + [expo_token]
                    self.admin_client.table("helpers").update(
                        {"push_notification_token": updated_tokens}
                    ).eq("id", user_id).execute()
                return

            # if user not found in either table
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found in clients or helpers",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to register device: {str(exc)}"
            )
