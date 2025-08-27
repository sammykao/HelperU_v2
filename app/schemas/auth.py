from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from app.utils.validators import validate_phone_number, normalize_phone_number


class PhoneOTPRequest(BaseModel):
    """Request to send OTP to phone number"""

    phone: str = Field(..., description="Phone number to send OTP to")

    @validator("phone")
    def validate_phone(cls, v):
        is_valid, error_msg = validate_phone_number(v)
        if not is_valid:
            raise ValueError(error_msg)
        return normalize_phone_number(v)


class PhoneOTPVerifyRequest(BaseModel):
    """Request to verify OTP from phone"""

    phone: str = Field(..., description="Phone number that received OTP")
    token: str = Field(..., description="OTP token received via SMS")

    @validator("phone")
    def validate_phone(cls, v):
        is_valid, error_msg = validate_phone_number(v)
        if not is_valid:
            raise ValueError(error_msg)
        return normalize_phone_number(v)


class ClientSignupRequest(BaseModel):
    """Request to sign up a new client"""

    phone: str = Field(..., description="Client's phone number")

    @validator("phone")
    def validate_phone(cls, v):
        is_valid, error_msg = validate_phone_number(v)
        if not is_valid:
            raise ValueError(error_msg)
        return normalize_phone_number(v)


class ClientProfileUpdateRequest(BaseModel):
    """Request to complete client profile"""

    first_name: str = Field(
        ..., min_length=1, max_length=50, description="Client's first name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=50, description="Client's last name"
    )
    email: str = Field(
        ..., min_length=4, max_length=100, description="Client's email address"
    )
    pfp_url: Optional[str] = Field(None, description="Profile picture URL")


class HelperSignupRequest(BaseModel):
    """Request to sign up a new helper"""

    email: EmailStr = Field(..., description="Helper's email address")
    phone: str = Field(..., description="Helper's phone number")

    @validator("phone")
    def validate_phone(cls, v):
        is_valid, error_msg = validate_phone_number(v)
        if not is_valid:
            raise ValueError(error_msg)
        return normalize_phone_number(v)


class HelperProfileUpdateRequest(BaseModel):
    """Request to complete helper profile"""

    first_name: str = Field(
        ..., min_length=1, max_length=50, description="Helper's first name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=50, description="Helper's last name"
    )
    college: str = Field(
        ..., min_length=1, max_length=100, description="Helper's college/university"
    )
    bio: str = Field(..., min_length=10, max_length=500, description="Helper's bio")
    graduation_year: int = Field(
        ..., ge=2020, le=2030, description="Expected graduation year"
    )
    zip_code: str = Field(..., pattern=r"^\d{5}$", description="5-digit ZIP code")
    pfp_url: Optional[str] = Field(None, description="Profile picture URL")


class AuthResponse(BaseModel):
    """Standard authentication response"""

    success: bool
    message: str
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    profile_completed: Optional[bool] = None
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None


class ProfileStatusResponse(BaseModel):
    """Response indicating profile completion status"""

    profile_completed: bool
    email_verified: bool
    phone_verified: bool
    user_type: str  # "client" or "helper"


class UserProfileStatusResponse(BaseModel):
    """Response for user profile status"""

    user_type: str
    profile_completed: bool
    email_verified: bool
    phone_verified: bool
    profile_data: Optional[dict] = (
        None  # Will contain validated ClientProfileData or HelperProfileData
    )


class HelperEmailVerificationResponse(BaseModel):
    """Response for helper email verification status"""

    success: bool
    email: str
    email_verified: bool
    email_verified_at: Optional[str] = None
    user_id: str
    message: str


# New response models to replace Dict[str, Any]


class OTPResponse(BaseModel):
    """Response for OTP operations"""

    success: bool
    message: str


class ClientProfileResponse(BaseModel):
    """Response for client profile operations"""

    success: bool
    message: str
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class HelperAccountResponse(BaseModel):
    """Response for helper account creation"""

    success: bool
    message: str
    user_id: Optional[str] = None


class HelperProfileResponse(BaseModel):
    """Response for helper profile operations"""

    success: bool
    message: str
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class HelperVerificationResponse(BaseModel):
    """Response for helper verification completion"""

    success: bool
    message: str
    user_id: Optional[str] = None


class UserProfileResponse(BaseModel):
    """Response for user profile retrieval"""

    success: bool
    profile_status: UserProfileStatusResponse
    profile: Optional[dict] = None


class LogoutResponse(BaseModel):
    """Response for logout operations"""

    success: bool
    message: str


class CurrentUser(BaseModel):
    """Current authenticated user data"""

    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    email_confirmed_at: Optional[str] = None
    phone_confirmed_at: Optional[str] = None
    created_at: Optional[str] = None


class HelperVerificationWebhookData(BaseModel):
    """Data structure for helper verification webhook from Supabase"""

    id: Optional[str] = Field(None, description="User ID")
    sub: Optional[str] = Field(None, description="Alternative user ID field")
    email: Optional[str] = Field(None, description="User's email address")
    email_confirmed_at: Optional[str] = Field(
        None, description="When email was confirmed"
    )
    phone: Optional[str] = Field(None, description="User's phone number")
    phone_number: Optional[str] = Field(None, description="Alternative phone field")
    phone_confirmed_at: Optional[str] = Field(
        None, description="When phone was confirmed"
    )

    @property
    def user_id(self) -> str:
        """Get the user ID from either id or sub field"""
        return self.id or self.sub or ""

    @property
    def phone_number_final(self) -> Optional[str]:
        """Get the phone number from either phone or phone_number field"""
        return self.phone or self.phone_number
