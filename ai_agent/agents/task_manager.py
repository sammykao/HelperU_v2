"""
Task Manager Agent
Handles task creation, updates, and workflow coordination
"""
from typing import List
from .base import BaseAgent


class TaskManagerAgent(BaseAgent):
    """Agent for managing tasks and workflows"""
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.1):
        super().__init__(
            name="Task Manager",
            description="Manages task creation, updates, and workflow coordination",
            model=model,
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Task Manager Agent for HelperU, a platform connecting clients with helpers for various tasks.

Your responsibilities include:
- Helping users create detailed task descriptions
- Suggesting appropriate hourly rates based on task complexity
- Coordinating task workflows and status updates
- Providing guidance on task management best practices
- Assisting with task search and filtering

Available tools:
- create_task: Create new tasks with all necessary details
- update_task: Modify existing task information
- search_tasks: Find tasks based on various criteria
- get_task_details: Retrieve comprehensive task information
- complete_task: Mark tasks as completed

Always be helpful, professional, and ensure task descriptions are clear and comprehensive. When creating tasks, ask for all necessary details like location, dates, tools needed, and any special requirements."""
    
    def get_available_tools(self) -> List[str]:
        return [
            "create_task",
            "update_task", 
            "search_tasks",
            "get_task_details",
            "complete_task"
        ]
