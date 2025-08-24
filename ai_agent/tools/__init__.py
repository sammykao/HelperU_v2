"""
MCP Tools for HelperU Backend Services
Wraps all service functions as MCP-compatible tools
"""

from .base import BaseMCPTool, ToolRegistry, tool_registry
from .auth_tools import AuthTools, register_auth_tools
from .task_tools import TaskTools, register_task_tools
from .chat_tools import ChatTools, register_chat_tools
from .profile_tools import ProfileTools, register_profile_tools
from .application_tools import ApplicationTools, register_application_tools
from .payment_tools import PaymentTools, register_payment_tools
from .notification_tools import NotificationTools, register_notification_tools

__all__ = [
    "BaseMCPTool",
    "ToolRegistry", 
    "tool_registry",
    "AuthTools", 
    "TaskTools",
    "ChatTools",
    "ProfileTools",
    "ApplicationTools",
    "PaymentTools",
    "NotificationTools",
    "register_auth_tools",
    "register_task_tools", 
    "register_chat_tools",
    "register_profile_tools",
    "register_application_tools",
    "register_payment_tools",
    "register_notification_tools"
]
