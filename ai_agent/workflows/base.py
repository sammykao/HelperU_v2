"""
Base Workflow Class using LangGraph
Provides common functionality for all workflows
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel
import logging
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver


class WorkflowState(TypedDict):
    """Base state for all workflows"""
    messages: List[Dict[str, Any]]
    context: Dict[str, Any]
    current_step: str
    workflow_data: Dict[str, Any]
    errors: List[str]


class BaseWorkflow(ABC):
    """Base class for all LangGraph workflows"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"workflow.{name}")
        self.graph: Optional[StateGraph] = None
        self.memory_saver = MemorySaver()
        
    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        pass
    
    @abstractmethod
    def get_workflow_steps(self) -> List[str]:
        """Get list of workflow steps"""
        pass
    
    def initialize(self):
        """Initialize the workflow graph"""
        if not self.graph:
            self.graph = self.build_graph()
            self.logger.info(f"Initialized workflow: {self.name}")
    
    async def run(self, initial_state: WorkflowState, config: Optional[Dict[str, Any]] = None) -> WorkflowState:
        """Run the workflow with initial state"""
        if not self.graph:
            self.initialize()
        
        try:
            # Run the workflow
            result = await self.graph.ainvoke(
                initial_state,
                config=config or {}
            )
            
            self.logger.info(f"Workflow {self.name} completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error running workflow {self.name}: {e}")
            # Add error to state
            initial_state["errors"].append(str(e))
            return initial_state
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get workflow information"""
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.get_workflow_steps(),
            "initialized": self.graph is not None
        }
    
    def add_error_handling(self, state: WorkflowState, error: str):
        """Add error to workflow state"""
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(error)
    
    def create_initial_state(self, **kwargs) -> WorkflowState:
        """Create initial workflow state"""
        return WorkflowState(
            messages=[],
            context=kwargs.get("context", {}),
            current_step="start",
            workflow_data=kwargs.get("workflow_data", {}),
            errors=[]
        )
    
    def add_message(self, state: WorkflowState, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add message to workflow state"""
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        state["messages"].append(message)
    
    def update_context(self, state: WorkflowState, key: str, value: Any):
        """Update workflow context"""
        state["context"][key] = value
    
    def get_context(self, state: WorkflowState, key: str, default: Any = None) -> Any:
        """Get value from workflow context"""
        return state["context"].get(key, default)
    
    def set_current_step(self, state: WorkflowState, step: str):
        """Set current workflow step"""
        state["current_step"] = step
    
    def add_workflow_data(self, state: WorkflowState, key: str, value: Any):
        """Add data to workflow state"""
        state["workflow_data"][key] = value
    
    def get_workflow_data(self, state: WorkflowState, key: str, default: Any = None) -> Any:
        """Get data from workflow state"""
        return state["workflow_data"].get(key, default)
    
    def has_errors(self, state: WorkflowState) -> bool:
        """Check if workflow has errors"""
        return len(state.get("errors", [])) > 0
    
    def get_errors(self, state: WorkflowState) -> List[str]:
        """Get workflow errors"""
        return state.get("errors", [])
    
    def clear_errors(self, state: WorkflowState):
        """Clear workflow errors"""
        state["errors"] = []
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()
