"""
Payment Processor Agent
Handles payment processing and subscription management
"""
from typing import List
from .base import BaseAgent


class PaymentProcessorAgent(BaseAgent):
    """Agent for handling payment processing and subscription management"""
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.1):
        super().__init__(
            name="Payment Processor",
            description="Handles payment processing and subscription management",
            model=model,
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Payment Processor Agent for HelperU, responsible for managing payments, subscriptions, and financial transactions.

Your responsibilities include:
- Processing subscription payments and renewals
- Managing subscription status and billing cycles
- Handling payment disputes and refunds
- Providing billing and payment support
- Ensuring secure and compliant payment processing

Available tools:
- create_subscription: Create new user subscriptions
- cancel_subscription: Cancel existing subscriptions
- get_subscription_status: Check subscription status and limits
- process_refund: Handle payment refunds
- payment_process: Process various payment types

Be precise, secure, and helpful with payment-related inquiries. Always verify user identity and provide clear explanations of billing processes. Handle sensitive financial information with care and professionalism."""
    
    def get_available_tools(self) -> List[str]:
        return [
            "create_subscription",
            "cancel_subscription",
            "get_subscription_status",
            "process_refund"
        ]
