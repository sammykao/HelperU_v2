from fastapi import APIRouter, Depends, HTTPException, status
from app.deps.supabase import get_current_user, get_account_service
from app.schemas.auth import CurrentUser
from app.schemas.account import (
    PasswordChangeRequest,
    NotificationSettings,
    AccountStats,
    AccountProfileResponse,
    PasswordChangeResponse,
    NotificationSettingsResponse,
    AccountActivityResponse,
    AccountDeletionResponse
)
from app.services.account_service import AccountService

router = APIRouter()

#  Think of it this way:
# /users/* = "Edit Profile" Section
# /account/* = "Account Settings" Section



@router.get("/", response_model=AccountProfileResponse)
async def get_account_profile(
    current_user: CurrentUser = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get comprehensive account profile information"""
    try:
        return await account_service.get_account_overview(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account profile: {str(e)}"
        )


@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    request: PasswordChangeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Change user password"""
    try:
        return await account_service.change_password(current_user.id, request.new_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


@router.get("/stats", response_model=AccountStats)
async def get_account_stats(
    current_user: CurrentUser = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get user account statistics"""
    try:
        return await account_service.get_account_stats(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account stats: {str(e)}"
        )


@router.get("/notifications", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: CurrentUser = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get user notification preferences"""
    try:
        return await account_service.get_notification_settings()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification settings: {str(e)}"
        )


@router.put("/notifications", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    settings: NotificationSettings,
    current_user: CurrentUser = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Update user notification preferences"""
    try:
        return await account_service.update_notification_settings(settings)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification settings: {str(e)}"
        )


@router.delete("/", response_model=AccountDeletionResponse)
async def delete_account(
    current_user: CurrentUser = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Delete user account (soft delete)"""
    try:
        return await account_service.delete_account(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )


@router.get("/activity", response_model=AccountActivityResponse)
async def get_account_activity(
    current_user: CurrentUser = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service),
    limit: int = 20,
    offset: int = 0
):
    """Get recent account activity"""
    try:
        return await account_service.get_account_activity(current_user.id, limit, offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account activity: {str(e)}"
        )
