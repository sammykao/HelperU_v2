"""Profile tools for AI agents"""

from typing import Any, Dict, Optional
from app.ai_agent.base import BaseTool
from app.services.profile_service import ProfileService

class ProfileTools(BaseTool):
    """Tools for profile management operations"""
    
    def __init__(self, profile_service: ProfileService):
        super().__init__("profile_tools", "Tools for managing user profiles")
        self.profile_service = profile_service
    
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute profile tool action"""
        try:
            if action == "get_client_profile":
                return await self._get_client_profile(**kwargs)
            elif action == "update_client_profile":
                return await self._update_client_profile(**kwargs)
            elif action == "get_helper_profile":
                return await self._get_helper_profile(**kwargs)
            elif action == "update_helper_profile":
                return await self._update_helper_profile(**kwargs)
            else:
                raise ValueError(f"Unknown profile action: {action}")
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_client_profile(self, user_id: str) -> Dict[str, Any]:
        """Get client profile"""
        try:
            result = await self.profile_service.get_client_profile(user_id)
            return {
                "success": True,
                "profile": {
                    "id": str(result.id),
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "email": result.email,
                    "phone": result.phone,
                    "zip_code": result.zip_code,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _update_client_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update client profile"""
        try:
            result = await self.profile_service.update_client_profile(user_id, profile_data)
            return {
                "success": True,
                "message": "Profile updated successfully",
                "profile": {
                    "id": str(result.id),
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "email": result.email,
                    "phone": result.phone,
                    "zip_code": result.zip_code,
                    "updated_at": result.updated_at.isoformat() if result.updated_at else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_helper_profile(self, user_id: str) -> Dict[str, Any]:
        """Get helper profile"""
        try:
            result = await self.profile_service.get_helper_profile(user_id)
            return {
                "success": True,
                "profile": {
                    "id": str(result.id),
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "email": result.email,
                    "phone": result.phone,
                    "college": result.college,
                    "bio": result.bio,
                    "graduation_year": result.graduation_year,
                    "zip_code": result.zip_code,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _update_helper_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update helper profile"""
        try:
            result = await self.profile_service.update_helper_profile(user_id, profile_data)
            return {
                "success": True,
                "message": "Profile updated successfully",
                "profile": {
                    "id": str(result.id),
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "email": result.email,
                    "phone": result.phone,
                    "college": result.college,
                    "bio": result.bio,
                    "graduation_year": result.graduation_year,
                    "zip_code": result.zip_code,
                    "updated_at": result.updated_at.isoformat() if result.updated_at else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema for profile tools"""
        return {
            "actions": {
                "get_client_profile": {
                    "user_id": "string - User ID to get profile for"
                },
                "update_client_profile": {
                    "user_id": "string - User ID to update profile for",
                    "profile_data": "object - Profile update data"
                },
                "get_helper_profile": {
                    "user_id": "string - Helper user ID to get profile for"
                },
                "update_helper_profile": {
                    "user_id": "string - Helper user ID to update profile for",
                    "profile_data": "object - Profile update data"
                }
            }
        }

