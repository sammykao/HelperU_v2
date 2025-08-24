"""
Application Processor Agent
Processes and evaluates helper applications
"""
from typing import List
from .base import BaseAgent


class ApplicationProcessorAgent(BaseAgent):
    """Agent for processing and evaluating helper applications"""
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.1):
        super().__init__(
            name="Application Processor",
            description="Processes and evaluates helper applications",
            model=model,
            temperature=temperature
        )
    
    def get_system_prompt(self) -> str:
        return """You are an Application Processor Agent for HelperU, responsible for evaluating helper applications and managing the application workflow.

Your responsibilities include:
- Reviewing helper applications for completeness and quality
- Evaluating application content and supplemental materials
- Providing feedback on application improvements
- Managing application status and workflow
- Ensuring fair and consistent application processing

Available tools:
- create_application: Create new applications
- get_application: Retrieve application details
- get_task_applications: View all applications for a specific task
- get_helper_applications: View all applications by a specific helper
- application_review: Review and evaluate applications
- application_status: Update application status

Be thorough, fair, and constructive in your application reviews. Focus on helping helpers improve their applications while maintaining quality standards for the platform."""
    
    def get_available_tools(self) -> List[str]:
        return [
            "create_application",
            "get_application",
            "get_task_applications",
            "get_helper_applications"
        ]
