from fastapi import HTTPException
from supabase import Client

from app.schemas.auth import (
    ClientAccountExistanceResponse,
    ClientProfileUpdateRequest,
    HelperSignupRequest,
    HelperProfileUpdateRequest,
    OTPResponse,
    ClientProfileResponse,
    HelperAccountResponse,
    HelperProfileResponse,
    HelperVerificationResponse,
    HelperVerificationWebhookData,
    HelperEmailVerificationResponse,
    LogoutResponse,
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
                raise HTTPException(
                    status_code=400, detail=f"Invalid phone number: {error_msg}"
                )

            self.public_client.auth.sign_in_with_otp(
                {
                    "phone": normalized_phone,
                }
            )
            return OTPResponse(success=True, message="OTP sent successfully")
        except HTTPException:
            raise
        except Exception as exc:
            error_msg = str(exc)
            if "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Too many OTP requests. Please wait before requesting another.",
                )
            elif "invalid" in error_msg.lower():
                raise HTTPException(
                    status_code=400, detail="Invalid phone number format."
                )
            else:
                raise HTTPException(
                    status_code=400, detail=f"Failed to send OTP: {error_msg}"
                )

    async def verify_client_otp(self, phone: str, token: str) -> ClientProfileResponse:
        """Verify client OTP and create/update profile"""
        try:
            # Normalize phone number for consistent processing
            normalized_phone = self._normalize_phone(phone)

            # Verify OTP
            auth_response = self.public_client.auth.verify_otp(
                {
                    "phone": normalized_phone,
                    "token": token,
                    "type": "sms",
                }
            )

            # Check if verification was successful
            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Invalid OTP token")

            user_id = auth_response.user.id

            # Extract tokens directly from auth response
            # The session approach doesn't work reliably across HTTP requests
            access_token = getattr(auth_response, "access_token", None)
            refresh_token = getattr(auth_response, "refresh_token", None)

            # If tokens are not in auth_response, try to get from session as fallback
            if not access_token:
                session = self.public_client.auth.get_session()
                if session:
                    access_token = getattr(session, "access_token", None)
                    refresh_token = getattr(session, "refresh_token", None)

            if not access_token:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to establish session after OTP verification",
                )

            return ClientProfileResponse(
                success=True,
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                message="Client verified successfully",
            )
        except HTTPException:
            raise
        except Exception as exc:
            # Check for specific Supabase errors
            error_msg = str(exc)
            if "expired" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="OTP token has expired or is invalid. Please request a new OTP.",
                )
            elif "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Too many OTP attempts. Please wait before trying again.",
                )
            else:
                raise HTTPException(
                    status_code=400, detail=f"Failed to verify OTP: {error_msg}"
                )

    async def complete_client_profile(
        self, user_id: str, payload: ClientProfileUpdateRequest
    ) -> ClientProfileResponse:
        """Complete client profile with names"""
        try:

            # Get user's phone from auth.users
            user_info = self.admin_client.auth.admin.get_user_by_id(user_id)
            user_phone = user_info.user.phone if user_info.user else ""

            # Create or update new profile
            self.admin_client.table("clients").upsert(
                {
                    "id": user_id,
                    "phone": user_phone,
                    "email": payload.email,
                    "first_name": payload.first_name,
                    "last_name": payload.last_name,
                    "pfp_url": payload.pfp_url,
                }
            ).execute()

            return ClientProfileResponse(
                success=True,
                user_id=user_id,
                message="Client profile completed successfully",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=400, detail=f"Failed to complete profile: {str(exc)}"
            )

    async def create_helper_account(
        self, payload: HelperSignupRequest
    ) -> HelperAccountResponse:
        """Create helper account with email and phone"""
        try:
            # Normalize phone number for consistent processing
            normalized_phone = self._normalize_phone(payload.phone)

            # Check if helper account already exists (efficient single query)
            existing_helper = (
                self.public_client.table("helpers")
                .select("id")
                .eq("phone", normalized_phone)
                .limit(1)
                .execute()
            )
            if existing_helper.data:
                raise HTTPException(
                    status_code=400,
                    detail="Helper account already exists with this phone number",
                )
            # Check if client account exists with same phone - if so, append helper data to existing user
            existing_client = (
                self.admin_client.table("clients")
                .select("id")
                .eq("phone", normalized_phone)
                .limit(1)
                .execute()
            )
            if existing_client.data:
                # Get the existing user ID from the client profile
                user_id = existing_client.data[0]["id"]
                # If no existing email, update it. We can assume helper account doesnt exist becasue check above.
                self.admin_client.auth.admin.update_user_by_id(
                    user_id, {"email": payload.email, "email_confirm": False}
                )

            else:
                print("No existing account found, creating new user")

                # If no existing account found, create new user
                user_response = self.admin_client.auth.admin.create_user(
                    {
                        "email": payload.email,
                        "phone": normalized_phone,
                        "email_confirm": False,
                        "phone_confirm": False,
                    }
                )

                if not user_response.user:
                    raise HTTPException(
                        status_code=400, detail="Failed to create helper account"
                    )
                user_id = user_response.user.id

            # Send OTP to phone
            self.public_client.auth.sign_in_with_otp(
                {
                    "phone": normalized_phone,
                }
            )
            # self.public_client.auth.resend({"type": "signup", "email": payload.email})

            return HelperAccountResponse(
                success=True,
                user_id=user_id,
                message="Helper account created. Please verify phone and email to complete signup.",
            )
        except HTTPException:
            raise
        except Exception as exc:
            print(exc)
            raise HTTPException(
                status_code=400, detail=f"Failed to create helper account: {str(exc)}"
            )

    async def send_helper_otp(self, phone: str) -> OTPResponse:
        """Send OTP to helper phone number"""
        try:
            # Normalize phone number for consistent processing
            normalized_phone = self._normalize_phone(phone)

            is_valid, error_msg = validate_phone_number(normalized_phone)

            # check for a phone testing account
            # for example Apple testing account phone: +1-555-555-5555
            # corresponds to OTP code 123456
            if normalized_phone == "15555555555":
                return OTPResponse(
                    success=True, message="testing account login detected"
                )

            if not is_valid:
                raise HTTPException(
                    status_code=400, detail=f"Invalid phone number: {error_msg}"
                )

            self.public_client.auth.sign_in_with_otp(
                {
                    "phone": normalized_phone,
                }
            )
            return OTPResponse(success=True, message="OTP sent successfully")
        except HTTPException:
            raise
        except Exception as exc:
            error_msg = str(exc)
            if "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Too many OTP requests. Please wait before requesting another.",
                )
            elif "invalid" in error_msg.lower():
                raise HTTPException(
                    status_code=400, detail="Invalid phone number format."
                )
            else:
                raise HTTPException(
                    status_code=400, detail=f"Failed to send OTP: {error_msg}"
                )

    async def verify_email_otp(self, email: str, otp_code: str) -> OTPResponse:
        """Verify email using OTP code"""
        try:
            # Verify email OTP
            auth_response = self.public_client.auth.verify_otp(
                {
                    "email": email,
                    "token": otp_code,
                    "type": "email",
                }
            )

            # Check if verification was successful
            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Invalid OTP token")

            return OTPResponse(
                success=True, message=f"Email {email} verified successfully"
            )
        except HTTPException:
            raise
        except Exception as exc:
            # Check for specific Supabase errors
            error_msg = str(exc)
            if "expired" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="OTP token has expired or is invalid. Please request a new OTP.",
                )
            elif "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Too many OTP attempts. Please wait before trying again.",
                )
            else:
                raise HTTPException(
                    status_code=400, detail=f"Failed to verify email OTP: {error_msg}"
                )

    async def verify_helper_otp(self, phone: str, token: str) -> HelperProfileResponse:
        """Verify helper phone OTP"""
        try:
            # Normalize phone number for consistent processing
            normalized_phone = self._normalize_phone(phone)

            if normalized_phone == "15555555555" and token == "123456":
                email = "tester@apple.com"
                response = self.public_client.auth.sign_in_with_password(
                    credentials={
                        "phone": normalized_phone,
                        "password": "somethingSuperSecure",
                    }
                )

                helper_exist_check = (
                    self.admin_client.table("helpers")
                    .select("id")
                    .eq("id", response.user.id)
                    .execute()
                )

                if len(helper_exist_check.data) == 0:
                    print("testing user does not exist, creating account")

                    testing_profile = {
                        "id": response.user.id,
                        "email": email,
                        "phone": normalized_phone,
                        "first_name": "Tester",
                        "last_name": "Apple",
                        "pfp_url": "",
                        "college": "Apple University",
                        "bio": "This is a testing account for apple testers only, do not invite this account for tasks",
                        "graduation_year": 2026,
                        "zip_code": "02155",
                    }

                    result = (
                        self.admin_client.table("helpers")
                        .insert(testing_profile)
                        .execute()
                    )

                    if not result:
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to create helper testing acconut",
                        )

                return HelperProfileResponse(
                    success=True,
                    message="testing user session",
                    user_id=response.user.id,
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                )

            if normalized_phone == "15555555555" and token != "123456":
                raise HTTPException(
                    status_code=400,
                    detail="Got known tester account but incorrect OTP code",
                )

            # Verify OTP
            auth_response = self.public_client.auth.verify_otp(
                {
                    "phone": normalized_phone,
                    "token": token,
                    "type": "sms",
                }
            )

            # Check if verification was successful
            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Invalid OTP token")

            user_id = auth_response.user.id

            # Extract tokens directly from auth response
            # The session approach doesn't work reliably across HTTP requests
            access_token = getattr(auth_response, "access_token", None)
            refresh_token = getattr(auth_response, "refresh_token", None)

            # If tokens are not in auth_response, try to get from session as fallback
            if not access_token:
                session = self.public_client.auth.get_session()
                if session:
                    access_token = getattr(session, "access_token", None)
                    refresh_token = getattr(session, "refresh_token", None)

            if not access_token:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to establish session after OTP verification",
                )

            return HelperProfileResponse(
                success=True,
                user_id=user_id,
                message="Helper phone verified successfully",
                access_token=access_token,
                refresh_token=refresh_token,
            )
        except HTTPException:
            raise
        except Exception as exc:
            # Check for specific Supabase errors
            error_msg = str(exc)
            if "expired" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="OTP token has expired or is invalid. Please request a new OTP.",
                )
            elif "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Too many OTP attempts. Please wait before trying again.",
                )
            else:
                print(exc)
                raise HTTPException(
                    status_code=400, detail=f"Failed to verify OTP: {error_msg}"
                )

    async def complete_helper_profile(
        self, user_id: str, payload: HelperProfileUpdateRequest
    ) -> HelperProfileResponse:
        """Complete helper profile with all details"""
        try:

            # Get user's phone and email from auth.users
            user_info = self.admin_client.auth.admin.get_user_by_id(user_id)
            if (
                not user_info.user.email_confirmed_at
                or not user_info.user.phone_confirmed_at
            ):
                raise HTTPException(
                    status_code=400, detail="Email and phone must both be verified"
                )

            user_phone = user_info.user.phone if user_info.user else ""
            user_email = user_info.user.email if user_info.user else ""

            self.admin_client.table("helpers").upsert(
                {
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
                    "venmo": payload.venmo,
                }
            ).execute()

            return HelperProfileResponse(
                success=True,
                user_id=user_id,
                message="Helper profile completed successfully",
                access_token=None,
                refresh_token=None,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=400, detail=f"Failed to complete profile: {str(exc)}"
            )

    async def complete_helper_verification(
        self, user: HelperVerificationWebhookData
    ) -> HelperVerificationResponse:
        """Complete helper verification and create profile"""
        try:
            # Use the property methods for cleaner access
            user_id = user.user_id
            email_confirmed_at = user.email_confirmed_at
            phone_confirmed_at = user.phone_confirmed_at

            if not email_confirmed_at or not phone_confirmed_at:
                raise HTTPException(
                    status_code=400, detail="Email and phone must both be verified"
                )

            # Don't create profile here - it will be created when they complete their profile
            return HelperVerificationResponse(
                success=True,
                user_id=user_id,
                message="Helper verification completed successfully",
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to complete verification: {str(exc)}"
            )

    async def logout_user(self, user_id: str) -> LogoutResponse:
        """Logout user by signing out from Supabase"""
        try:
            # Sign out the user from Supabase
            self.public_client.auth.sign_out()

            return LogoutResponse(success=True, message="Logged out successfully")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to logout: {str(exc)}")

    async def resend_email_verification(self, email: str) -> OTPResponse:
        """Resend email verification link"""
        try:
            # Use Supabase's resend method for email verification
            self.public_client.auth.resend({"type": "signup", "email": email})

            return OTPResponse(
                success=True, message="Email verification link resent successfully"
            )
        except Exception as exc:
            error_msg = str(exc)
            if "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Too many resend requests. Please wait before requesting another.",
                )
            elif "user not found" in error_msg.lower():
                raise HTTPException(
                    status_code=404, detail="User not found with this email address"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to resend email verification: {error_msg}",
                )

    async def check_helper_email_verification(
        self, user_id: str
    ) -> HelperEmailVerificationResponse:
        """Check if a helper's email is verified by user ID"""
        try:
            # Get user by ID using admin API
            user_response = self.admin_client.auth.admin.get_user_by_id(user_id)

            if not user_response.user:
                raise HTTPException(status_code=404, detail="User not found")

            email_verified, email_verified_at, email = False, None, None
            if user_response.user.email_confirmed_at:
                email_verified = False
                email_verified_at = None
                email = user_response.user.email

            return HelperEmailVerificationResponse(
                success=True,
                email=email,
                email_verified=email_verified,
                email_verified_at=email_verified_at,
                user_id=user_id,
                message="Email verification status retrieved successfully",
            )

        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to check email verification: {str(exc)}",
            )

    async def check_account_existence(
        self, phone: str
    ) -> ClientAccountExistanceResponse:
        try:
            existing_client = (
                self.admin_client.table("clients")
                .select("id")
                .eq("phone", phone)
                .limit(1)
                .execute()
            )

            if not existing_client.data:
                return ClientAccountExistanceResponse(does_exist=False)

            return ClientAccountExistanceResponse(does_exist=True)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to check account existence: {str(exc)}",
            )

    async def update_helper_email(self, user_id: str, email: str) -> OTPResponse:
        """Update helper email"""
        try:
            self.admin_client.auth.admin.update_user_by_id(user_id, {"email": email})
            result = await self.resend_email_verification(email)
            if not result.success:
                raise HTTPException(
                    status_code=500, detail="Failed to resend email verification"
                )
            return result
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to update helper email: {str(exc)}"
            )

    async def check_helper_completion(self, user_id: str) -> bool:
        """Check if a helper account exists by email"""
        try:
            existing_helper = (
                self.admin_client.table("helpers")
                .select("id")
                .eq("id", user_id)
                .limit(1)
                .execute()
            )
            if not existing_helper.data:
                return False
            return True
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to check helper existence: {str(exc)}"
            )
