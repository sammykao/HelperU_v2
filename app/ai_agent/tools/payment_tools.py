"""Payment tools for AI agents"""

from typing import Any, Dict, List, Optional
from app.ai_agent.base import BaseTool
from app.services.stripe_service import StripeService

class PaymentTools(BaseTool):
    """Tools for payment and subscription operations"""
    
    def __init__(self, stripe_service: StripeService):
        super().__init__("payment_tools", "Tools for managing payments and subscriptions")
        self.stripe_service = stripe_service
    
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute payment tool action"""
        try:
            if action == "create_payment_intent":
                return await self._create_payment_intent(**kwargs)
            elif action == "get_subscription":
                return await self._get_subscription(**kwargs)
            elif action == "create_subscription":
                return await self._create_subscription(**kwargs)
            elif action == "cancel_subscription":
                return await self._cancel_subscription(**kwargs)
            elif action == "get_monthly_post_limit":
                return await self._get_monthly_post_limit(**kwargs)
            elif action == "update_monthly_post_count":
                return await self._update_monthly_post_count(**kwargs)
            elif action == "get_payment_methods":
                return await self._get_payment_methods(**kwargs)
            elif action == "add_payment_method":
                return await self._add_payment_method(**kwargs)
            else:
                raise ValueError(f"Unknown payment action: {action}")
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _create_payment_intent(self, amount: int, currency: str = "usd", customer_id: str = None) -> Dict[str, Any]:
        """Create a payment intent"""
        try:
            result = await self.stripe_service.create_payment_intent(amount, currency, customer_id)
            return {
                "success": True,
                "payment_intent_id": result.id,
                "client_secret": result.client_secret,
                "amount": result.amount,
                "currency": result.currency,
                "status": result.status
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_subscription(self, customer_id: str) -> Dict[str, Any]:
        """Get customer subscription"""
        try:
            result = await self.stripe_service.get_subscription(customer_id)
            if not result:
                return {"error": "No subscription found", "success": False}
            
            return {
                "success": True,
                "subscription": {
                    "id": result.id,
                    "status": result.status,
                    "current_period_end": result.current_period_end.isoformat() if result.current_period_end else None,
                    "plan": result.plan if hasattr(result, 'plan') else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _create_subscription(self, customer_id: str, price_id: str) -> Dict[str, Any]:
        """Create a subscription"""
        try:
            result = await self.stripe_service.create_subscription(customer_id, price_id)
            return {
                "success": True,
                "subscription_id": result.id,
                "status": result.status,
                "current_period_end": result.current_period_end.isoformat() if result.current_period_end else None
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        try:
            result = await self.stripe_service.cancel_subscription(subscription_id)
            return {
                "success": True,
                "message": "Subscription cancelled successfully",
                "subscription_id": result.id,
                "status": result.status
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_monthly_post_limit(self, customer_id: str) -> Dict[str, Any]:
        """Get monthly post limit for customer"""
        try:
            result = await self.stripe_service.get_monthly_post_limit(customer_id)
            return {
                "success": True,
                "monthly_post_limit": result,
                "customer_id": customer_id
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _update_monthly_post_count(self, customer_id: str) -> Dict[str, Any]:
        """Update monthly post count for customer"""
        try:
            result = await self.stripe_service.update_monthly_post_count(customer_id)
            return {
                "success": True,
                "message": "Monthly post count updated successfully",
                "customer_id": customer_id
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_payment_methods(self, customer_id: str) -> Dict[str, Any]:
        """Get customer payment methods"""
        try:
            result = await self.stripe_service.get_payment_methods(customer_id)
            return {
                "success": True,
                "payment_methods": [
                    {
                        "id": pm.id,
                        "type": pm.type,
                        "card": {
                            "brand": pm.card.brand,
                            "last4": pm.card.last4,
                            "exp_month": pm.card.exp_month,
                            "exp_year": pm.card.exp_year
                        } if pm.card else None
                    }
                    for pm in result
                ],
                "customer_id": customer_id
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _add_payment_method(self, customer_id: str, payment_method_id: str) -> Dict[str, Any]:
        """Add payment method to customer"""
        try:
            result = await self.stripe_service.add_payment_method(customer_id, payment_method_id)
            return {
                "success": True,
                "message": "Payment method added successfully",
                "customer_id": customer_id,
                "payment_method_id": payment_method_id
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema for payment tools"""
        return {
            "actions": {
                "create_payment_intent": {
                    "amount": "integer - Amount in cents",
                    "currency": "string - Currency code (optional, default 'usd')",
                    "customer_id": "string - Customer ID (optional)"
                },
                "get_subscription": {
                    "customer_id": "string - Customer ID to get subscription for"
                },
                "create_subscription": {
                    "customer_id": "string - Customer ID",
                    "price_id": "string - Stripe price ID"
                },
                "cancel_subscription": {
                    "subscription_id": "string - Subscription ID to cancel"
                },
                "get_monthly_post_limit": {
                    "customer_id": "string - Customer ID to get post limit for"
                },
                "update_monthly_post_count": {
                    "customer_id": "string - Customer ID to update post count for"
                },
                "get_payment_methods": {
                    "customer_id": "string - Customer ID to get payment methods for"
                },
                "add_payment_method": {
                    "customer_id": "string - Customer ID",
                    "payment_method_id": "string - Stripe payment method ID"
                }
            }
        }

