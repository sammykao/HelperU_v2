"""
Authentication MCP Tools
Wraps auth_service functions as MCP tools
"""
from typing import Any, Dict, Optional
from uuid import UUID
from .base import BaseMCPTool, ToolSchema, tool_registry
from app.services.auth_service import AuthService
from app.schemas.auth import (
    PhoneOTPRequest, PhoneOTPVerifyRequest, ClientSignupRequest, 
    HelperSignupRequest, ClientProfileUpdateRequest, HelperProfileUpdateRequest
)


class SendOTPTool(BaseMCPTool):
    """Send OTP to phone number"""
    
    def __init__(self, auth_service: AuthService):
        super().__init__("send_otp", "Send OTP verification code to phone number")
        self.auth_service = auth_service
    
    async def execute(self, phone: str) -> Dict[str, Any]:
        """Send OTP to phone number"""
        request = PhoneOTPRequest(phone=phone)
        result = await self.auth_service.send_phone_otp(request)
        return {"success": True, "message": "OTP sent successfully"}
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="send_otp",
            description="Send OTP verification code to phone number",
            input_schema={
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Phone number to send OTP to"}
                },
                "required": ["phone"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"}
                }
            }
        )


class VerifyOTPTool(BaseMCPTool):
    """Verify OTP code"""
    
    def __init__(self, auth_service: AuthService):
        super().__init__("verify_otp", "Verify OTP code and authenticate user")
        self.auth_service = auth_service
    
    async def execute(self, phone: str, otp_code: str) -> Dict[str, Any]:
        """Verify OTP code"""
        request = PhoneOTPVerifyRequest(phone=phone, otp_code=otp_code)
        result = await self.auth_service.verify_phone_otp(request)
        return {"success": True, "user_id": str(result.user_id), "access_token": result.access_token}
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="verify_otp",
            description="Verify OTP code and authenticate user",
            input_schema={
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Phone number"},
                    "otp_code": {"type": "string", "description": "OTP verification code"}
                },
                "required": ["phone", "otp_code"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "user_id": {"type": "string"},
                    "access_token": {"type": "string"}
                }
            }
        )


class ClientSignupTool(BaseMCPTool):
    """Sign up new client user"""
    
    def __init__(self, auth_service: AuthService):
        super().__init__("client_signup", "Sign up new client user")
        self.auth_service = auth_service
    
    async def execute(self, phone: str, email: str, first_name: str, last_name: str, 
                     pfp_url: Optional[str] = None) -> Dict[str, Any]:
        """Sign up new client"""
        request = ClientSignupRequest(
            phone=phone, email=email, first_name=first_name, 
            last_name=last_name, pfp_url=pfp_url
        )
        result = await self.auth_service.client_signup(request)
        return {"success": True, "user_id": str(result.user_id), "access_token": result.access_token}
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="client_signup",
            description="Sign up new client user",
            input_schema={
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Phone number"},
                    "email": {"type": "string", "description": "Email address"},
                    "first_name": {"type": "string", "description": "First name"},
                    "last_name": {"type": "string", "description": "Last name"},
                    "pfp_url": {"type": "string", "description": "Profile picture URL (optional)"}
                },
                "required": ["phone", "email", "first_name", "last_name"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "user_id": {"type": "string"},
                    "access_token": {"type": "string"}
                }
            }
        )


class HelperSignupTool(BaseMCPTool):
    """Sign up new helper user"""
    
    def __init__(self, auth_service: AuthService):
        super().__init__("helper_signup", "Sign up new helper user")
        self.auth_service = auth_service
    
    async def execute(self, phone: str, email: str, first_name: str, last_name: str,
                     college: str, bio: str, graduation_year: int, zip_code: str,
                     pfp_url: Optional[str] = None) -> Dict[str, Any]:
        """Sign up new helper"""
        request = HelperSignupRequest(
            phone=phone, email=email, first_name=first_name, last_name=last_name,
            college=college, bio=bio, graduation_year=graduation_year, 
            zip_code=zip_code, pfp_url=pfp_url
        )
        result = await self.auth_service.helper_signup(request)
        return {"success": True, "user_id": str(result.user_id), "access_token": result.access_token}
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="helper_signup",
            description="Sign up new helper user",
            input_schema={
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Phone number"},
                    "email": {"type": "string", "description": "Email address"},
                    "first_name": {"type": "string", "description": "First name"},
                    "last_name": {"type": "string", "description": "Last name"},
                    "college": {"type": "string", "description": "College/University name"},
                    "bio": {"type": "string", "description": "Personal bio"},
                    "graduation_year": {"type": "integer", "description": "Expected graduation year"},
                    "zip_code": {"type": "string", "description": "ZIP code"},
                    "pfp_url": {"type": "string", "description": "Profile picture URL (optional)"}
                },
                "required": ["phone", "email", "first_name", "last_name", "college", "bio", "graduation_year", "zip_code"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "user_id": {"type": "string"},
                    "access_token": {"type": "string"}
                }
            }
        )


class GetUserProfileTool(BaseMCPTool):
    """Get user profile information"""
    
    def __init__(self, auth_service: AuthService):
        super().__init__("get_user_profile", "Get user profile information")
        self.auth_service = auth_service
    
    async def execute(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        result = await self.auth_service.get_user_profile(UUID(user_id))
        return {
            "user_id": str(result.user_id),
            "profile_type": result.profile_type,
            "profile_data": result.profile_data.dict() if result.profile_data else None
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_user_profile",
            description="Get user profile information",
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
                    "user_id": {"type": "string"},
                    "profile_type": {"type": "string"},
                    "profile_data": {"type": "object"}
                }
            }
        )


def register_auth_tools(auth_service: AuthService):
    """Register all auth tools"""
    tools = [
        SendOTPTool(auth_service),
        VerifyOTPTool(auth_service),
        ClientSignupTool(auth_service),
        HelperSignupTool(auth_service),
        GetUserProfileTool(auth_service)
    ]
    
    for tool in tools:
        tool_registry.register(tool)
    
    return tools
