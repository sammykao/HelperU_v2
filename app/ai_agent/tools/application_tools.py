"""Application tools for AI agents"""

from typing import Any, Dict, List, Optional
from app.ai_agent.base import BaseTool
from app.services.application_service import ApplicationService

class ApplicationTools(BaseTool):
    """Tools for application management operations"""
    
    def __init__(self, application_service: ApplicationService):
        super().__init__("application_tools", "Tools for managing task applications")
        self.application_service = application_service
    
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute application tool action"""
        try:
            if action == "create_application":
                return await self._create_application(**kwargs)
            elif action == "get_application":
                return await self._get_application(**kwargs)
            elif action == "update_application":
                return await self._update_application(**kwargs)
            elif action == "delete_application":
                return await self._delete_application(**kwargs)
            elif action == "get_task_applications":
                return await self._get_task_applications(**kwargs)
            elif action == "get_helper_applications":
                return await self._get_helper_applications(**kwargs)
            elif action == "accept_application":
                return await self._accept_application(**kwargs)
            elif action == "reject_application":
                return await self._reject_application(**kwargs)
            else:
                raise ValueError(f"Unknown application action: {action}")
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _create_application(self, helper_id: str, task_id: str, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new application"""
        try:
            result = await self.application_service.create_application(helper_id, task_id, application_data)
            return {
                "success": True,
                "application_id": str(result.id),
                "helper_id": str(result.helper_id),
                "task_id": str(result.task_id),
                "status": result.status,
                "created_at": result.created_at.isoformat() if result.created_at else None
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_application(self, application_id: str) -> Dict[str, Any]:
        """Get application by ID"""
        try:
            result = await self.application_service.get_application(application_id)
            if not result:
                return {"error": "Application not found", "success": False}
            
            return {
                "success": True,
                "application": {
                    "id": str(result.id),
                    "helper_id": str(result.helper_id),
                    "task_id": str(result.task_id),
                    "status": result.status,
                    "proposal": result.proposal,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _update_application(self, application_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update application"""
        try:
            result = await self.application_service.update_application(application_id, user_id, update_data)
            return {
                "success": True,
                "message": "Application updated successfully",
                "application": {
                    "id": str(result.id),
                    "status": result.status,
                    "proposal": result.proposal,
                    "updated_at": result.updated_at.isoformat() if result.updated_at else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _delete_application(self, application_id: str, user_id: str) -> Dict[str, Any]:
        """Delete application"""
        try:
            result = await self.application_service.delete_application(application_id, user_id)
            return {
                "success": result,
                "message": "Application deleted successfully" if result else "Failed to delete application"
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_task_applications(self, task_id: str) -> Dict[str, Any]:
        """Get all applications for a task"""
        try:
            result = await self.application_service.get_task_applications(task_id)
            return {
                "success": True,
                "applications": [
                    {
                        "id": str(app.id),
                        "helper_id": str(app.helper_id),
                        "status": app.status,
                        "proposal": app.proposal,
                        "created_at": app.created_at.isoformat() if app.created_at else None
                    }
                    for app in result.applications
                ],
                "total": result.total
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_helper_applications(self, helper_id: str) -> Dict[str, Any]:
        """Get all applications by a helper"""
        try:
            result = await self.application_service.get_helper_applications(helper_id)
            return {
                "success": True,
                "applications": [
                    {
                        "id": str(app.id),
                        "task_id": str(app.task_id),
                        "status": app.status,
                        "proposal": app.proposal,
                        "created_at": app.created_at.isoformat() if app.created_at else None
                    }
                    for app in result.applications
                ],
                "total": result.total
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _accept_application(self, application_id: str, client_id: str) -> Dict[str, Any]:
        """Accept an application"""
        try:
            result = await self.application_service.accept_application(application_id, client_id)
            return {
                "success": True,
                "message": "Application accepted successfully",
                "application": {
                    "id": str(result.id),
                    "status": result.status,
                    "updated_at": result.updated_at.isoformat() if result.updated_at else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _reject_application(self, application_id: str, client_id: str) -> Dict[str, Any]:
        """Reject an application"""
        try:
            result = await self.application_service.reject_application(application_id, client_id)
            return {
                "success": True,
                "message": "Application rejected successfully",
                "application": {
                    "id": str(result.id),
                    "status": result.status,
                    "updated_at": result.updated_at.isoformat() if result.updated_at else None
                }
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema for application tools"""
        return {
            "actions": {
                "create_application": {
                    "helper_id": "string - Helper ID creating the application",
                    "task_id": "string - Task ID to apply for",
                    "application_data": "object - Application data (proposal, etc.)"
                },
                "get_application": {
                    "application_id": "string - Application ID to retrieve"
                },
                "update_application": {
                    "application_id": "string - Application ID to update",
                    "user_id": "string - User ID making the update",
                    "update_data": "object - Update data"
                },
                "delete_application": {
                    "application_id": "string - Application ID to delete",
                    "user_id": "string - User ID requesting deletion"
                },
                "get_task_applications": {
                    "task_id": "string - Task ID to get applications for"
                },
                "get_helper_applications": {
                    "helper_id": "string - Helper ID to get applications for"
                },
                "accept_application": {
                    "application_id": "string - Application ID to accept",
                    "client_id": "string - Client ID accepting the application"
                },
                "reject_application": {
                    "application_id": "string - Application ID to reject",
                    "client_id": "string - Client ID rejecting the application"
                }
            }
        }

