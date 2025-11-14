import stripe
import json
from app.core.config import settings
from supabase import Client
from fastapi import HTTPException
from datetime import datetime
from typing import Optional
from app.schemas.subscription import (
    SubscriptionStatus,
    CreateSubscriptionResponse,
    WebhookResult
)
from app.schemas.task import TaskCreate

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    def __init__(self, admin_client: Client):
        self.admin_client = admin_client

    def _convert_timestamp_to_iso(self, timestamp) -> str:
        """Convert Unix timestamp to ISO format string"""
        try:
            if timestamp is None:
                return None
            return datetime.fromtimestamp(timestamp).isoformat()
        except (ValueError, TypeError, OSError) as e:
            print(f"Failed to convert timestamp {timestamp}: {str(e)}")
            return None
    
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
    
    async def create_checkout_session(self, user_id: str, price_id: str = None) -> str:
        """Create a Stripe Checkout session for subscription"""
        try:
            # Get user's Stripe customer ID
            result = self.admin_client.table("subscriptions").select("stripe_customer_id").eq("user_id", user_id).execute()
            
            if not result.data:
                # This should not happen as the endpoint creates the customer first
                raise HTTPException(status_code=500, detail="Customer not found - please try again")
            
            customer_id = result.data[0]["stripe_customer_id"]
            
            # Use provided price_id or default to premium price
            subscription_price_id = price_id or settings.STRIPE_PREMIUM_PRICE_ID
            
            # Create Stripe Checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': subscription_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f'{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{settings.FRONTEND_URL}/subscription/upgrade',
                metadata={
                    'user_id': user_id,
                }
            )
            
            return checkout_session.url
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")
    
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

            if not subscription:
                raise HTTPException(status_code=400, detail="Failed to create subscription in stripe")
            print(subscription)
            
            # Update subscription in Supabase
            # Convert Unix timestamps to ISO format for PostgreSQL
            period_start_iso = self._convert_timestamp_to_iso(subscription.current_period_start)
            period_end_iso = self._convert_timestamp_to_iso(subscription.current_period_end)
            
            self.admin_client.table("subscriptions").upsert({
                "user_id": user_id,
                "stripe_subscription_id": subscription.id,
                "stripe_customer_id": customer_id,
                "plan": "premium",
                "status": subscription.status,
                "current_period_start": period_start_iso,
                "current_period_end": period_end_iso
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
    
    async def create_portal_session(self, user_id: str) -> str:
        """Create a Stripe customer portal session for subscription management"""
        try:
            # Get user's Stripe customer ID
            result = self.admin_client.table("subscriptions").select("stripe_customer_id").eq("user_id", user_id).execute()
            
            if not result.data or not result.data[0]["stripe_customer_id"]:
                raise HTTPException(status_code=404, detail="No Stripe customer found")
            
            customer_id = result.data[0]["stripe_customer_id"]
            
            # Create portal session
            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f'{settings.FRONTEND_URL}/subscription/upgrade',
            )
            
            return portal_session.url
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create portal session: {str(e)}")
    
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
            client_post_count = await self.get_client_post_count(user_id)
            client_posts_remaining = await self.get_client_posts_remaining(user_id)
            result = self.admin_client.table("subscriptions").select("*").eq("user_id", user_id).execute()
            if not result.data:
                return SubscriptionStatus(
                    plan="free",
                    status="active",
                    post_limit=client_posts_remaining,
                    posts_used=client_post_count
                )
            
            subscription = result.data[0]
            
            return SubscriptionStatus(
                plan=subscription["plan"],
                status=subscription["status"],
                post_limit=client_posts_remaining,
                posts_used=client_post_count
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get subscription status: {str(e)}")


    async def get_client_post_count(self, user_id: str) -> int:
        """Get client post count for a user"""
        try:
            result = self.admin_client.table("clients").select("number_of_posts").eq("id", user_id).execute()
            return result.data[0]["number_of_posts"] if result.data else 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get client post count: {str(e)}")

    async def get_client_posts_remaining(self, user_id: str) -> int:
        """Get client posts remaining for a user"""
        try:
            client_post_count = await self.get_client_post_count(user_id)
            plan = self.admin_client.table("subscriptions").select("plan").eq("user_id", user_id).execute()
            if plan.data and plan.data[0]["plan"] == "premium":
                return -1 # Unlimited posts for premium users
            return 1 - client_post_count
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get client posts remaining: {str(e)}")

    async def user_exists_in_subscriptions(self, user_id: str) -> bool:
        """Check if user exists in subscriptions table"""
        try:
            result = self.admin_client.table("subscriptions").select("user_id").eq("user_id", user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to check user subscription: {str(e)}")


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

            
            if event.data.object.mode == "payment":
                return WebhookResult(
                    action="payment",
                    success=True,
                    event_id=event.id,
                    event_type=event.type
                )
            elif event.type == "checkout.session.completed":
                await self._handle_checkout_completed(event.data.object)
            elif event.type == "customer.subscription.created":
                await self._handle_subscription_created(event.data.object)
            elif event.type == "customer.subscription.updated" and event.data.object.cancel_at_period_end:
                await self._handle_subscription_deleted(event.data.object)
            elif event.type == "customer.subscription.updated":
                await self._handle_subscription_updated(event.data.object)
            elif event.type == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(event.data.object)
            elif event.type == "invoice.payment_failed":
                await self._handle_payment_failed(event.data.object)

            return WebhookResult(
                action="subscription",
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
            # Convert Unix timestamps to ISO format for PostgreSQL
            period_start_iso = self._convert_timestamp_to_iso(subscription_data.current_period_start)
            period_end_iso = self._convert_timestamp_to_iso(subscription_data.current_period_end)
            
            # Update subscription in Supabase
            self.admin_client.table("subscriptions").update({
                "status": subscription_data.status,
                "current_period_start": period_start_iso,
                "current_period_end": period_end_iso,
                "cancel_at_period_end": subscription_data.cancel_at_period_end
            }).eq("stripe_subscription_id", subscription_data.id).execute()
        except Exception as e:
            print(f"Failed to handle subscription update: {str(e)}")
    
    async def _handle_subscription_deleted(self, subscription_data) -> None:
        """Handle subscription deletion events"""
        try:
            # Update subscription status in Supabase
            self.admin_client.table("subscriptions").update({
                "plan": "free"
            }).eq("stripe_subscription_id", subscription_data.id).execute()
        except Exception as e:
            print(f"Failed to handle subscription deletion: {str(e)}")
    
    async def _handle_checkout_completed(self, session_data) -> None:
        """Handle checkout session completion"""
        try:
            # Get user_id from metadata
            user_id = session_data.metadata.get('user_id')
            if not user_id or session_data.mode == 'payment':
                print("No user_id in checkout session metadata or payment mode is one time")
                return
            # Get subscription from session
            subscription_id = session_data.subscription
            if not subscription_id:
                print("No subscription in checkout session")
                return
            
            # Retrieve subscription details from Stripe
            subscription = stripe.Subscription.retrieve(subscription_id)
            period_start_iso = self._convert_timestamp_to_iso(subscription.current_period_start)
            period_end_iso = self._convert_timestamp_to_iso(subscription.current_period_end)
            
            self.admin_client.table("subscriptions").update({
                "stripe_subscription_id": subscription.id,
                "plan": "premium",
                "status": 'active',
                "current_period_start": period_start_iso,
                "current_period_end": period_end_iso,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }).eq("user_id", user_id).execute()
            
            print(f"Checkout completed for user {user_id}, subscription {subscription.id}")
        except Exception as e:
            print(f"Failed to handle checkout completion: {str(e)}")
    
    async def _handle_subscription_created(self, subscription_data) -> None:
        """Handle subscription creation events"""
        try:
            # Get customer ID to find user
            customer_id = subscription_data.customer
            
            # Find user by customer ID
            result = self.admin_client.table("subscriptions").select("user_id").eq("stripe_customer_id", customer_id).execute()
            if not result.data:
                print(f"No user found for customer {customer_id}")
                return
            
            user_id = result.data[0]["user_id"]
            
            # Update subscription in database
            period_start_iso = self._convert_timestamp_to_iso(subscription_data.current_period_start)
            period_end_iso = self._convert_timestamp_to_iso(subscription_data.current_period_end)
            
            self.admin_client.table("subscriptions").update({
                "stripe_subscription_id": subscription_data.id,
                "plan": "premium",
                "status": "active",
                "current_period_start": period_start_iso,
                "current_period_end": period_end_iso,
                "cancel_at_period_end": subscription_data.cancel_at_period_end
            }).eq("user_id", user_id).execute()
            
            print(f"Subscription created for user {user_id}, subscription {subscription_data.id}")
        except Exception as e:
            print(f"Failed to handle subscription creation: {str(e)}")
    
    async def _handle_payment_succeeded(self, invoice_data) -> None:
        """Handle successful payment events"""
        try:
            subscription_id = invoice_data.subscription
            if not subscription_id:
                return
            
            # Update subscription status to active
            self.admin_client.table("subscriptions").update({
                "status": "active"
            }).eq("stripe_subscription_id", subscription_id).execute()
            
            print(f"Payment succeeded for subscription {subscription_id}")
        except Exception as e:
            print(f"Failed to handle payment success: {str(e)}")
    
    async def _handle_payment_failed(self, invoice_data) -> None:
        """Handle failed payment events"""
        try:
            subscription_id = invoice_data.subscription
            if not subscription_id:
                return
            
            # Update subscription status to past_due
            self.admin_client.table("subscriptions").update({
                "status": "past_due"
            }).eq("stripe_subscription_id", subscription_id).execute()
            
            print(f"Payment failed for subscription {subscription_id}")
        except Exception as e:
            print(f"Failed to handle payment failure: {str(e)}")

    async def create_onetime_payment_session(self, user_id: str, price_id: str = None, task_data: Optional[TaskCreate] = None) -> str:
        """Create a Stripe Checkout session for a one-time payment"""
        try:
            if not task_data:
                raise HTTPException(status_code=400, detail="Task data is required")
            # Get user's Stripe customer ID
            result = self.admin_client.table("subscriptions").select("stripe_customer_id").eq("user_id", user_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="User not found in subscriptions table")
            
            customer_id = result.data[0]["stripe_customer_id"]
            
            # Use provided price_id or default to premium price
            subscription_price_id = price_id or settings.STRIPE_ONE_TIME_POST_PRICE_ID

            # Create Stripe Checkout session
            # Convert task_data to JSON string for Stripe metadata (metadata values must be strings)
            task_data_json = json.dumps(task_data.model_dump(), default=str)
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': subscription_price_id,
                    'quantity': 1,
                }],
                success_url=f'{settings.FRONTEND_URL}/onetime-payment/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{settings.FRONTEND_URL}/onetime-payment/cancel',
                mode='payment',
                metadata={
                    'user_id': user_id,
                    'task_data': task_data_json
                }
            )

            return checkout_session.url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create one-time payment session: {str(e)}")

   