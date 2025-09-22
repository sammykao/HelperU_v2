from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserProfileStatusResponse(BaseModel):
    """Response for user profile status"""
    user_type: str
    profile_completed: bool
    email_verified: bool
    phone_verified: bool
    profile_data: Optional[dict] = None  # Will contain validated ClientProfileData or HelperProfileData


class ProfileUpdateResponse(BaseModel):
    """Response for profile update operations"""
    success: bool
    message: str
    profile_data: Optional[dict] = None  # Keep as dict for flexibility, but it will contain validated data


class ClientProfileData(BaseModel):
    """Client profile data structure"""
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    pfp_url: Optional[str] = None
    number_of_posts: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HelperProfileData(BaseModel):
    """Helper profile data structure"""
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    bio: Optional[str] = None
    graduation_year: Optional[int] = None
    zip_code: Optional[str] = None
    pfp_url: Optional[str] = None
    number_of_applications: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProfileUpdateData(BaseModel):
    """Data for updating profiles"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    pfp_url: Optional[str] = None
    # Helper-specific fields
    college: Optional[str] = None
    bio: Optional[str] = None
    graduation_year: Optional[int] = None
    zip_code: Optional[str] = None

class ProfileExpoNotificationRequest(BaseModel):
    """request to register notification push token"""
    expo_token: str
