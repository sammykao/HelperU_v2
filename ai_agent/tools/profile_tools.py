"""
Profile Management MCP Tools
Wraps profile_service functions as MCP tools
"""
from typing import Any, Dict, Optional
from uuid import UUID
from .base import BaseMCPTool, ToolSchema, tool_registry
from app.services.profile_service import ProfileService
from app.schemas.profile import ProfileUpdateData


class GetProfileTool(BaseMCPTool):
    """Get user profile information"""
    
    def __init__(self, profile_service: ProfileService):
        super().__init__("get_profile", "Get user profile information")
        self.profile_service = profile_service
    
    async def execute(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        result = await self.profile_service.get_user_profile(UUID(user_id))
        
        if result.profile_type == "client":
            profile_data = {
                "id": str(result.profile_data.id),
                "first_name": result.profile_data.first_name,
                "last_name": result.profile_data.last_name,
                "email": result.profile_data.email,
                "phone": result.profile_data.phone,
                "pfp_url": result.profile_data.pfp_url,
                "number_of_posts": result.profile_data.number_of_posts
            }
        else:  # helper
            profile_data = {
                "id": str(result.profile_data.id),
                "first_name": result.profile_data.first_name,
                "last_name": result.profile_data.last_name,
                "email": result.profile_data.email,
                "phone": result.profile_data.phone,
                "pfp_url": result.profile_data.pfp_url,
                "college": result.profile_data.college,
                "bio": result.profile_data.bio,
                "graduation_year": result.profile_data.graduation_year,
                "zip_code": result.profile_data.zip_code,
                "number_of_applications": result.profile_data.number_of_applications,
                "invited_count": result.profile_data.invited_count
            }
        
        return {
            "success": True,
            "profile_type": result.profile_type,
            "profile_data": profile_data
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_profile",
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
                    "success": {"type": "boolean"},
                    "profile_type": {"type": "string"},
                    "profile_data": {"type": "object"}
                }
            }
        )


class UpdateProfileTool(BaseMCPTool):
    """Update user profile information"""
    
    def __init__(self, profile_service: ProfileService):
        super().__init__("update_profile", "Update user profile information")
        self.profile_service = profile_service
    
    async def execute(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Update profile with provided fields"""
        # Filter out None values
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        profile_update = ProfileUpdateData(**update_data)
        
        result = await self.profile_service.update_user_profile(UUID(user_id), profile_update)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile_id": str(result.profile_id)
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="update_profile",
            description="Update user profile information",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "first_name": {"type": "string", "description": "First name (optional)"},
                    "last_name": {"type": "string", "description": "Last name (optional)"},
                    "pfp_url": {"type": "string", "description": "Profile picture URL (optional)"},
                    "bio": {"type": "string", "description": "Bio (helpers only, optional)"},
                    "college": {"type": "string", "description": "College (helpers only, optional)"},
                    "graduation_year": {"type": "integer", "description": "Graduation year (helpers only, optional)"},
                    "zip_code": {"type": "string", "description": "ZIP code (helpers only, optional)"}
                },
                "required": ["user_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "profile_id": {"type": "string"}
                }
            }
        )


def register_profile_tools(profile_service: ProfileService):
    """Register all profile tools"""
    tools = [
        GetProfileTool(profile_service),
        UpdateProfileTool(profile_service)
    ]
    
    for tool in tools:
        tool_registry.register(tool)
    
    return tools
