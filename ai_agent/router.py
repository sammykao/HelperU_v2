"""
Agent Router
Routes requests to appropriate agents and manages workflow execution
"""
from typing import Dict, List, Optional, Any, Union
import logging
from .system import AgentSystem
from .workflows import (
    TaskCreationWorkflow, ApplicationReviewWorkflow, DisputeResolutionWorkflow
)


class AgentRouter:
    """Routes requests to appropriate agents and manages workflows"""
    
    def __init__(self, agent_system: AgentSystem):
        self.agent_system = agent_system
        self.logger = logging.getLogger("agent_router")
        
        # Initialize workflows
        self.workflows = {
            "task_creation": TaskCreationWorkflow(),
            "application_review": ApplicationReviewWorkflow(),
            "dispute_resolution": DisputeResolutionWorkflow()
        }
        
        self.logger.info("Agent router initialized with workflows")
    
    async def route_request(self, 
                          user_message: str, 
                          user_id: Optional[str] = None,
                          context: Optional[Dict[str, Any]] = None,
                          preferred_agent: Optional[str] = None,
                          workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Route a user request to appropriate agent or workflow"""
        
        try:
            if workflow_type and workflow_type in self.workflows:
                # Execute workflow
                return await self._execute_workflow(workflow_type, user_message, user_id, context)
            else:
                # Route to agent
                response = await self.agent_system.route_request(
                    user_message, user_id, context, preferred_agent
                )
                
                return {
                    "type": "agent_response",
                    "response": response,
                    "agent_used": "auto_routed",
                    "success": True
                }
                
        except Exception as e:
            self.logger.error(f"Error routing request: {e}")
            return {
                "type": "error",
                "error": str(e),
                "success": False
            }
    
    async def _execute_workflow(self, workflow_type: str, user_message: str, 
                              user_id: Optional[str] = None, 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific workflow"""
        
        workflow = self.workflows.get(workflow_type)
        if not workflow:
            return {
                "type": "error",
                "error": f"Unknown workflow type: {workflow_type}",
                "success": False
            }
        
        try:
            # Create initial workflow state
            if workflow_type == "task_creation":
                initial_state = workflow.create_task_workflow_state(
                    context.get("task_data", {}), user_id or "unknown"
                )
            elif workflow_type == "application_review":
                initial_state = workflow.create_application_review_state(
                    context.get("application_id", "unknown"),
                    user_id or "unknown"
                )
            elif workflow_type == "dispute_resolution":
                initial_state = workflow.create_dispute_resolution_state(
                    context.get("dispute_id", "unknown"),
                    user_id or "unknown",
                    context.get("dispute_type", "general"),
                    context.get("severity", "medium")
                )
            else:
                initial_state = workflow.create_initial_state(
                    context=context or {},
                    workflow_data={"user_id": user_id}
                )
            
            # Add user message to workflow state
            workflow.add_message(initial_state, "user", user_message, {"user_id": user_id})
            
            # Execute workflow
            result_state = await workflow.run(initial_state)
            
            # Extract workflow results
            workflow_summary = workflow.get_context(result_state, "final_summary", "Workflow completed")
            workflow_data = result_state.get("workflow_data", {})
            errors = workflow.get_errors(result_state)
            
            return {
                "type": "workflow_result",
                "workflow_type": workflow_type,
                "workflow_summary": workflow_summary,
                "workflow_data": workflow_data,
                "errors": errors,
                "success": not workflow.has_errors(result_state),
                "completed": workflow.get_context(result_state, "workflow_completed", False)
            }
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_type}: {e}")
            return {
                "type": "workflow_error",
                "workflow_type": workflow_type,
                "error": str(e),
                "success": False
            }
    
    def get_available_workflows(self) -> List[str]:
        """Get list of available workflow types"""
        return list(self.workflows.keys())
    
    def get_workflow_info(self, workflow_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific workflow"""
        workflow = self.workflows.get(workflow_type)
        if workflow:
            return workflow.get_workflow_info()
        return None
    
    async def execute_direct_agent_call(self, agent_id: str, message: str, 
                                      user_id: Optional[str] = None,
                                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a direct call to a specific agent"""
        
        agent = self.agent_system.get_agent(agent_id)
        if not agent:
            return {
                "type": "error",
                "error": f"Agent not found: {agent_id}",
                "success": False
            }
        
        try:
            response = await agent.process_message(message, user_id, context)
            
            return {
                "type": "direct_agent_response",
                "agent_id": agent_id,
                "response": response,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error in direct agent call to {agent_id}: {e}")
            return {
                "type": "error",
                "error": str(e),
                "success": False
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_status = self.agent_system.get_system_status()
        
        workflow_status = {}
        for workflow_type, workflow in self.workflows.items():
            workflow_status[workflow_type] = workflow.get_workflow_info()
        
        return {
            "agent_system": agent_status,
            "workflows": workflow_status,
            "router": {
                "status": "operational",
                "available_workflows": self.get_available_workflows()
            }
        }
    
    async def shutdown(self):
        """Shutdown the router and all components"""
        self.logger.info("Shutting down agent router...")
        
        # Shutdown workflows
        for workflow in self.workflows.values():
            try:
                await workflow.graph.aclose() if workflow.graph else None
            except Exception as e:
                self.logger.warning(f"Error closing workflow: {e}")
        
        # Shutdown agent system
        await self.agent_system.shutdown()
        
        self.logger.info("Agent router shutdown complete")
