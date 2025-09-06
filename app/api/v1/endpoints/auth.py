from fastapi import APIRouter, Depends, HTTPException, status

from app.deps.supabase import get_current_user, get_profile_service, get_auth_service
from app.services.auth_service import AuthService
from app.schemas.auth import (
    PhoneOTPRequest,
    PhoneOTPVerifyRequest,
    ClientSignupRequest,
    ClientProfileUpdateRequest,
    HelperSignupRequest,
    HelperProfileUpdateRequest,
    ProfileStatusResponse,
    OTPResponse,
    ClientProfileResponse,
    HelperAccountResponse,
    HelperProfileResponse,
    HelperVerificationResponse,
    HelperVerificationWebhookData,
    HelperEmailVerificationResponse,
    LogoutResponse,
    CurrentUser,
    ClientAccountExistanceResponse
)

router = APIRouter()


@router.post("/client/signup", response_model=OTPResponse)
async def client_signup(
    request: ClientSignupRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """Sign up a new client with phone number"""
    try:
        result = await auth_service.send_client_otp(request.phone)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}",
        )


@router.post("/client/signin", response_model=OTPResponse)
async def client_signin(
    request: PhoneOTPRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """Sign in existing client with phone number"""
    try:
        is_existing_client = await auth_service.check_account_existence(request.phone)
        if not is_existing_client.does_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )

        result = await auth_service.send_client_otp(request.phone)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}",
        )


@router.post("/client/verify-otp", response_model=ClientProfileResponse)
async def client_verify_otp(
    request: PhoneOTPVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verify OTP for client signup/signin"""
    try:
        result = await auth_service.verify_client_otp(request.phone, request.token)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}",
        )


@router.post("/client/complete-profile", response_model=ClientProfileResponse)
async def client_complete_profile(
    request: ClientProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Complete client profile with names"""
    try:
        user_id = current_user.id
        result = await auth_service.complete_client_profile(user_id, request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete profile: {str(e)}",
        )

@router.get("/client/check-completion", response_model=ClientAccountExistanceResponse)
async def check_helper_existence(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Check if a client account exists"""
    try:
        phone = current_user.phone
        result = await auth_service.check_account_existence(phone)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to check helper existence: {str(e)}")



@router.post("/helper/signup", response_model=HelperAccountResponse)
async def helper_signup(
    request: HelperSignupRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """Sign up a new helper with email and phone"""
    try:
        result = await auth_service.create_helper_account(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create helper account: {str(e)}",
        )


@router.post("/helper/signin", response_model=OTPResponse)
async def helper_signin(
    request: PhoneOTPRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """Sign in existing helper with phone number"""
    try:
        result = await auth_service.send_helper_otp(request.phone)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}",
        )


@router.post("/helper/verify-otp", response_model=HelperProfileResponse)
async def helper_verify_otp(
    request: PhoneOTPVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verify OTP for helper signin"""
    try:
        result = await auth_service.verify_helper_otp(request.phone, request.token)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}",
        )


@router.post("/helper/complete-profile", response_model=HelperProfileResponse)
async def helper_complete_profile(
    request: HelperProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Complete helper profile with all details"""
    try:
        user_id = current_user.id
        result = await auth_service.complete_helper_profile(user_id, request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete profile: {str(e)}",
        )


@router.post("/helper/complete-verification", response_model=HelperVerificationResponse)
async def helper_complete_verification(
    user_data: HelperVerificationWebhookData,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Complete helper verification (called by Supabase webhook)"""
    try:
        result = await auth_service.complete_helper_verification(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete verification: {str(e)}",
        )


@router.get("/profile-status", response_model=ProfileStatusResponse)
async def get_profile_status(
    current_user: CurrentUser = Depends(get_current_user),
    profile_service=Depends(get_profile_service),
):
    """Get current user's profile completion status"""
    try:
        user_id = current_user.id
        profile_status = await profile_service.get_user_profile_status(user_id)

        return ProfileStatusResponse(
            profile_completed=profile_status.profile_completed,
            email_verified=profile_status.email_verified,
            phone_verified=profile_status.phone_verified,
            user_type=profile_status.user_type,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile status: {str(e)}",
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Logout current user"""
    try:
        # The auth service should handle the logout logic
        result = await auth_service.logout_user(current_user.id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout: {str(e)}",
        )


@router.post("/resend-email-verification")
async def resend_email_verification(
    request: dict, auth_service: AuthService = Depends(get_auth_service)
):
    """Resend email verification link"""
    try:
        email = request.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        result = await auth_service.resend_email_verification(email)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend email verification: {str(e)}",
        )


@router.post("/verify-email-otp", response_model=OTPResponse)
async def verify_email_otp(
    request: dict, auth_service: AuthService = Depends(get_auth_service)
):
    """Verify email using OTP code"""
    try:
        email = request.get("email")
        otp_code = request.get("otp_code")

        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        if not otp_code:
            raise HTTPException(status_code=400, detail="OTP code is required")

        result = await auth_service.verify_email_otp(email, otp_code)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify email OTP: {str(e)}",
        )


@router.get(
    "/helper/email-verification-status/{user_id}",
    response_model=HelperEmailVerificationResponse,
)
async def check_helper_email_verification(
    user_id: str, auth_service: AuthService = Depends(get_auth_service)
):
    """Check if a helper's email is verified by user ID"""
    try:
        result = await auth_service.check_helper_email_verification(user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check email verification: {str(e)}",
        )

@router.post("/helper/update-email", response_model=OTPResponse)
async def update_helper_email(
    request: dict, auth_service: AuthService = Depends(get_auth_service), current_user: CurrentUser = Depends(get_current_user)
):
    """Update helper email"""
    try:
        email = request.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        user_id = request.get("user_id") or current_user.id
        result = await auth_service.update_helper_email(user_id, email)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update helper email: {str(e)}")


@router.get("/helper/check-completion", response_model=bool)
async def check_helper_completion(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Check if a helper account is complete"""
    try:
        result = await auth_service.check_helper_completion(current_user.id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to check helper completion: {str(e)}")