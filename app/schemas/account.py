from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any


class AccountUpdateRequest(BaseModel):
    """Request to update account information"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None)
    pfp_url: Optional[str] = Field(None)


class PasswordChangeRequest(BaseModel):
    """Request to change password"""
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class NotificationSettings(BaseModel):
    """User notification preferences"""
    email_notifications: bool = Field(True, description="Receive email notifications")
    sms_notifications: bool = Field(True, description="Receive SMS notifications")
    push_notifications: bool = Field(True, description="Receive push notifications")
    marketing_emails: bool = Field(False, description="Receive marketing emails")


class AccountStats(BaseModel):
    """User account statistics"""
    total_posts: int
    total_applications: int
    member_since: str
    subscription_plan: str
    posts_this_month: int
    monthly_limit: int


class AccountProfileResponse(BaseModel):
    """Response model for account profile"""
    success: bool
    user_type: str
    auth_info: Dict[str, Any]
    profile_data: Dict[str, Any]
    subscription_status: Dict[str, Any]


class PasswordChangeResponse(BaseModel):
    """Response model for password change"""
    success: bool
    message: str


class NotificationSettingsResponse(BaseModel):
    """Response model for notification settings update"""
    success: bool
    message: str


class AccountActivityResponse(BaseModel):
    """Response model for account activity"""
    success: bool
    activity: list[Dict[str, Any]]
    total_count: int


class AccountDeletionResponse(BaseModel):
    """Response model for account deletion"""
    success: bool
    message: str
