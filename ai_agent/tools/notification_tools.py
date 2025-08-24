"""
Notification Management MCP Tools
Wraps openphone_service functions as MCP tools
"""
from typing import Any, Dict, Optional, List
from .base import BaseMCPTool, ToolSchema, tool_registry
from app.services.openphone_service import OpenPhoneService
from app.schemas.openphone import (
    MessageNotification, TaskCreationNotification, 
    ApplicationReceivedNotification, BulkNotificationRequest
)


class SendSMSTool(BaseMCPTool):
    """Send SMS notification"""
    
    def __init__(self, openphone_service: OpenPhoneService):
        super().__init__("send_sms", "Send SMS notification")
        self.openphone_service = openphone_service
    
    async def execute(self, recipient_phone: str, message: str) -> Dict[str, Any]:
        """Send SMS"""
        # This would need to be implemented in openphone_service
        # For now, returning a placeholder
        return {
            "success": True,
            "message_id": "msg_placeholder",
            "status": "sent",
            "recipient": recipient_phone
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="send_sms",
            description="Send SMS notification",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient_phone": {"type": "string", "description": "Recipient phone number"},
                    "message": {"type": "string", "description": "Message content"}
                },
                "required": ["recipient_phone", "message"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message_id": {"type": "string"},
                    "status": {"type": "string"},
                    "recipient": {"type": "string"}
                }
            }
        )


class SendTaskCreationNotificationTool(BaseMCPTool):
    """Send task creation notification"""
    
    def __init__(self, openphone_service: OpenPhoneService):
        super().__init__("send_task_creation_notification", "Send task creation notification")
        self.openphone_service = openphone_service
    
    async def execute(self, recipient_phone: str, task_title: str, client_name: str, 
                     hourly_rate: float, location: str) -> Dict[str, Any]:
        """Send task creation notification"""
        notification = TaskCreationNotification(
            recipient_phone=recipient_phone,
            task_title=task_title,
            client_name=client_name,
            hourly_rate=hourly_rate,
            location=location
        )
        
        result = await self.openphone_service.send_task_creation_notification(notification)
        
        return {
            "success": True,
            "notification_id": "notif_placeholder",
            "status": "sent",
            "type": "task_creation"
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="send_task_creation_notification",
            description="Send task creation notification",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient_phone": {"type": "string", "description": "Recipient phone number"},
                    "task_title": {"type": "string", "description": "Task title"},
                    "client_name": {"type": "string", "description": "Client name"},
                    "hourly_rate": {"type": "number", "description": "Hourly rate"},
                    "location": {"type": "string", "description": "Task location"}
                },
                "required": ["recipient_phone", "task_title", "client_name", "hourly_rate", "location"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "notification_id": {"type": "string"},
                    "status": {"type": "string"},
                    "type": {"type": "string"}
                }
            }
        )


class SendApplicationNotificationTool(BaseMCPTool):
    """Send application received notification"""
    
    def __init__(self, openphone_service: OpenPhoneService):
        super().__init__("send_application_notification", "Send application received notification")
        self.openphone_service = openphone_service
    
    async def execute(self, recipient_phone: str, helper_name: str, task_title: str) -> Dict[str, Any]:
        """Send application notification"""
        notification = ApplicationReceivedNotification(
            recipient_phone=recipient_phone,
            helper_name=helper_name,
            task_title=task_title
        )
        
        result = await self.openphone_service.send_application_received_notification(notification)
        
        return {
            "success": True,
            "notification_id": "notif_placeholder",
            "status": "sent",
            "type": "application_received"
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="send_application_notification",
            description="Send application received notification",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient_phone": {"type": "string", "description": "Recipient phone number"},
                    "helper_name": {"type": "string", "description": "Helper name"},
                    "task_title": {"type": "string", "description": "Task title"}
                },
                "required": ["recipient_phone", "helper_name", "task_title"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "notification_id": {"type": "string"},
                    "status": {"type": "string"},
                    "type": {"type": "string"}
                }
            }
        )


class SendBulkNotificationTool(BaseMCPTool):
    """Send bulk notifications"""
    
    def __init__(self, openphone_service: OpenPhoneService):
        super().__init__("send_bulk_notification", "Send bulk notifications to multiple recipients")
        self.openphone_service = openphone_service
    
    async def execute(self, recipient_phones: List[str], message: str, 
                     notification_type: str = "general") -> Dict[str, Any]:
        """Send bulk notifications"""
        request = BulkNotificationRequest(
            recipient_phones=recipient_phones,
            message=message,
            notification_type=notification_type
        )
        
        result = await self.openphone_service.send_bulk_notifications(request)
        
        return {
            "success": True,
            "total_sent": result.total_sent,
            "total_failed": result.total_failed,
            "failed_phones": result.failed_phones
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="send_bulk_notification",
            description="Send bulk notifications to multiple recipients",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient_phones": {"type": "array", "items": {"type": "string"}, "description": "List of recipient phone numbers"},
                    "message": {"type": "string", "description": "Message content"},
                    "notification_type": {"type": "string", "description": "Type of notification", "default": "general"}
                },
                "required": ["recipient_phones", "message"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "total_sent": {"type": "integer"},
                    "total_failed": {"type": "integer"},
                    "failed_phones": {"type": "array", "items": {"type": "string"}}
                }
            }
        )


def register_notification_tools(openphone_service: OpenPhoneService):
    """Register all notification tools"""
    tools = [
        SendSMSTool(openphone_service),
        SendTaskCreationNotificationTool(openphone_service),
        SendApplicationNotificationTool(openphone_service),
        SendBulkNotificationTool(openphone_service)
    ]
    
    for tool in tools:
        tool_registry.register(tool)
    
    return tools
