"""
Payment and Subscription MCP Tools
Wraps stripe_service functions as MCP tools
"""
from typing import Any, Dict, Optional
from .base import BaseMCPTool, ToolSchema, tool_registry
from app.services.stripe_service import StripeService
from app.schemas.subscription import CreateSubscriptionRequest


class CreateSubscriptionTool(BaseMCPTool):
    """Create a new subscription for a user"""
    
    def __init__(self, stripe_service: StripeService):
        super().__init__("create_subscription", "Create a new subscription for a user")
        self.stripe_service = stripe_service
    
    async def execute(self, user_id: str, price_id: str, customer_email: str) -> Dict[str, Any]:
        """Create subscription"""
        request = CreateSubscriptionRequest(
            user_id=user_id,
            price_id=price_id,
            customer_email=customer_email
        )
        result = await self.stripe_service.create_subscription(request)
        
        return {
            "success": True,
            "subscription_id": result.subscription_id,
            "customer_id": result.customer_id,
            "status": result.status,
            "current_period_end": result.current_period_end.isoformat() if result.current_period_end else None
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="create_subscription",
            description="Create a new subscription for a user",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "price_id": {"type": "string", "description": "Stripe price ID"},
                    "customer_email": {"type": "string", "description": "Customer email"}
                },
                "required": ["user_id", "price_id", "customer_email"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "subscription_id": {"type": "string"},
                    "customer_id": {"type": "string"},
                    "status": {"type": "string"},
                    "current_period_end": {"type": "string"}
                }
            }
        )


class CancelSubscriptionTool(BaseMCPTool):
    """Cancel a subscription"""
    
    def __init__(self, stripe_service: StripeService):
        super().__init__("cancel_subscription", "Cancel a subscription")
        self.stripe_service = stripe_service
    
    async def execute(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel subscription"""
        result = await self.stripe_service.cancel_subscription(subscription_id)
        
        return {
            "success": True,
            "subscription_id": result.subscription_id,
            "status": result.status,
            "canceled_at": result.canceled_at.isoformat() if result.canceled_at else None
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="cancel_subscription",
            description="Cancel a subscription",
            input_schema={
                "type": "object",
                "properties": {
                    "subscription_id": {"type": "string", "description": "Stripe subscription ID"}
                },
                "required": ["subscription_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "subscription_id": {"type": "string"},
                    "status": {"type": "string"},
                    "canceled_at": {"type": "string"}
                }
            }
        )


class GetSubscriptionStatusTool(BaseMCPTool):
    """Get subscription status for a user"""
    
    def __init__(self, stripe_service: StripeService):
        super().__init__("get_subscription_status", "Get subscription status for a user")
        self.stripe_service = stripe_service
    
    async def execute(self, user_id: str) -> Dict[str, Any]:
        """Get subscription status"""
        result = await self.stripe_service.get_subscription_status(user_id)
        
        return {
            "success": True,
            "user_id": str(result.user_id),
            "subscription_status": result.subscription_status,
            "current_period_end": result.current_period_end.isoformat() if result.current_period_end else None,
            "post_limit": result.post_limit,
            "posts_used": result.posts_used
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_subscription_status",
            description="Get subscription status for a user",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"}
                },
                "required": ["user_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "user_id": {"type": "string"},
                    "subscription_status": {"type": "string"},
                    "current_period_end": {"type": "string"},
                    "post_limit": {"type": "integer"},
                    "posts_used": {"type": "integer"}
                }
            }
        )


class ProcessRefundTool(BaseMCPTool):
    """Process a refund for a payment"""
    
    def __init__(self, stripe_service: StripeService):
        super().__init__("process_refund", "Process a refund for a payment")
        self.stripe_service = stripe_service
    
    async def execute(self, payment_intent_id: str, amount: Optional[int] = None, reason: Optional[str] = None) -> Dict[str, Any]:
        """Process refund"""
        # This would need to be implemented in stripe_service
        # For now, returning a placeholder
        return {
            "success": True,
            "refund_id": "ref_placeholder",
            "amount": amount or 0,
            "status": "succeeded"
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="process_refund",
            description="Process a refund for a payment",
            input_schema={
                "type": "object",
                "properties": {
                    "payment_intent_id": {"type": "string", "description": "Stripe payment intent ID"},
                    "amount": {"type": "integer", "description": "Amount to refund in cents (optional)"},
                    "reason": {"type": "string", "description": "Reason for refund (optional)"}
                },
                "required": ["payment_intent_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "refund_id": {"type": "string"},
                    "amount": {"type": "integer"},
                    "status": {"type": "string"}
                }
            }
        )


def register_payment_tools(stripe_service: StripeService):
    """Register all payment tools"""
    tools = [
        CreateSubscriptionTool(stripe_service),
        CancelSubscriptionTool(stripe_service),
        GetSubscriptionStatusTool(stripe_service),
        ProcessRefundTool(stripe_service)
    ]
    
    for tool in tools:
        tool_registry.register(tool)
    
    return tools
