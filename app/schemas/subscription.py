from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class SubscriptionStatus(BaseModel):
    """Current user's subscription status and post limits"""
    plan: str = Field(..., description="Subscription plan (free, basic, premium, enterprise)")
    status: str = Field(..., description="Subscription status (active, canceled, past_due, etc.)")
    post_limit: int = Field(..., description="Monthly post limit (-1 for unlimited)")
    posts_used: int = Field(..., description="Posts used this month")


class CreateSubscriptionRequest(BaseModel):
    """Request to create a new subscription"""
    price_id: Optional[str] = Field(None, description="Stripe price ID for the subscription plan (optional, defaults to premium)")


class CreateSubscriptionResponse(BaseModel):
    """Response after creating a subscription"""
    subscription_id: str = Field(..., description="Stripe subscription ID")
    client_secret: str = Field(..., description="Payment intent client secret for frontend")
    status: str = Field(..., description="Subscription status")


class CancelSubscriptionResponse(BaseModel):
    """Response after canceling a subscription"""
    success: bool = Field(..., description="Whether cancellation was successful")
    message: str = Field(..., description="Cancellation message")


class StripeCustomerData(BaseModel):
    """Data for creating a Stripe customer"""
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="Customer email")
    name: str = Field(..., description="Customer name")


class StripeSubscriptionData(BaseModel):
    """Data for creating a Stripe subscription"""
    user_id: str = Field(..., description="User ID")
    price_id: str = Field(..., description="Stripe price ID")
    customer_id: str = Field(..., description="Stripe customer ID")


class SubscriptionData(BaseModel):
    """Subscription data structure"""
    user_id: str = Field(..., description="User ID")
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")
    stripe_subscription_id: Optional[str] = Field(None, description="Stripe subscription ID")
    plan: str = Field(..., description="Subscription plan")
    status: str = Field(..., description="Subscription status")
    current_period_start: Optional[int] = Field(None, description="Current period start timestamp")
    current_period_end: Optional[int] = Field(None, description="Current period end timestamp")
    cancel_at_period_end: Optional[bool] = Field(False, description="Whether subscription will cancel at period end")


class SubscriptionEventData(BaseModel):
    """Data for storing subscription events"""
    stripe_event_id: str = Field(..., description="Stripe event ID")
    event_type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data object")


class PostLimitInfo(BaseModel):
    """Information about user's post limits"""
    post_limit: int = Field(..., description="Monthly post limit (-1 for unlimited)")
    posts_used: int = Field(..., description="Posts used this month")
    can_post: bool = Field(..., description="Whether user can post more")


class WebhookResult(BaseModel):
    """Result of webhook processing"""
    action: str = Field(..., description="Action taken by the webhook")
    success: bool = Field(..., description="Whether webhook was processed successfully")
    event_id: str = Field(..., description="Stripe event ID")
    event_type: str = Field(..., description="Event type")


class OnetimePaymentRequest(BaseModel):
    """Request for a one-time payment"""
    price_id: Optional[str] = Field(None, description="Stripe price ID for the one-time payment (optional, defaults to STRIPE_ONE_TIME_POST_PRICE_ID)")