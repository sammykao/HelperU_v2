"""
Application Management MCP Tools
Wraps application_service functions as MCP tools
"""
from typing import Any, Dict, Optional, List
from uuid import UUID
from .base import BaseMCPTool, ToolSchema, tool_registry
from app.services.application_service import ApplicationService
from app.schemas.applications import ApplicationCreateRequest


class CreateApplicationTool(BaseMCPTool):
    """Create a new application for a task"""
    
    def __init__(self, application_service: ApplicationService):
        super().__init__("create_application", "Create a new application for a task")
        self.application_service = application_service
    
    async def execute(self, task_id: str, helper_id: str, introduction_message: str, 
                     supplements_url: Optional[str] = None) -> Dict[str, Any]:
        """Create application"""
        request = ApplicationCreateRequest(
            task_id=task_id,
            helper_id=helper_id,
            introduction_message=introduction_message,
            supplements_url=supplements_url
        )
        result = await self.application_service.create_application(request)
        
        return {
            "success": True,
            "application_id": str(result.id),
            "task_id": str(result.task_id),
            "helper_id": str(result.helper_id),
            "status": "created"
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="create_application",
            description="Create a new application for a task",
            input_schema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"},
                    "helper_id": {"type": "string", "description": "Helper user ID"},
                    "introduction_message": {"type": "string", "description": "Introduction message"},
                    "supplements_url": {"type": "string", "description": "Supplemental materials URL (optional)"}
                },
                "required": ["task_id", "helper_id", "introduction_message"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "application_id": {"type": "string"},
                    "task_id": {"type": "string"},
                    "helper_id": {"type": "string"},
                    "status": {"type": "string"}
                }
            }
        )


class GetApplicationTool(BaseMCPTool):
    """Get application details"""
    
    def __init__(self, application_service: ApplicationService):
        super().__init__("get_application", "Get application details")
        self.application_service = application_service
    
    async def execute(self, application_id: str) -> Dict[str, Any]:
        """Get application"""
        result = await self.application_service.get_application(UUID(application_id))
        
        return {
            "success": True,
            "application": {
                "id": str(result.id),
                "task_id": str(result.task_id),
                "helper_id": str(result.helper_id),
                "introduction_message": result.introduction_message,
                "supplements_url": result.supplements_url,
                "created_at": result.created_at.isoformat(),
                "updated_at": result.updated_at.isoformat()
            }
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_application",
            description="Get application details",
            input_schema={
                "type": "object",
                "properties": {
                    "application_id": {"type": "string", "description": "Application ID"}
                },
                "required": ["application_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "application": {"type": "object"}
                }
            }
        )


class GetTaskApplicationsTool(BaseMCPTool):
    """Get all applications for a task"""
    
    def __init__(self, application_service: ApplicationService):
        super().__init__("get_task_applications", "Get all applications for a task")
        self.application_service = application_service
    
    async def execute(self, task_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get task applications"""
        result = await self.application_service.get_task_applications(UUID(task_id), limit, offset)
        
        applications = []
        for app in result.applications:
            applications.append({
                "id": str(app.id),
                "helper_id": str(app.helper_id),
                "introduction_message": app.introduction_message,
                "supplements_url": app.supplements_url,
                "created_at": app.created_at.isoformat()
            })
        
        return {
            "success": True,
            "applications": applications,
            "total": result.total,
            "has_more": result.has_more
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_task_applications",
            description="Get all applications for a task",
            input_schema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"},
                    "limit": {"type": "integer", "description": "Number of results to return", "default": 20},
                    "offset": {"type": "integer", "description": "Number of results to skip", "default": 0}
                },
                "required": ["task_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "applications": {"type": "array", "items": {"type": "object"}},
                    "total": {"type": "integer"},
                    "has_more": {"type": "boolean"}
                }
            }
        )


class GetHelperApplicationsTool(BaseMCPTool):
    """Get all applications by a helper"""
    
    def __init__(self, application_service: ApplicationService):
        super().__init__("get_helper_applications", "Get all applications by a helper")
        self.application_service = application_service
    
    async def execute(self, helper_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get helper applications"""
        result = await self.application_service.get_helper_applications(UUID(helper_id), limit, offset)
        
        applications = []
        for app in result.applications:
            applications.append({
                "id": str(app.id),
                "task_id": str(app.task_id),
                "introduction_message": app.introduction_message,
                "supplements_url": app.supplements_url,
                "created_at": app.created_at.isoformat()
            })
        
        return {
            "success": True,
            "applications": applications,
            "total": result.total,
            "has_more": result.has_more
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_helper_applications",
            description="Get all applications by a helper",
            input_schema={
                "type": "object",
                "properties": {
                    "helper_id": {"type": "string", "description": "Helper user ID"},
                    "limit": {"type": "integer", "description": "Number of results to return", "default": 20},
                    "offset": {"type": "integer", "description": "Number of results to skip", "default": 0}
                },
                "required": ["helper_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "applications": {"type": "array", "items": {"type": "object"}},
                    "total": {"type": "integer"},
                    "has_more": {"type": "boolean"}
                }
            }
        )


def register_application_tools(application_service: ApplicationService):
    """Register all application tools"""
    tools = [
        CreateApplicationTool(application_service),
        GetApplicationTool(application_service),
        GetTaskApplicationsTool(application_service),
        GetHelperApplicationsTool(application_service)
    ]
    
    for tool in tools:
        tool_registry.register(tool)
    
    return tools
