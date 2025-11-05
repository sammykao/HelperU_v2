import requests
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.sms import (
    OpenPhoneMessageResponse,
    OpenPhoneMessageStatus,
    OpenPhoneServiceHealth,
    TaskCreationNotification,
    ApplicationReceivedNotification,
    ApplicationStatusNotification,
    MessageNotification,
    TaskCompletionNotification,
    PaymentReminderNotification,
    VerificationCodeNotification,
    WelcomeMessageNotification,
    BulkNotificationRequest,
    BulkNotificationResponse,
    InvitationNotification
)

logger = logging.getLogger(__name__)

class SMSUtils:
    """Service for sending SMS notifications"""
    
    def __init__(self):
        self.from_number = settings.OPENPHONE_FROM_NUMBER
        self.api_key = settings.OPENPHONE_API_KEY
        self.base_url = "https://api.openphone.com/v1"
        if not self.from_number:
            raise ValueError("OPENPHONE_FROM_NUMBER is required")
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for OpenPhone API"""
        # Remove any non-digit characters except +
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Ensure it starts with +
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
            
        return cleaned
    
    def _send_sms(self, to_numbers: List[str], content: str, user_id: Optional[str] = None) -> OpenPhoneMessageResponse:
        """Send SMS via OpenPhone API"""
        try:
            # Format phone numbers
            formatted_numbers = [self._format_phone_number(phone) for phone in to_numbers]
            
            # Prepare payload
            payload = {
                "from": self.from_number,
                "to": formatted_numbers,
                "content": content
            }
            
            if user_id:
                payload["userId"] = user_id
            
            # Send request
            response = requests.post(
                f"{self.base_url}/messages",
                headers={
                    "Authorization": self.api_key,  # No "Bearer" prefix
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                result = response.json().get("data")
                logger.info(f"SMS sent successfully to {len(formatted_numbers)} recipients")
                return OpenPhoneMessageResponse(
                    message_id=result.get("id"),
                    recipients=formatted_numbers,
                    content=content
                )
            else:
                logger.error(f"OpenPhone API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send SMS: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenPhone API request failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SMS service unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send SMS: {str(e)}"
            )
    
    async def send_task_creation_notification(
        self, 
        notification: TaskCreationNotification
    ) -> OpenPhoneMessageResponse:
        """Send notification when a new task is created"""
        content = f"""🎯 New Task Created!

Task: {notification.task_title}
Description: {notification.task_description[:100]}{'...' if len(notification.task_description) > 100 else ''}

You'll be notified by text message when helpers apply to your task. You can also search for and invite students to apply to the task on the task dashboard page.

View details in the HelperU app or website."""

        return self._send_sms([notification.client_phone], content)
    
    async def send_application_received_notification(
        self, 
        notification: ApplicationReceivedNotification
    ) -> OpenPhoneMessageResponse:


        """Send notification when a helper applies to a task"""
        content = f"""📝 New Application Received!

Helper: {notification.helper_name}
Task: {notification.task_title}

To view the Helpers contact information, visit the HelperU website, go to my posts page, click on your post, and click the  "Show Contact Details" button."""
        # if notification.task_id:
        #     content += f"\nView it here: https://helperu.com/tasks/browse/{notification.task_id}"


        return self._send_sms([notification.client_phone], content)
    
    

    
    async def send_message_notification(
        self, 
        notification: MessageNotification
    ) -> OpenPhoneMessageResponse:
        """Send notification when a new message is received"""
        content = f"""💬 New Message from {notification.sender_name}

"{notification.message_preview[:50]}{'...' if len(notification.message_preview) > 50 else ''}"

Reply in the HelperU app to continue the conversation."""

        return self._send_sms([notification.recipient_phone], content)
    
    async def send_invitation_notification(
        self, 
        notification: InvitationNotification
    ) -> OpenPhoneMessageResponse:
        """Send notification when a helper is invited to a task"""
        content = f"""📝 New Invitation to apply to a task!

Task: {notification.task_title}
Client: {notification.client_name}

Visit HelperU or open the app to go view the post they invited you to.
        """
        # if notification.task_id:
        #     content += f"\nView it here: https://helperu.com/tasks/browse/{notification.task_id}"
        return self._send_sms([notification.helper_phone], content)
    
    async def send_welcome_message(
        self, 
        notification: WelcomeMessageNotification
    ) -> OpenPhoneMessageResponse:
        """Send welcome message to new users"""
        content = f"""🎉 Welcome to HelperU, {notification.user_name}!

You've successfully created your {notification.user_type} account. 

Get started by:
• Completing your profile
• Browsing available tasks (if you're a helper)
• Creating your first task (if you're a client)

Welcome to the HelperU community! 🚀"""

        return self._send_sms([notification.phone], content)
    
    async def send_bulk_notification(
        self, 
        request: BulkNotificationRequest
    ) -> BulkNotificationResponse:
        """Send bulk SMS notification to multiple recipients"""
        if len(request.phone_numbers) > 100:  # OpenPhone limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send to more than 100 recipients at once"
            )
        
        try:
            # Send SMS to all recipients
            result = self._send_sms(request.phone_numbers, request.content, request.user_id)
            
            return BulkNotificationResponse(
                total_recipients=len(request.phone_numbers),
                successful_sends=len(request.phone_numbers),
                failed_sends=0,
                message_ids=[result.message_id] if result.message_id else [],
                errors=[]
            )
        except Exception as e:
            return BulkNotificationResponse(
                total_recipients=len(request.phone_numbers),
                successful_sends=0,
                failed_sends=len(request.phone_numbers),
                message_ids=[],
                errors=[str(e)]
            )
    