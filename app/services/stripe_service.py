import stripe
from app.core.config import settings
from supabase import Client
from fastapi import HTTPException
from datetime import datetime

from app.schemas.subscription import (
    SubscriptionStatus,
    CreateSubscriptionResponse,
    WebhookResult
)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    def __init__(self, admin_client: Client):
        self.admin_client = admin_client
    
    async def create_customer(self, user_id: str, email: str, name: str) -> str:
        """Create a Stripe customer and store the ID in Supabase"""
        try:
            # Create customer in Stripe
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": user_id}
            )
            
            # Store customer ID in Supabase
            self.admin_client.table("subscriptions").upsert({
                "user_id": user_id,
                "stripe_customer_id": customer.id,
                "plan": "free",
                "status": "active"
            }).execute()
            
            return customer.id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create Stripe customer: {str(e)}")
    
    async def create_subscription(self, user_id: str, price_id: str = None) -> CreateSubscriptionResponse:
        """Create a subscription for a user"""
        try:
            # Get user's Stripe customer ID
            result = self.admin_client.table("subscriptions").select("stripe_customer_id").eq("user_id", user_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="User not found in subscriptions table")
            
            customer_id = result.data[0]["stripe_customer_id"]
            
            # Use provided price_id or default to premium price
            subscription_price_id = price_id or settings.STRIPE_PREMIUM_PRICE_ID
            
            # Create subscription in Stripe
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": subscription_price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
            )
            
            # Update subscription in Supabase
            self.admin_client.table("subscriptions").upsert({
                "user_id": user_id,
                "stripe_subscription_id": subscription.id,
                "stripe_customer_id": customer_id,
                "plan": "premium",
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end
            }).execute()
            
            return CreateSubscriptionResponse(
                subscription_id=subscription.id,
                client_secret=subscription.latest_invoice.payment_intent.client_secret,
                status=subscription.status
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")
    
    async def cancel_subscription(self, user_id: str) -> bool:
        """Cancel a user's subscription"""
        try:
            # Get subscription ID
            result = self.admin_client.table("subscriptions").select("stripe_subscription_id").eq("user_id", user_id).execute()
            
            if not result.data or not result.data[0]["stripe_subscription_id"]:
                raise HTTPException(status_code=404, detail="No active subscription found")
            
            subscription_id = result.data[0]["stripe_subscription_id"]
            
            # Cancel in Stripe
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            # Update in Supabase
            self.admin_client.table("subscriptions").update({
                "cancel_at_period_end": True
            }).eq("user_id", user_id).execute()
            
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")
    
    async def get_subscription_status(self, user_id: str) -> SubscriptionStatus:
        """Get current subscription status for a user"""
        try:
            result = self.admin_client.table("subscriptions").select("*").eq("user_id", user_id).execute()
            
            if not result.data:
                return SubscriptionStatus(
                    plan="free",
                    status="active",
                    post_limit=1,
                    posts_used=0
                )
            
            subscription = result.data[0]
            post_limit = await self.get_monthly_post_limit(user_id)
            posts_used = await self.get_monthly_post_count(user_id)
            
            return SubscriptionStatus(
                plan=subscription["plan"],
                status=subscription["status"],
                post_limit=post_limit,
                posts_used=posts_used
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get subscription status: {str(e)}")

    async def get_monthly_post_limit(self, user_id: str) -> int:
        """Get remaining posts before reaching the limit for a user"""
        try:
            result = self.admin_client.rpc('get_user_post_limit', {'user_uuid': user_id}).execute()
            print("RESULYS", result, "RESSSS")
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get user post limit: {str(e)}")

    async def get_monthly_post_count(self, user_id: str) -> int:
        """Get monthly post count for a user"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            result = self.admin_client.table("monthly_post_counts").select("post_count").eq("user_id", user_id).eq("year_month", current_month).execute()
            return result.data[0]["post_count"] if result.data else 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get user post count: {str(e)}")

    async def update_monthly_post_count(self, user_id: str) -> bool:
        """Update monthly post count for a user"""
        try:
            self.admin_client.rpc('increment_monthly_post_count', {'user_uuid': user_id}).execute()
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update user post count: {str(e)}")


    async def handle_webhook(self, payload: bytes, sig_header: str) -> WebhookResult:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # Store event in database
            self.admin_client.table("subscription_events").insert({
                "stripe_event_id": event.id,
                "event_type": event.type,
                "data": event.data.object
            }).execute()
            
            # Handle specific events
            if event.type == "customer.subscription.updated":
                await self._handle_subscription_updated(event.data.object)
            elif event.type == "customer.subscription.deleted":
                await self._handle_subscription_deleted(event.data.object)
            
            return WebhookResult(
                success=True,
                event_id=event.id,
                event_type=event.type
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Webhook handling failed: {str(e)}")
    
    async def _handle_subscription_updated(self, subscription_data) -> None:
        """Handle subscription update events"""
        try:
            # Update subscription in Supabase
            self.admin_client.table("subscriptions").update({
                "status": subscription_data.status,
                "current_period_start": subscription_data.current_period_start,
                "current_period_end": subscription_data.current_period_end,
                "cancel_at_period_end": subscription_data.cancel_at_period_end
            }).eq("stripe_subscription_id", subscription_data.id).execute()
        except Exception as e:
            print(f"Failed to handle subscription update: {str(e)}")
    
    async def _handle_subscription_deleted(self, subscription_data) -> None:
        """Handle subscription deletion events"""
        try:
            # Update subscription status in Supabase
            self.admin_client.table("subscriptions").update({
                "status": "canceled"
            }).eq("stripe_subscription_id", subscription_data.id).execute()
        except Exception as e:
            print(f"Failed to handle subscription deletion: {str(e)}")

