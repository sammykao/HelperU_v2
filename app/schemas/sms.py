from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class OpenPhoneMessageRequest(BaseModel):
    """Request model for sending SMS via OpenPhone"""
    from_number: str = Field(..., description="Sender phone number")
    to_numbers: List[str] = Field(..., description="Recipient phone numbers")
    content: str = Field(..., description="Message content")
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking")


class OpenPhoneMessageResponse(BaseModel):
    """Response model for successful SMS sending"""
    success: bool = Field(True, description="Whether the SMS was sent successfully")
    message_id: str = Field(..., description="OpenPhone message ID")
    recipients: List[str] = Field(..., description="Formatted recipient phone numbers")
    content: str = Field(..., description="Message content that was sent")
    sent_at: datetime = Field(default_factory=datetime.utcnow, description="When the SMS was sent")


class OpenPhoneErrorResponse(BaseModel):
    """Response model for SMS sending errors"""
    success: bool = Field(False, description="Whether the SMS was sent successfully")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="OpenPhone error code if available")
    recipients: Optional[List[str]] = Field(None, description="Recipient phone numbers that failed")
    content: Optional[str] = Field(None, description="Message content that failed to send")


class OpenPhoneMessageStatus(BaseModel):
    """Model for SMS message status"""
    message_id: str = Field(..., description="OpenPhone message ID")
    status: str = Field(..., description="Message status (delivered, failed, pending, etc.)")
    delivered_at: Optional[datetime] = Field(None, description="When the message was delivered")
    error_message: Optional[str] = Field(None, description="Error message if delivery failed")
    recipient: str = Field(..., description="Recipient phone number")
    cost: Optional[float] = Field(None, description="Cost of the message")


class TaskCreationNotification(BaseModel):
    """Model for task creation SMS notification"""
    client_phone: str = Field(..., description="Client's phone number")
    task_title: str = Field(..., description="Title of the created task")
    task_description: str = Field(..., description="Description of the task")
    task_id: str = Field(..., description="Task ID")


class ApplicationReceivedNotification(BaseModel):
    """Model for application received SMS notification"""
    client_phone: str = Field(..., description="Client's phone number")
    helper_name: str = Field(..., description="Name of the helper who applied")
    task_title: str = Field(..., description="Title of the task")
    task_id: Optional[str] = Field(None, description="Task ID")


class ApplicationStatusNotification(BaseModel):
    """Model for application status update SMS notification"""
    helper_phone: str = Field(..., description="Helper's phone number")
    task_title: str = Field(..., description="Title of the task")
    status: str = Field(..., description="Application status (accepted, declined, pending)")
    client_name: str = Field(..., description="Name of the client")


class MessageNotification(BaseModel):
    """Model for new message SMS notification"""
    recipient_phone: str = Field(..., description="Recipient's phone number")
    sender_name: str = Field(..., description="Name of the message sender")
    chat_id: str = Field(..., description="Chat ID")
    message_preview: str = Field(..., description="Preview of the message content")


class TaskCompletionNotification(BaseModel):
    """Model for task completion SMS notification"""
    client_phone: str = Field(..., description="Client's phone number")
    helper_name: str = Field(..., description="Name of the helper who completed the task")
    task_title: str = Field(..., description="Title of the completed task")
    task_id: str = Field(..., description="Task ID")


class PaymentReminderNotification(BaseModel):
    """Model for payment reminder SMS notification"""
    client_phone: str = Field(..., description="Client's phone number")
    task_title: str = Field(..., description="Title of the task")
    amount: float = Field(..., description="Payment amount")
    due_date: str = Field(..., description="Payment due date")


class VerificationCodeNotification(BaseModel):
    """Model for verification code SMS notification"""
    phone: str = Field(..., description="Phone number to send code to")
    code: str = Field(..., description="Verification code")
    purpose: str = Field(default="verification", description="Purpose of the verification")


class WelcomeMessageNotification(BaseModel):
    """Model for welcome message SMS notification"""
    phone: str = Field(..., description="Phone number to send welcome message to")
    user_name: str = Field(..., description="Name of the new user")
    user_type: str = Field(..., description="Type of user (client or helper)")


class BulkNotificationRequest(BaseModel):
    """Model for bulk SMS notification request"""
    phone_numbers: List[str] = Field(..., description="List of phone numbers to notify")
    content: str = Field(..., description="Message content to send")
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking")


class BulkNotificationResponse(BaseModel):
    """Model for bulk SMS notification response"""
    success: bool = Field(..., description="Whether the bulk SMS was sent successfully")
    total_recipients: int = Field(..., description="Total number of recipients")
    successful_sends: int = Field(..., description="Number of successful sends")
    failed_sends: int = Field(..., description="Number of failed sends")
    message_ids: List[str] = Field(..., description="List of message IDs for successful sends")
    errors: List[str] = Field(default_factory=list, description="List of error messages for failed sends")


class OpenPhoneServiceHealth(BaseModel):
    """Model for OpenPhone service health check"""
    status: str = Field(..., description="Service status (healthy, unhealthy)")
    api_key_configured: bool = Field(..., description="Whether API key is configured")
    from_number_configured: bool = Field(..., description="Whether from number is configured")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="When the health check was performed")
    error_message: Optional[str] = Field(None, description="Error message if service is unhealthy")

class InvitationNotification(BaseModel):
    """Model for invitation SMS notification"""
    helper_phone: str = Field(..., description="Helper's phone number")
    client_name: str = Field(..., description="Name of the client")
    task_title: str = Field(..., description="Title of the task")
    task_id: Optional[str] = Field(None, description="Task ID")
    pay: Optional[float] = Field(None, description="Pay per hour")

# Union type for all notification models
NotificationRequest = (
    TaskCreationNotification |
    ApplicationReceivedNotification |
    ApplicationStatusNotification |
    MessageNotification |
    TaskCompletionNotification |
    PaymentReminderNotification |
    VerificationCodeNotification |
    WelcomeMessageNotification |
    InvitationNotification
)
