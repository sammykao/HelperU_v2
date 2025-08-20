from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.deps.supabase import get_current_user, get_profile_service, get_stripe_service
from app.schemas.subscription import (
    SubscriptionStatus,
    CreateSubscriptionRequest,
    CreateSubscriptionResponse,
    CancelSubscriptionResponse
)
from app.services.stripe_service import StripeService
from app.schemas.auth import CurrentUser

router = APIRouter()


@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user: CurrentUser = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """Get current user's subscription status and post limits"""
    try:
        user_id = current_user.id
        status_info = await stripe_service.get_subscription_status(user_id)
        return SubscriptionStatus(**status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription status: {str(e)}"
        )


@router.post("/create", response_model=CreateSubscriptionResponse)
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service),
    profile_service = Depends(get_profile_service)
):
    """Create a new subscription for the current user"""
    try:
        user_id = current_user.id
        email = current_user.email or ""
        
        # Get user profile data for name
        profile = await profile_service.get_user_profile_status(user_id)
        
        # Extract name from profile or use email as fallback
        if profile and profile.profile_data:
            first_name = profile.profile_data.get("first_name", "")
            last_name = profile.profile_data.get("last_name", "")
            name = f"{first_name} {last_name}".strip()
        else:
            name = email.split("@")[0] if email else "User"
        
        # Ensure user has a Stripe customer record
        if not await stripe_service.get_subscription_status(user_id):
            await stripe_service.create_customer(user_id, email, name)
        
        # Create subscription (price_id is optional, defaults to premium)
        subscription_data = await stripe_service.create_subscription(
            user_id, 
            request.price_id
        )
        
        return CreateSubscriptionResponse(**subscription_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.post("/cancel", response_model=CancelSubscriptionResponse)
async def cancel_subscription(
    current_user: CurrentUser = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """Cancel the current user's subscription"""
    try:
        user_id = current_user.id
        success = await stripe_service.cancel_subscription(user_id)
        
        if success:
            return CancelSubscriptionResponse(
                success=True,
                message="Subscription will be canceled at the end of the current period"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found to cancel"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing stripe-signature header"
            )
        
        success = await stripe_service.handle_webhook(payload, sig_header)
        
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook processing failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook error: {str(e)}"
        )
