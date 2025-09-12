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
        return status_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription status: {str(e)}"
        )


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateSubscriptionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service),
    profile_service = Depends(get_profile_service)
):
    """Create a Stripe Checkout session for subscription"""
    try:
        user_id = current_user.id
        # Get user profile data for name
        profile = await profile_service.get_client_profile(user_id)
        email = current_user.email or profile.email or ""
        # Ensure user has a subscription record in the database
        if not await stripe_service.user_exists_in_subscriptions(user_id):
            # Extract name from profile or use email as fallback
            if profile and profile.first_name and profile.last_name:
                name = f"{profile.first_name} {profile.last_name}".strip()
            else:
                name = email.split("@")[0] if email else "User"
            await stripe_service.create_customer(user_id, email, name)
        
        # Create checkout session
        checkout_url = await stripe_service.create_checkout_session(
            user_id, 
            request.price_id
        )
        
        return {"checkout_url": checkout_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
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
