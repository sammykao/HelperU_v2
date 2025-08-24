"""
Task Creation Workflow
Multi-step workflow for creating and managing tasks
"""
from typing import List, Dict, Any
from .base import BaseWorkflow, WorkflowState
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode


class TaskCreationWorkflow(BaseWorkflow):
    """Workflow for creating and managing tasks"""
    
    def __init__(self):
        super().__init__(
            name="Task Creation Workflow",
            description="Multi-step workflow for creating and managing tasks"
        )
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each step
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("create_task", self._create_task)
        workflow.add_node("notify_helpers", self._notify_helpers)
        workflow.add_node("finalize", self._finalize)
        
        # Define the workflow flow
        workflow.set_entry_point("validate_input")
        workflow.add_edge("validate_input", "create_task")
        workflow.add_edge("create_task", "notify_helpers")
        workflow.add_edge("notify_helpers", "finalize")
        workflow.add_edge("finalize", END)
        
        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "validate_input",
            self._should_continue,
            {
                "continue": "create_task",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "create_task",
            self._should_continue,
            {
                "continue": "notify_helpers",
                "error": END
            }
        )
        
        return workflow
    
    def get_workflow_steps(self) -> List[str]:
        """Get list of workflow steps"""
        return [
            "validate_input",
            "create_task", 
            "notify_helpers",
            "finalize"
        ]
    
    async def _validate_input(self, state: WorkflowState) -> WorkflowState:
        """Validate task creation input"""
        self.set_current_step(state, "validate_input")
        self.add_message(state, "system", "Validating task input...")
        
        # Get task data from context
        task_data = self.get_context(state, "task_data", {})
        
        # Validate required fields
        required_fields = ["title", "description", "hourly_rate", "zip_code"]
        missing_fields = [field for field in required_fields if not task_data.get(field)]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            self.add_error_handling(state, error_msg)
            self.add_message(state, "system", f"Validation failed: {error_msg}")
            return state
        
        # Validate data types and ranges
        if not isinstance(task_data.get("hourly_rate"), (int, float)) or task_data["hourly_rate"] <= 0:
            error_msg = "Hourly rate must be a positive number"
            self.add_error_handling(state, error_msg)
            self.add_message(state, "system", f"Validation failed: {error_msg}")
            return state
        
        if not isinstance(task_data.get("dates"), list) or len(task_data["dates"]) == 0:
            error_msg = "At least one available date must be specified"
            self.add_error_handling(state, error_msg)
            self.add_message(state, error_msg)
            return state
        
        self.add_message(state, "system", "Task input validation successful")
        self.update_context(state, "validation_passed", True)
        
        return state
    
    async def _create_task(self, state: WorkflowState) -> WorkflowState:
        """Create the task in the system"""
        self.set_current_step(state, "create_task")
        self.add_message(state, "system", "Creating task...")
        
        try:
            # This would integrate with the actual task creation tool
            # For now, simulating the process
            task_data = self.get_context(state, "task_data", {})
            
            # Simulate task creation
            task_id = f"task_{len(task_data.get('title', ''))}"
            self.add_workflow_data(state, "task_id", task_id)
            self.add_workflow_data(state, "task_created", True)
            
            self.add_message(state, "system", f"Task created successfully with ID: {task_id}")
            
        except Exception as e:
            error_msg = f"Failed to create task: {str(e)}"
            self.add_error_handling(state, error_msg)
            self.add_message(state, "system", f"Task creation failed: {error_msg}")
        
        return state
    
    async def _notify_helpers(self, state: WorkflowState) -> WorkflowState:
        """Notify relevant helpers about the new task"""
        self.set_current_step(state, "notify_helpers")
        self.add_message(state, "system", "Notifying relevant helpers...")
        
        try:
            # This would integrate with the notification system
            # For now, simulating the process
            task_data = self.get_context(state, "task_data", {})
            zip_code = task_data.get("zip_code", "")
            
            # Simulate helper notification
            helpers_notified = 5  # Mock number
            self.add_workflow_data(state, "helpers_notified", helpers_notified)
            
            self.add_message(
                state, 
                "system", 
                f"Notified {helpers_notified} helpers in area {zip_code}"
            )
            
        except Exception as e:
            error_msg = f"Failed to notify helpers: {str(e)}"
            self.add_error_handling(state, error_msg)
            self.add_message(state, "system", f"Helper notification failed: {error_msg}")
        
        return state
    
    async def _finalize(self, state: WorkflowState) -> WorkflowState:
        """Finalize the workflow"""
        self.set_current_step(state, "finalize")
        self.add_message(state, "system", "Finalizing task creation workflow...")
        
        # Compile workflow results
        task_id = self.get_workflow_data(state, "task_id", "unknown")
        helpers_notified = self.get_workflow_data(state, "helpers_notified", 0)
        
        summary = f"Task creation workflow completed successfully. Task ID: {task_id}, Helpers notified: {helpers_notified}"
        self.add_message(state, "system", summary)
        
        # Update final context
        self.update_context(state, "workflow_completed", True)
        self.update_context(state, "final_summary", summary)
        
        return state
    
    def _should_continue(self, state: WorkflowState) -> str:
        """Determine if workflow should continue or end due to errors"""
        if self.has_errors(state):
            return "error"
        return "continue"
    
    def create_task_workflow_state(self, task_data: Dict[str, Any], user_id: str) -> WorkflowState:
        """Create initial state for task creation workflow"""
        return self.create_initial_state(
            context={
                "task_data": task_data,
                "user_id": user_id,
                "workflow_type": "task_creation"
            },
            workflow_data={
                "start_time": "now",
                "user_id": user_id
            }
        )
