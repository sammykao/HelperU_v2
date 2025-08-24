"""
Application Review Workflow
Multi-step workflow for reviewing helper applications
"""
from typing import List, Dict, Any
from .base import BaseWorkflow, WorkflowState
from langgraph.graph import StateGraph, END


class ApplicationReviewWorkflow(BaseWorkflow):
    """Workflow for reviewing helper applications"""
    
    def __init__(self):
        super().__init__(
            name="Application Review Workflow",
            description="Multi-step workflow for reviewing helper applications"
        )
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each step
        workflow.add_node("fetch_application", self._fetch_application)
        workflow.add_node("evaluate_qualifications", self._evaluate_qualifications)
        workflow.add_node("check_references", self._check_references)
        workflow.add_node("make_decision", self._make_decision)
        workflow.add_node("notify_result", self._notify_result)
        
        # Define the workflow flow
        workflow.set_entry_point("fetch_application")
        workflow.add_edge("fetch_application", "evaluate_qualifications")
        workflow.add_edge("evaluate_qualifications", "check_references")
        workflow.add_edge("check_references", "make_decision")
        workflow.add_edge("make_decision", "notify_result")
        workflow.add_edge("notify_result", END)
        
        return workflow
    
    def get_workflow_steps(self) -> List[str]:
        """Get list of workflow steps"""
        return [
            "fetch_application",
            "evaluate_qualifications",
            "check_references", 
            "make_decision",
            "notify_result"
        ]
    
    async def _fetch_application(self, state: WorkflowState) -> WorkflowState:
        """Fetch application details"""
        self.set_current_step(state, "fetch_application")
        self.add_message(state, "system", "Fetching application details...")
        
        application_id = self.get_context(state, "application_id")
        if not application_id:
            self.add_error_handling(state, "No application ID provided")
            return state
        
        # Simulate fetching application
        self.add_workflow_data(state, "application_fetched", True)
        self.add_message(state, "system", "Application details retrieved successfully")
        
        return state
    
    async def _evaluate_qualifications(self, state: WorkflowState) -> WorkflowState:
        """Evaluate helper qualifications"""
        self.set_current_step(state, "evaluate_qualifications")
        self.add_message(state, "system", "Evaluating helper qualifications...")
        
        # Simulate qualification evaluation
        score = 85  # Mock score
        self.add_workflow_data(state, "qualification_score", score)
        self.add_message(state, "system", f"Qualification evaluation complete. Score: {score}/100")
        
        return state
    
    async def _check_references(self, state: WorkflowState) -> WorkflowState:
        """Check helper references"""
        self.set_current_step(state, "check_references")
        self.add_message(state, "system", "Checking helper references...")
        
        # Simulate reference checking
        references_verified = True
        self.add_workflow_data(state, "references_verified", references_verified)
        self.add_message(state, "system", "References verified successfully")
        
        return state
    
    async def _make_decision(self, state: WorkflowState) -> WorkflowState:
        """Make final decision on application"""
        self.set_current_step(state, "make_decision")
        self.add_message(state, "system", "Making final decision...")
        
        score = self.get_workflow_data(state, "qualification_score", 0)
        references_ok = self.get_workflow_data(state, "references_verified", False)
        
        if score >= 80 and references_ok:
            decision = "approved"
            self.add_message(state, "system", "Application approved")
        else:
            decision = "rejected"
            self.add_message(state, "system", "Application rejected")
        
        self.add_workflow_data(state, "decision", decision)
        
        return state
    
    async def _notify_result(self, state: WorkflowState) -> WorkflowState:
        """Notify helper of application result"""
        self.set_current_step(state, "notify_result")
        self.add_message(state, "system", "Notifying helper of result...")
        
        decision = self.get_workflow_data(state, "decision", "unknown")
        
        # Simulate notification
        notification_sent = True
        self.add_workflow_data(state, "notification_sent", notification_sent)
        
        summary = f"Application review workflow completed. Decision: {decision}"
        self.add_message(state, "system", summary)
        self.update_context(state, "workflow_completed", True)
        
        return state
    
    def create_application_review_state(self, application_id: str, reviewer_id: str) -> WorkflowState:
        """Create initial state for application review workflow"""
        return self.create_initial_state(
            context={
                "application_id": application_id,
                "reviewer_id": reviewer_id,
                "workflow_type": "application_review"
            },
            workflow_data={
                "start_time": "now",
                "reviewer_id": reviewer_id
            }
        )
