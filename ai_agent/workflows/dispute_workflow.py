"""
Dispute Resolution Workflow
Multi-step workflow for resolving user disputes
"""
from typing import List, Dict, Any
from .base import BaseWorkflow, WorkflowState
from langgraph.graph import StateGraph, END


class DisputeResolutionWorkflow(BaseWorkflow):
    """Workflow for resolving user disputes"""
    
    def __init__(self):
        super().__init__(
            name="Dispute Resolution Workflow",
            description="Multi-step workflow for resolving user disputes"
        )
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each step
        workflow.add_node("assess_dispute", self._assess_dispute)
        workflow.add_node("gather_evidence", self._gather_evidence)
        workflow.add_node("mediate_discussion", self._mediate_discussion)
        workflow.add_node("propose_resolution", self._propose_resolution)
        workflow.add_node("implement_resolution", self._implement_resolution)
        
        # Define the workflow flow
        workflow.set_entry_point("assess_dispute")
        workflow.add_edge("assess_dispute", "gather_evidence")
        workflow.add_edge("gather_evidence", "mediate_discussion")
        workflow.add_edge("mediate_discussion", "propose_resolution")
        workflow.add_edge("propose_resolution", "implement_resolution")
        workflow.add_edge("implement_resolution", END)
        
        return workflow
    
    def get_workflow_steps(self) -> List[str]:
        """Get list of workflow steps"""
        return [
            "assess_dispute",
            "gather_evidence",
            "mediate_discussion",
            "propose_resolution",
            "implement_resolution"
        ]
    
    async def _assess_dispute(self, state: WorkflowState) -> WorkflowState:
        """Assess the nature and severity of the dispute"""
        self.set_current_step(state, "assess_dispute")
        self.add_message(state, "system", "Assessing dispute...")
        
        dispute_type = self.get_context(state, "dispute_type", "general")
        severity = self.get_context(state, "severity", "medium")
        
        self.add_workflow_data(state, "dispute_assessed", True)
        self.add_workflow_data(state, "dispute_type", dispute_type)
        self.add_workflow_data(state, "severity", severity)
        
        self.add_message(state, "system", f"Dispute assessed: {dispute_type}, Severity: {severity}")
        
        return state
    
    async def _gather_evidence(self, state: WorkflowState) -> WorkflowState:
        """Gather relevant evidence and documentation"""
        self.set_current_step(state, "gather_evidence")
        self.add_message(state, "system", "Gathering evidence...")
        
        # Simulate evidence gathering
        evidence_collected = ["chat_logs", "payment_records", "user_testimonials"]
        self.add_workflow_data(state, "evidence_collected", evidence_collected)
        
        self.add_message(state, "system", f"Evidence collected: {', '.join(evidence_collected)}")
        
        return state
    
    async def _mediate_discussion(self, state: WorkflowState) -> WorkflowState:
        """Facilitate discussion between parties"""
        self.set_current_step(state, "mediate_discussion")
        self.add_message(state, "system", "Mediating discussion...")
        
        # Simulate mediation
        parties_communicated = True
        self.add_workflow_data(state, "parties_communicated", parties_communicated)
        
        self.add_message(state, "system", "Mediation discussion completed")
        
        return state
    
    async def _propose_resolution(self, state: WorkflowState) -> WorkflowState:
        """Propose resolution based on evidence and discussion"""
        self.set_current_step(state, "propose_resolution")
        self.add_message(state, "system", "Proposing resolution...")
        
        # Simulate resolution proposal
        resolution = "partial_refund"
        self.add_workflow_data(state, "proposed_resolution", resolution)
        
        self.add_message(state, "system", f"Resolution proposed: {resolution}")
        
        return state
    
    async def _implement_resolution(self, state: WorkflowState) -> WorkflowState:
        """Implement the proposed resolution"""
        self.set_current_step(state, "implement_resolution")
        self.add_message(state, "system", "Implementing resolution...")
        
        resolution = self.get_workflow_data(state, "proposed_resolution", "unknown")
        
        # Simulate resolution implementation
        resolution_implemented = True
        self.add_workflow_data(state, "resolution_implemented", resolution_implemented)
        
        summary = f"Dispute resolution workflow completed. Resolution: {resolution}"
        self.add_message(state, "system", summary)
        self.update_context(state, "workflow_completed", True)
        
        return state
    
    def create_dispute_resolution_state(self, dispute_id: str, mediator_id: str, 
                                      dispute_type: str, severity: str) -> WorkflowState:
        """Create initial state for dispute resolution workflow"""
        return self.create_initial_state(
            context={
                "dispute_id": dispute_id,
                "mediator_id": mediator_id,
                "dispute_type": dispute_type,
                "severity": severity,
                "workflow_type": "dispute_resolution"
            },
            workflow_data={
                "start_time": "now",
                "mediator_id": mediator_id
            }
        )
