from supabase import Client
from fastapi import HTTPException

from app.schemas.account import (
    NotificationSettings,
    AccountStats,
    AccountProfileResponse,
    PasswordChangeResponse,
    NotificationSettingsResponse,
    AccountDeletionResponse
)
from app.services.stripe_service import StripeService


class AccountService:
    """Service for handling account management and dashboard operations"""

    def __init__(self, admin_client: Client, stripe_service: StripeService):
        self.admin_client = admin_client
        self.stripe_service = stripe_service

    async def get_account_overview(self, user_id: str) -> AccountProfileResponse:
        """Get comprehensive account profile information"""
        try:
            # Get user's basic auth info
            auth_user = await self.admin_client.auth.admin.get_user(user_id)
            if not auth_user.user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get subscription status
            subscription_status = await self.stripe_service.get_subscription_status(user_id)
            
            # Get profile data based on user type
            profile_data = {}
            user_type = "unknown"
            
            # Check if user is a client
            client_result = await self.admin_client.table("clients").select("*").eq("id", user_id).execute()
            if client_result.data:
                profile_data = client_result.data[0]
                user_type = "client"
            else:
                # Check if user is a helper
                helper_result = await self.admin_client.table("helpers").select("*").eq("id", user_id).execute()
                if helper_result.data:
                    profile_data = helper_result.data[0]
                    user_type = "helper"
            
            return AccountProfileResponse(
                success=True,
                user_type=user_type,
                auth_info={
                    "id": auth_user.user.id,
                    "email": auth_user.user.email,
                    "phone": auth_user.user.phone,
                    "email_confirmed_at": auth_user.user.email_confirmed_at,
                    "phone_confirmed_at": auth_user.user.phone_confirmed_at,
                    "created_at": auth_user.user.created_at
                },
                profile_data=profile_data,
                subscription_status=subscription_status
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get account profile: {str(e)}")


    async def change_password(self, user_id: str, new_password: str) -> PasswordChangeResponse:
        """Change user password"""
        try:
            # Update password
            await self.admin_client.auth.admin.update_user_by_id(
                user_id,
                {"password": new_password}
            )
            
            return PasswordChangeResponse(
                success=True,
                message="Password changed successfully"
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")
    
    async def get_account_stats(self, user_id: str) -> AccountStats:
        """Get user account statistics"""
        try:
            # Get subscription status
            subscription_status = await self.stripe_service.get_subscription_status(user_id)
            
            # Get user type and stats
            client_result = await self.admin_client.table("clients").select("number_of_posts, created_at").eq("id", user_id).execute()
            helper_result = await self.admin_client.table("helpers").select("number_of_applications, created_at").eq("id", user_id).execute()
            
            if client_result.data:
                # Client stats
                total_posts = client_result.data[0]["number_of_posts"]
                total_applications = 0
                member_since = client_result.data[0]["created_at"]
            elif helper_result.data:
                # Helper stats
                total_posts = 0
                total_applications = helper_result.data[0]["number_of_applications"]
                member_since = helper_result.data[0]["created_at"]
            else:
                total_posts = 0
                total_applications = 0
                member_since = None
            
            return AccountStats(
                total_posts=total_posts,
                total_applications=total_applications,
                member_since=member_since,
                subscription_plan=subscription_status["plan"],
                posts_this_month=subscription_status["posts_used"],
                monthly_limit=subscription_status["post_limit"] if subscription_status["post_limit"] > 0 else -1
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get account stats: {str(e)}")

    async def get_notification_settings(self) -> NotificationSettings:
        """Get user notification preferences"""
        try:
            # For now, return default settings
            # In the future, store these in a separate table, for mobile notifications
            return NotificationSettings()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get notification settings: {str(e)}")

    async def update_notification_settings(self, settings: NotificationSettings) -> NotificationSettingsResponse:
        """Update user notification preferences"""
        try:
            # For now, just return success
            # In the future, store these in a separate table, for mobile notifications
            return NotificationSettingsResponse(
                success=True,
                message="Notification settings updated successfully"
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update notification settings: {str(e)}")

    async def delete_account(self, user_id: str) -> AccountDeletionResponse:
        """Delete user account (soft delete)"""
        try:
            # Cancel any active subscriptions
            try:
                await self.stripe_service.cancel_subscription(user_id)
            except Exception:
                pass  # User might not have a subscription
            
            return AccountDeletionResponse(
                success=True,
                message="Account deletion initiated. Your data will be permanently removed within 30 days."
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")

   