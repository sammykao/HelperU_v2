"""Helper tools for AI agents"""

from typing import Any, Dict, List, Optional
from app.ai_agent.base import BaseTool
from app.services.helper_service import HelperService

class HelperTools(BaseTool):
    """Tools for helper management operations"""
    
    def __init__(self, helper_service: HelperService):
        super().__init__("helper_tools", "Tools for managing helper operations")
        self.helper_service = helper_service
    
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute helper tool action"""
        try:
            if action == "get_helpers":
                return await self._get_helpers(**kwargs)
            elif action == "get_helper_by_id":
                return await self._get_helper_by_id(**kwargs)
            elif action == "search_helpers":
                return await self._search_helpers(**kwargs)
            else:
                raise ValueError(f"Unknown helper action: {action}")
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_helpers(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get list of helpers"""
        try:
            result = await self.helper_service.get_helpers(limit, offset)
            return {
                "success": True,
                "helpers": [
                    {
                        "id": str(helper.id),
                        "first_name": helper.first_name,
                        "last_name": helper.last_name,
                        "email": helper.email,
                        "college": helper.college,
                        "bio": helper.bio,
                        "graduation_year": helper.graduation_year,
                        "zip_code": helper.zip_code,
                        "created_at": helper.created_at.isoformat() if helper.created_at else None
                    }
                    for helper in result.helpers
                ],
                "total": result.total
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_helper_by_id(self, helper_id: str) -> Dict[str, Any]:
        """Get helper by ID"""
        try:
            result = await self.helper_service.get_helper_by_id(helper_id)
            if not result:
                return {"error": "Helper not found", "success": False}
            
            return {
                "success": True,
                "helper": {
                    "id": str(result.id),
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "email": result.email,
                    "college": result.college,
                    "bio": result.bio,
                    "graduation_year": result.graduation_year,
                    "zip_code": result.zip_code,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _search_helpers(self, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Search helpers based on criteria"""
        try:
            result = await self.helper_service.search_helpers(search_criteria)
            return {
                "success": True,
                "helpers": [
                    {
                        "id": str(helper.id),
                        "first_name": helper.first_name,
                        "last_name": helper.last_name,
                        "email": helper.email,
                        "college": helper.college,
                        "bio": helper.bio,
                        "graduation_year": helper.graduation_year,
                        "zip_code": helper.zip_code,
                        "created_at": helper.created_at.isoformat() if helper.created_at else None
                    }
                    for helper in result.helpers
                ],
                "total": result.total
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema for helper tools"""
        return {
            "actions": {
                "get_helpers": {
                    "limit": "integer - Maximum number of helpers to return (optional, default 50)",
                    "offset": "integer - Number of helpers to skip (optional, default 0)"
                },
                "get_helper_by_id": {
                    "helper_id": "string - Helper ID to retrieve"
                },
                "search_helpers": {
                    "search_criteria": "object - Search criteria (location, skills, availability, etc.)"
                }
            }
        }

