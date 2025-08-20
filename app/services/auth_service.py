from fastapi import HTTPException
from supabase import Client

from app.schemas.auth import (
    ClientProfileUpdateRequest, 
    HelperSignupRequest, 
    HelperProfileUpdateRequest,
    OTPResponse,
    ClientProfileResponse,
    HelperAccountResponse,
    HelperProfileResponse,
    HelperVerificationResponse,
    HelperVerificationWebhookData
)
from app.utils.validators import normalize_phone_number, validate_phone_number


class AuthService:
    """Service for handling authentication operations"""

    def __init__(self, public_client: Client, admin_client: Client):
        self.public_client = public_client
        self.admin_client = admin_client

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for consistent processing"""
        return normalize_phone_number(phone)

    async def send_client_otp(self, phone: str) -> OTPResponse:
        """Send OTP to client phone number"""
        try:
            # Normalize phone number for consistent processing
            normalized_phone = self._normalize_phone(phone)
            
            is_valid, error_msg = validate_phone_number(normalized_phone)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid phone number: {error_msg}")
            
            self.public_client.auth.sign_in_with_otp({
                "phone": normalized_phone,
            })
            return OTPResponse(
                success=True,
                message="OTP sent successfully"
            )
        except HTTPException:
            raise
        except Exception as exc:
            error_msg = str(exc)
            if "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail="Too many OTP requests. Please wait before requesting another.")
            elif "invalid" in error_msg.lower():
                raise HTTPException(status_code=400, detail="Invalid phone number format.")
            else:
                raise HTTPException(status_code=400, detail=f"Failed to send OTP: {error_msg}")


    async def verify_client_otp(self, phone: str, token: str) -> ClientProfileResponse:
        """Verify client OTP and create/update profile"""
        try:
            # Normalize phone number for consistent processing
            normalized_phone = self._normalize_phone(phone)
            
            # Verify OTP
            auth_response = self.public_client.auth.verify_otp({
                "phone": normalized_phone,
                "token": token,
                "type": "sms",
            })
            
            # Check if verification was successful
            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Invalid OTP token")
            
            user_id = auth_response.user.id
            
            # Get the session to extract tokens
            session = self.public_client.auth.get_session()
            if session is None:
                # If no session, try to get user data from the auth response
                access_token = getattr(auth_response, "access_token", None)
                refresh_token = getattr(auth_response, "refresh_token", None)
                
                if not access_token:
                    raise HTTPException(status_code=400, detail="Failed to establish session after OTP verification")
            else:
                access_token = getattr(session, "access_token", None)
                refresh_token = getattr(session, "refresh_token", None)

            return ClientProfileResponse(
                success=True,
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                message="Client verified successfully"
            )
        except HTTPException:
            raise
        except Exception as exc:
            # Check for specific Supabase errors
            error_msg = str(exc)
            if "expired" in error_msg.lower() or "invalid" in error_msg.lower():
                print(error_msg)
                raise HTTPException(status_code=400, detail="OTP token has expired or is invalid. Please request a new OTP.")
            elif "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail="Too many OTP attempts. Please wait before trying again.")
            else:
                raise HTTPException(status_code=400, detail=f"Failed to verify OTP: {error_msg}")


    async def complete_client_profile(self, user_id: str, payload: ClientProfileUpdateRequest) -> ClientProfileResponse:
        """Complete client profile with names"""
        try:
            
            # Get user's phone from auth.users
            user_info = self.admin_client.auth.admin.get_user_by_id(user_id)
            user_phone = user_info.user.phone if user_info.user else ""
        
            # Create or update new profile
            self.admin_client.table("clients").upsert({
                "id": user_id,
                "phone": user_phone,
                "email": payload.email,
                "first_name": payload.first_name,
                "last_name": payload.last_name,
                "pfp_url": payload.pfp_url,
            }).execute()

            return ClientProfileResponse(
                success=True,
                user_id=user_id,
                message="Client profile completed successfully"
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to complete profile: {str(exc)}")


    async def create_helper_account(self, payload: HelperSignupRequest) -> HelperAccountResponse:
        """Create helper account with email and phone"""
        try:
            # Normalize phone number for consistent processing
            normalized_phone = self._normalize_phone(payload.phone)
            
            # Create user with email
            user_response = self.admin_client.auth.admin.create_user({
                "email": payload.email,
                "phone": normalized_phone,
                "email_confirm": False,
                "phone_confirm": False,
            })

            if not user_response.user:
                raise HTTPException(status_code=400, detail="Failed to create helper account")

            user_id = user_response.user.id

            # Send OTP to phone
            self.public_client.auth.sign_in_with_otp({
                "phone": normalized_phone,
            })

            return HelperAccountResponse(
                success=True,
                user_id=user_id,
                message="Helper account created. Please verify phone and email to complete signup."
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to create helper account: {str(exc)}")

    async def send_helper_otp(self, phone: str) -> OTPResponse:
        """Send OTP to helper phone number"""
        try:
            # Normalize phone number for consistent processing
            normalized_phone = self._normalize_phone(phone)
            
            is_valid, error_msg = validate_phone_number(normalized_phone)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid phone number: {error_msg}")
            
            self.public_client.auth.sign_in_with_otp({
                "phone": normalized_phone,
            })
            return OTPResponse(
                success=True,
                message="OTP sent successfully"
            )
        except HTTPException:
            raise
        except Exception as exc:
            error_msg = str(exc)
            if "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail="Too many OTP requests. Please wait before requesting another.")
            elif "invalid" in error_msg.lower():
                raise HTTPException(status_code=400, detail="Invalid phone number format.")
            else:
                raise HTTPException(status_code=400, detail=f"Failed to send OTP: {error_msg}")


    async def verify_helper_otp(self, phone: str, token: str) -> HelperProfileResponse:
        """Verify helper phone OTP"""
        try:
            # Normalize phone number for consistent processing
            normalized_phone = self._normalize_phone(phone)
            
            # Verify OTP
            auth_response = self.public_client.auth.verify_otp({
                "phone": normalized_phone,
                "token": token,
                "type": "sms",
            })
            
            # Check if verification was successful
            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Invalid OTP token")
            
            user_id = auth_response.user.id

            return HelperProfileResponse(
                success=True,
                user_id=user_id,
                message="Helper phone verified successfully"
            )
        except HTTPException:
            raise
        except Exception as exc:
            # Check for specific Supabase errors
            error_msg = str(exc)
            if "expired" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(status_code=400, detail="OTP token has expired or is invalid. Please request a new OTP.")
            elif "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail="Too many OTP attempts. Please wait before trying again.")
            else:
                raise HTTPException(status_code=400, detail=f"Failed to verify OTP: {error_msg}")


    async def complete_helper_profile(self, user_id: str, payload: HelperProfileUpdateRequest) -> HelperProfileResponse:
        """Complete helper profile with all details"""
        try:
           
            # Get user's phone and email from auth.users
            user_info = self.admin_client.auth.admin.get_user_by_id(user_id)
            user_phone = user_info.user.phone if user_info.user else ""
            user_email = user_info.user.email if user_info.user else ""
            
    
            self.admin_client.table("helpers").upsert({
                "id": user_id,
                "phone": user_phone,
                "email": user_email,
                "first_name": payload.first_name,
                "last_name": payload.last_name,
                "college": payload.college,
                "bio": payload.bio,
                "graduation_year": payload.graduation_year,
                "zip_code": payload.zip_code,
                "pfp_url": payload.pfp_url,
            }).execute()

            return HelperProfileResponse(
                success=True,
                user_id=user_id,
                message="Helper profile completed successfully"
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to complete profile: {str(exc)}")


    async def complete_helper_verification(self, user: HelperVerificationWebhookData) -> HelperVerificationResponse:
        """Complete helper verification and create profile"""
        try:
            # Use the property methods for cleaner access
            user_id = user.user_id
            email_confirmed_at = user.email_confirmed_at
            phone_confirmed_at = user.phone_confirmed_at

            if not email_confirmed_at or not phone_confirmed_at:
                raise HTTPException(status_code=400, detail="Email and phone must both be verified")

            # Don't create profile here - it will be created when they complete their profile
            return HelperVerificationResponse(
                success=True,
                user_id=user_id,
                message="Helper verification completed successfully"
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to complete verification: {str(exc)}")

    async def logout_user(self, user_id: str) -> dict:
        """Logout user by signing out from Supabase"""
        try:
            # Sign out the user from Supabase
            self.public_client.auth.sign_out()
            
            return {
                "success": True, 
                "message": "Logged out successfully"
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to logout: {str(exc)}")
