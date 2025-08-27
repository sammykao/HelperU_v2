"""Task tools for AI agents"""

from typing import Any, Dict, List, Optional
from app.ai_agent.base import BaseTool
from app.services.task_service import TaskService
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskSearchRequest
)

class TaskTools(BaseTool):
    """Tools for task management operations"""
    
    def __init__(self, task_service: TaskService):
        super().__init__("task_tools", "Tools for managing tasks and assignments")
        self.task_service = task_service
    
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute task tool action"""
        try:
            if action == "create_task":
                return await self._create_task(**kwargs)
            elif action == "get_task":
                return await self._get_task(**kwargs)
            elif action == "update_task":
                return await self._update_task(**kwargs)
            elif action == "delete_task":
                return await self._delete_task(**kwargs)
            elif action == "search_tasks":
                return await self._search_tasks(**kwargs)
            elif action == "get_user_tasks":
                return await self._get_user_tasks(**kwargs)
            elif action == "complete_task":
                return await self._complete_task(**kwargs)
            else:
                raise ValueError(f"Unknown task action: {action}")
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _create_task(self, client_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        try:
            request = TaskCreate(**task_data)
            result = await self.task_service.create_task(client_id, request)
            return {
                "success": True,
                "task_id": str(result.id),
                "title": result.title,
                "description": result.description,
                "client_id": str(result.client_id),
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "status": result.status
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a single task by ID"""
        try:
            result = await self.task_service.get_task(task_id)
            if not result:
                return {"error": "Task not found", "success": False}
            
            return {
                "success": True,
                "task_id": str(result.id),
                "title": result.title,
                "description": result.description,
                "client_id": str(result.client_id),
                "helper_id": str(result.helper_id) if result.helper_id else None,
                "status": result.status,
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                "budget": result.budget,
                "location": result.location
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _update_task(self, task_id: str, user_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing task"""
        try:
            request = TaskUpdate(**task_data)
            result = await self.task_service.update_task(task_id, user_id, request)
            return {
                "success": True,
                "task_id": str(result.id),
                "title": result.title,
                "description": result.description,
                "status": result.status,
                "updated_at": result.updated_at.isoformat() if result.updated_at else None
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _delete_task(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a task"""
        try:
            result = await self.task_service.delete_task(task_id, user_id)
            return {
                "success": result,
                "message": "Task deleted successfully" if result else "Failed to delete task"
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _search_tasks(self, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for tasks based on criteria"""
        try:
            request = TaskSearchRequest(**search_data)
            result = await self.task_service.search_tasks(request)
            return {
                "success": True,
                "tasks": [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "client_id": str(task.client_id),
                        "helper_id": str(task.helper_id) if task.helper_id else None,
                        "status": task.status,
                        "budget": task.budget,
                        "location": task.location,
                        "created_at": task.created_at.isoformat() if task.created_at else None
                    }
                    for task in result.tasks
                ],
                "total": result.total
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _get_user_tasks(self, user_id: str, user_type: str = "client") -> Dict[str, Any]:
        """Get tasks for a specific user (client or helper)"""
        try:
            if user_type == "client":
                result = await self.task_service.get_client_tasks(user_id)
            else:
                result = await self.task_service.get_helper_tasks(user_id)
            
            return {
                "success": True,
                "tasks": [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "budget": task.budget,
                        "location": task.location,
                        "created_at": task.created_at.isoformat() if task.created_at else None
                    }
                    for task in result.tasks
                ],
                "total": result.total
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _complete_task(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """Mark a task as completed"""
        try:
            # Create a completion update
            completion_data = {"status": "completed"}
            request = TaskUpdate(**completion_data)
            result = await self.task_service.update_task(task_id, user_id, request)
            
            return {
                "success": True,
                "task_id": str(result.id),
                "status": result.status,
                "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                "message": "Task marked as completed"
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema for task tools"""
        return {
            "actions": {
                "create_task": {
                    "client_id": "string - Client ID creating the task",
                    "task_data": "object - Task creation data (title, description, budget, location, etc.)"
                },
                "get_task": {
                    "task_id": "string - Task ID to retrieve"
                },
                "update_task": {
                    "task_id": "string - Task ID to update",
                    "user_id": "string - User ID making the update",
                    "task_data": "object - Task update data"
                },
                "delete_task": {
                    "task_id": "string - Task ID to delete",
                    "user_id": "string - User ID requesting deletion"
                },
                "search_tasks": {
                    "search_data": "object - Search criteria (keywords, location, budget_range, etc.)"
                },
                "get_user_tasks": {
                    "user_id": "string - User ID to get tasks for",
                    "user_type": "string - Type of user ('client' or 'helper')"
                },
                "complete_task": {
                    "task_id": "string - Task ID to complete",
                    "user_id": "string - User ID completing the task"
                }
            }
        }

