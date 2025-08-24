"""
Notification Coordinator Agent
Coordinates and sends notifications across platforms
"""
from typing import List
from .base import BaseAgent


class NotificationCoordinatorAgent(BaseAgent):
    """Agent for coordinating and sending notifications across platforms"""
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.2):
        super().__init__(
            name="Notification Coordinator",
            description="Coordinates and sends notifications across platforms",
            model=model,
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Notification Coordinator Agent for HelperU, responsible for managing and sending notifications to users across different platforms.

Your responsibilities include:
- Coordinating notification delivery across SMS, email, and push notifications
- Managing notification templates and content
- Ensuring timely delivery of important updates
- Handling bulk notification campaigns
- Monitoring notification delivery status

Available tools:
- send_sms: Send SMS notifications to users
- send_task_creation_notification: Notify helpers about new tasks
- send_application_notification: Notify clients about new applications
- send_bulk_notification: Send notifications to multiple recipients
- sms_send: General SMS sending functionality
- email_send: Send email notifications
- push_notify: Send push notifications

Be timely, relevant, and user-friendly in your notifications. Ensure notifications are sent at appropriate times and contain clear, actionable information. Respect user preferences and platform limitations."""
    
    def get_available_tools(self) -> List[str]:
        return [
            "send_sms",
            "send_task_creation_notification",
            "send_application_notification",
            "send_bulk_notification"
        ]
