"""Authentication tools for AI agents"""

from typing import Any, Dict, Optional
from app.ai_agent.base import BaseTool
from app.services.auth_service import AuthService
from app.schemas.auth import (
    ClientProfileUpdateRequest,
    HelperSignupRequest,
    HelperProfileUpdateRequest
)

class AuthTools(BaseTool):
    """Tools for authentication operations"""
    
    def __init__(self, auth_service: AuthService):
        super().__init__("auth_tools", "Tools for user authentication and verification")
        self.auth_service = auth_service
    
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute authentication tool action"""
        try:
            if action == "send_client_otp":
                return await self._send_client_otp(**kwargs)
            elif action == "verify_client_otp":
                return await self._verify_client_otp(**kwargs)
            elif action == "create_helper_account":
                return await self._create_helper_account(**kwargs)
            elif action == "verify_helper_otp":
                return await self._verify_helper_otp(**kwargs)
            elif action == "verify_email_otp":
                return await self._verify_email_otp(**kwargs)
            elif action == "resend_email_verification":
                return await self._resend_email_verification(**kwargs)
            elif action == "get_helper_profile_status":
                return await self._get_helper_profile_status(**kwargs)
            elif action == "logout":
                return await self._logout(**kwargs)
            else:
                raise ValueError(f"Unknown auth action: {action}")
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _send_client_otp(self, phone: str) -> Dict[str, Any]:
        """Send OTP to client phone"""
        result = await self.auth_service.send_client_otp(phone)
        return {
            "success": result.success,
            "message": result.message
        }
    
    async def _verify_client_otp(self, phone: str, token: str) -> Dict[str, Any]:
        """Verify client OTP"""
        result = await self.auth_service.verify_client_otp(phone, token)
        return {
            "success": result.success,
            "user_id": result.user_id,
            "access_token": result.access_token,
            "refresh_token": result.refresh_token,
            "message": result.message
        }
    
    async def _create_helper_account(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create helper account"""
        request = HelperSignupRequest(**request_data)
        result = await self.auth_service.create_helper_account(request)
        return {
            "success": result.success,
            "message": result.message,
            "user_id": result.user_id if hasattr(result, 'user_id') else None
        }
    
    async def _verify_helper_otp(self, phone: str, token: str) -> Dict[str, Any]:
        """Verify helper OTP"""
        result = await self.auth_service.verify_helper_otp(phone, token)
        return {
            "success": result.success,
            "access_token": result.access_token,
            "refresh_token": result.refresh_token,
            "message": result.message
        }
    
    async def _verify_email_otp(self, user_id: str, otp: str) -> Dict[str, Any]:
        """Verify email OTP"""
        result = await self.auth_service.verify_email_otp(user_id, otp)
        return {
            "success": result.success,
            "message": result.message
        }
    
    async def _resend_email_verification(self, email: str) -> Dict[str, Any]:
        """Resend email verification"""
        result = await self.auth_service.resend_email_verification(email)
        return {
            "success": result.success,
            "message": result.message
        }
    
    async def _get_helper_profile_status(self, user_id: str) -> Dict[str, Any]:
        """Get helper profile status"""
        result = await self.auth_service.get_helper_profile_status(user_id)
        return {
            "success": result.success,
            "email_verified": result.email_verified,
            "phone_verified": result.phone_verified,
            "profile_complete": result.profile_complete,
            "message": result.message
        }
    
    async def _logout(self, user_id: str) -> Dict[str, Any]:
        """Logout user"""
        result = await self.auth_service.logout(user_id)
        return {
            "success": result.success,
            "message": result.message
        }
    
    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema for auth tools"""
        return {
            "actions": {
                "send_client_otp": {
                    "phone": "string - Phone number to send OTP to"
                },
                "verify_client_otp": {
                    "phone": "string - Phone number",
                    "token": "string - OTP token"
                },
                "create_helper_account": {
                    "request_data": "object - Helper signup data"
                },
                "verify_helper_otp": {
                    "phone": "string - Phone number",
                    "token": "string - OTP token"
                },
                "verify_email_otp": {
                    "user_id": "string - User ID",
                    "otp": "string - Email OTP code"
                },
                "resend_email_verification": {
                    "email": "string - Email address"
                },
                "get_helper_profile_status": {
                    "user_id": "string - User ID"
                },
                "logout": {
                    "user_id": "string - User ID"
                }
            }
        }

