import requests
import logging
from typing import List, Optional, Union
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.openphone import (
    OpenPhoneMessageResponse,
    OpenPhoneErrorResponse,
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
    BulkNotificationResponse
)

logger = logging.getLogger(__name__)


class OpenPhoneService:
    """Service for sending SMS notifications via OpenPhone API"""
    
    def __init__(self):
        self.api_key = settings.OPENPHONE_API_KEY
        self.from_number = settings.OPENPHONE_FROM_NUMBER
        self.base_url = "https://api.openphone.com/v1"
        
        if not self.api_key:
            raise ValueError("OPENPHONE_API_KEY is required")
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
            
            if response.status_code == 200:
                result = response.json()
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
Task ID: {notification.task_id[:8]}...

You'll be notified when helpers apply to your task.

View details in the HelperU app."""

        return self._send_sms([notification.client_phone], content)
    
    async def send_application_received_notification(
        self, 
        notification: ApplicationReceivedNotification
    ) -> OpenPhoneMessageResponse:
        """Send notification when a helper applies to a task"""
        content = f"""📝 New Application Received!

Helper: {notification.helper_name}
Task: {notification.task_title}
Application ID: {notification.application_id[:8]}...

Review the application in the HelperU app to accept or decline."""

        return self._send_sms([notification.client_phone], content)
    
    async def send_application_status_notification(
        self, 
        notification: ApplicationStatusNotification
    ) -> OpenPhoneMessageResponse:
        """Send notification about application status update"""
        if notification.status == "accepted":
            content = f"""✅ Application Accepted!

Task: {notification.task_title}
Client: {notification.client_name}

Congratulations! Your application has been accepted. The client will contact you soon to discuss details.

View the task in the HelperU app."""
        elif notification.status == "declined":
            content = f"""❌ Application Declined

Task: {notification.task_title}
Client: {notification.client_name}

Unfortunately, your application was not selected for this task. Don't worry - there are many other opportunities available.

Keep applying to tasks that match your skills!"""
        else:
            content = f"""⏳ Application Status Update

Task: {notification.task_title}
Client: {notification.client_name}
Status: {notification.status.title()}

Your application is being reviewed. You'll be notified of the final decision soon."""

        return self._send_sms([notification.helper_phone], content)
    
    async def send_message_notification(
        self, 
        notification: MessageNotification
    ) -> OpenPhoneMessageResponse:
        """Send notification when a new message is received"""
        content = f"""💬 New Message from {notification.sender_name}

"{notification.message_preview[:50]}{'...' if len(notification.message_preview) > 50 else ''}"

Chat ID: {notification.chat_id[:8]}...

Reply in the HelperU app to continue the conversation."""

        return self._send_sms([notification.recipient_phone], content)
    
    async def send_task_completion_notification(
        self, 
        notification: TaskCompletionNotification
    ) -> OpenPhoneMessageResponse:
        """Send notification when a task is marked as completed"""
        content = f"""🎉 Task Completed!

Task: {notification.task_title}
Helper: {notification.helper_name}
Task ID: {notification.task_id[:8]}...

The task has been marked as completed. Please review and provide feedback in the HelperU app.

Thank you for using HelperU!"""

        return self._send_sms([notification.client_phone], content)
    
    async def send_payment_reminder(
        self, 
        notification: PaymentReminderNotification
    ) -> OpenPhoneMessageResponse:
        """Send payment reminder for completed tasks"""
        content = f"""💰 Payment Reminder

Task: {notification.task_title}
Amount: ${notification.amount:.2f}
Due Date: {notification.due_date}

Please complete payment for this completed task in the HelperU app.

Thank you for your prompt payment!"""

        return self._send_sms([notification.client_phone], content)
    
    async def send_verification_code(
        self, 
        notification: VerificationCodeNotification
    ) -> OpenPhoneMessageResponse:
        """Send verification code via SMS"""
        content = f"""🔐 HelperU {notification.purpose.title()} Code

Your verification code is: {notification.code}

This code will expire in 10 minutes. Do not share this code with anyone.

If you didn't request this code, please ignore this message."""

        return self._send_sms([notification.phone], content)
    
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
    
    def get_sms_status(self, message_id: str) -> OpenPhoneMessageStatus:
        """Get status of a sent SMS message"""
        try:
            response = requests.get(
                f"{self.base_url}/messages/{message_id}",
                headers={
                    "Authorization": self.api_key,
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return OpenPhoneMessageStatus(
                    message_id=message_id,
                    status=data.get("status", "unknown"),
                    delivered_at=data.get("delivered_at"),
                    error_message=data.get("error_message"),
                    recipient=data.get("recipient", ""),
                    cost=data.get("cost")
                )
            else:
                logger.error(f"Failed to get SMS status: {response.status_code}")
                return OpenPhoneMessageStatus(
                    message_id=message_id,
                    status="error",
                    error_message="Failed to get message status",
                    recipient=""
                )
                
        except Exception as e:
            logger.error(f"Error getting SMS status: {str(e)}")
            return OpenPhoneMessageStatus(
                message_id=message_id,
                status="error",
                error_message=str(e),
                recipient=""
            )
    
    def check_health(self) -> OpenPhoneServiceHealth:
        """Check the health status of the OpenPhone service"""
        try:
            # Check if required configuration is present
            api_key_configured = bool(self.api_key)
            from_number_configured = bool(self.from_number)
            
            if not api_key_configured or not from_number_configured:
                return OpenPhoneServiceHealth(
                    status="unhealthy",
                    api_key_configured=api_key_configured,
                    from_number_configured=from_number_configured,
                    error_message="Missing required configuration"
                )
            
            # Try to make a simple API call to verify connectivity
            response = requests.get(
                f"{self.base_url}/health",
                headers={
                    "Authorization": self.api_key,
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return OpenPhoneServiceHealth(
                    status="healthy",
                    api_key_configured=api_key_configured,
                    from_number_configured=from_number_configured
                )
            else:
                return OpenPhoneServiceHealth(
                    status="unhealthy",
                    api_key_configured=api_key_configured,
                    from_number_configured=from_number_configured,
                    error_message=f"API health check failed: {response.status_code}"
                )
                
        except Exception as e:
            return OpenPhoneServiceHealth(
                status="unhealthy",
                api_key_configured=bool(self.api_key),
                from_number_configured=bool(self.from_number),
                error_message=str(e)
            )
