"""
Task Management MCP Tools
Wraps task_service functions as MCP tools
"""
from typing import Any, Dict, Optional, List
from uuid import UUID
from .base import BaseMCPTool, ToolSchema, tool_registry
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskSearchRequest


class CreateTaskTool(BaseMCPTool):
    """Create a new task"""
    
    def __init__(self, task_service: TaskService):
        super().__init__("create_task", "Create a new task")
        self.task_service = task_service
    
    async def execute(self, client_id: str, hourly_rate: float, title: str, 
                     dates: List[str], location_type: str, zip_code: str,
                     description: str, tools_info: Optional[str] = None,
                     public_transport_info: Optional[str] = None) -> Dict[str, Any]:
        """Create a new task"""
        task_data = TaskCreate(
            client_id=UUID(client_id),
            hourly_rate=hourly_rate,
            title=title,
            dates=dates,
            location_type=location_type,
            zip_code=zip_code,
            description=description,
            tools_info=tools_info,
            public_transport_info=public_transport_info
        )
        result = await self.task_service.create_task(task_data)
        return {
            "success": True,
            "task_id": str(result.id),
            "title": result.title,
            "status": "created"
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="create_task",
            description="Create a new task",
            input_schema={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string", "description": "Client user ID"},
                    "hourly_rate": {"type": "number", "description": "Hourly rate for the task"},
                    "title": {"type": "string", "description": "Task title"},
                    "dates": {"type": "array", "items": {"type": "string"}, "description": "Available dates"},
                    "location_type": {"type": "string", "description": "Location type (remote/onsite)"},
                    "zip_code": {"type": "string", "description": "ZIP code for location"},
                    "description": {"type": "string", "description": "Task description"},
                    "tools_info": {"type": "string", "description": "Tools information (optional)"},
                    "public_transport_info": {"type": "string", "description": "Public transport info (optional)"}
                },
                "required": ["client_id", "hourly_rate", "title", "dates", "location_type", "zip_code", "description"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "task_id": {"type": "string"},
                    "title": {"type": "string"},
                    "status": {"type": "string"}
                }
            }
        )


class UpdateTaskTool(BaseMCPTool):
    """Update an existing task"""
    
    def __init__(self, task_service: TaskService):
        super().__init__("update_task", "Update an existing task")
        self.task_service = task_service
    
    async def execute(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """Update task with provided fields"""
        # Filter out None values
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        task_update = TaskUpdate(**update_data)
        
        result = await self.task_service.update_task(UUID(task_id), task_update)
        return {
            "success": True,
            "task_id": str(result.id),
            "title": result.title,
            "status": "updated"
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="update_task",
            description="Update an existing task",
            input_schema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to update"},
                    "title": {"type": "string", "description": "New task title (optional)"},
                    "hourly_rate": {"type": "number", "description": "New hourly rate (optional)"},
                    "dates": {"type": "array", "items": {"type": "string"}, "description": "New dates (optional)"},
                    "description": {"type": "string", "description": "New description (optional)"},
                    "tools_info": {"type": "string", "description": "New tools info (optional)"},
                    "public_transport_info": {"type": "string", "description": "New transport info (optional)"}
                },
                "required": ["task_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "task_id": {"type": "string"},
                    "title": {"type": "string"},
                    "status": {"type": "string"}
                }
            }
        )


class SearchTasksTool(BaseMCPTool):
    """Search for tasks based on criteria"""
    
    def __init__(self, task_service: TaskService):
        super().__init__("search_tasks", "Search for tasks based on criteria")
        self.task_service = task_service
    
    async def execute(self, zip_code: Optional[str] = None, max_distance: Optional[float] = None,
                     min_rate: Optional[float] = None, max_rate: Optional[float] = None,
                     location_type: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search for tasks"""
        search_request = TaskSearchRequest(
            zip_code=zip_code,
            max_distance=max_distance,
            min_rate=min_rate,
            max_rate=max_rate,
            location_type=location_type
        )
        
        result = await self.task_service.search_tasks(search_request, limit, offset)
        
        tasks = []
        for task in result.tasks:
            tasks.append({
                "id": str(task.id),
                "title": task.title,
                "hourly_rate": task.hourly_rate,
                "description": task.description,
                "location_type": task.location_type,
                "zip_code": task.zip_code,
                "created_at": task.created_at.isoformat()
            })
        
        return {
            "success": True,
            "tasks": tasks,
            "total": result.total,
            "has_more": result.has_more
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="search_tasks",
            description="Search for tasks based on criteria",
            input_schema={
                "type": "object",
                "properties": {
                    "zip_code": {"type": "string", "description": "ZIP code to search around (optional)"},
                    "max_distance": {"type": "number", "description": "Maximum distance in miles (optional)"},
                    "min_rate": {"type": "number", "description": "Minimum hourly rate (optional)"},
                    "max_rate": {"type": "number", "description": "Maximum hourly rate (optional)"},
                    "location_type": {"type": "string", "description": "Location type filter (optional)"},
                    "limit": {"type": "integer", "description": "Number of results to return", "default": 20},
                    "offset": {"type": "integer", "description": "Number of results to skip", "default": 0}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "tasks": {"type": "array", "items": {"type": "object"}},
                    "total": {"type": "integer"},
                    "has_more": {"type": "boolean"}
                }
            }
        )


class GetTaskDetailsTool(BaseMCPTool):
    """Get detailed information about a specific task"""
    
    def __init__(self, task_service: TaskService):
        super().__init__("get_task_details", "Get detailed information about a specific task")
        self.task_service = task_service
    
    async def execute(self, task_id: str) -> Dict[str, Any]:
        """Get task details"""
        result = await self.task_service.get_task(UUID(task_id))
        
        return {
            "success": True,
            "task": {
                "id": str(result.id),
                "title": result.title,
                "hourly_rate": result.hourly_rate,
                "description": result.description,
                "dates": result.dates,
                "location_type": result.location_type,
                "zip_code": result.zip_code,
                "tools_info": result.tools_info,
                "public_transport_info": result.public_transport_info,
                "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                "created_at": result.created_at.isoformat(),
                "updated_at": result.updated_at.isoformat()
            }
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_task_details",
            description="Get detailed information about a specific task",
            input_schema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"}
                },
                "required": ["task_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "task": {"type": "object"}
                }
            }
        )


class CompleteTaskTool(BaseMCPTool):
    """Mark a task as completed"""
    
    def __init__(self, task_service: TaskService):
        super().__init__("complete_task", "Mark a task as completed")
        self.task_service = task_service
    
    async def execute(self, task_id: str) -> Dict[str, Any]:
        """Mark task as completed"""
        result = await self.task_service.complete_task(UUID(task_id))
        return {
            "success": True,
            "task_id": str(result.id),
            "status": "completed",
            "completed_at": result.completed_at.isoformat() if result.completed_at else None
        }
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="complete_task",
            description="Mark a task as completed",
            input_schema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to complete"}
                },
                "required": ["task_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "task_id": {"type": "string"},
                    "status": {"type": "string"},
                    "completed_at": {"type": "string"}
                }
            }
        )


def register_task_tools(task_service: TaskService):
    """Register all task tools"""
    tools = [
        CreateTaskTool(task_service),
        UpdateTaskTool(task_service),
        SearchTasksTool(task_service),
        GetTaskDetailsTool(task_service),
        CompleteTaskTool(task_service)
    ]
    
    for tool in tools:
        tool_registry.register(tool)
    
    return tools
