"""Application tools for AI agents

This module provides comprehensive tools for AI agents to interact with the application
and invitation management system. It includes functions for creating, reading, updating,
and managing applications that helpers submit for tasks, as well as handling task
invitations sent to specific helpers. All functions are designed to work with LangChain's
tool system and return serializable JSON responses.
"""

from typing import Optional
from app.deps.supabase import get_application_service
from langchain_core.tools import tool
from app.schemas.applications import (
    ApplicationResponse, 
    ApplicationCreateRequest, 
    ApplicationListResponse
)
from app.schemas.invitations import (
    InvitationResponse, 
    InvitationListResponse
)
from fastapi import HTTPException

# Global service instance
application_service = get_application_service()
    
@tool
async def create_application(
        helper_id: str, 
        task_id: str, 
        introduction_message: str,
        supplements_url: Optional[str]) -> ApplicationResponse:
        """Create a new application for a helper to apply to a task.
        
        This function allows AI agents to create new applications on behalf of helpers
        who want to apply for specific tasks. The application includes an introduction
        message where helpers can explain why they're qualified and interested in the
        task, plus optional supplementary materials like portfolios or references.
        Applications are the primary way helpers express interest in tasks and clients
        evaluate potential candidates.
        
        Args:
            helper_id (str): The unique identifier of the helper submitting the application.
                            Must be a valid UUID string that exists in the system.
                            This helper will be the applicant for the specified task.
                            If the user is a helper, it will be the user's id.
            task_id (str): The unique identifier of the task the helper is applying for.
                          Must be a valid UUID string that exists in the system and
                          is currently open (not completed). Only open tasks accept
                          new applications.
            introduction_message (str): A compelling message from the helper explaining
                                      why they're interested in the task, their relevant
                                      experience, qualifications, and why they would be
                                      a good fit. This is the primary way helpers
                                      differentiate themselves and convince clients
                                      to choose them.
            supplements_url (Optional[str]): An optional URL to supplementary materials
                                            that support the helper's application.
                                            Examples include: portfolio websites,
                                            resume links, reference letters, work
                                            samples, or certifications. Can be null
                                            if no additional materials are provided.
        
        Returns:
            ApplicationResponse: A complete application object containing all the
                                created application details. Fields include:
                                - application (ApplicationInfo): Application details
                                - helper (HelperResponse): Helper information
                                - task (Optional[TaskResponse]): Task information
                                
                                ApplicationInfo includes:
                                - id (str): Unique application identifier
                                - task_id (str): ID of the task being applied to
                                - helper_id (str): ID of the helper applying
                                - introduction_message (str): Helper's introduction message
                                - supplements_url (Optional[str]): URL of supplementary materials
                                - created_at (datetime): Application creation timestamp
                                - updated_at (datetime): Last update timestamp
        
        Raises:
            HTTPException: Returns a 500 status code with error details if the
                          application creation fails due to validation errors,
                          database issues, duplicate applications, or other system
                          problems. Common errors include: helper already applied,
                          task not found, or task is no longer accepting applications.
        
        Example:
            >>> result = await create_application(
            ...     helper_id="helper-uuid-here",
            ...     task_id="task-uuid-here",
            ...     introduction_message="I have 3 years of experience moving furniture and would love to help with your moving task. I'm available on the dates you specified and have my own moving blankets.",
            ...     supplements_url="https://myportfolio.com/moving-experience"
            ... )
            >>> print(f"Application created with ID: {result.id}")
        """
        try:
            application_data = ApplicationCreateRequest(
                helper_id=helper_id,
                task_id=task_id,
                introduction_message=introduction_message,
                supplements_url=supplements_url
            )
            result = await application_service.create_application(helper_id, task_id, application_data)
            if not result:
                return HTTPException(status_code=500, detail="Failed to create application")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_application(application_id: str) -> ApplicationResponse:
        """Retrieve a single application by its unique identifier.
        
        This function fetches the complete details of a specific application from
        the database. It's useful for AI agents that need to examine application
        details, verify application information, retrieve application data for
        further processing, or display application details to users. 
        Application's aren't acceptable, the task poster does not accept or reject applications,
        only completes the task when they don't want to see any more applications.
        
        Args:
            application_id (str): The unique identifier of the application to retrieve.
                                 Must be a valid UUID string that exists in the system.
                                 This will return the complete application details
                                 including helper information and application status.
        
        Returns:
            ApplicationResponse: A complete application object containing all
                                application details. Fields include:
                                - application (ApplicationInfo): Application details
                                - helper (HelperResponse): Helper information
                                - task (Optional[TaskResponse]): Task information
                                
                                ApplicationInfo includes:
                                - id (str): Unique application identifier
                                - task_id (str): ID of the task being applied to
                                - helper_id (str): ID of the helper applying
                                - introduction_message (str): Helper's introduction message
                                - supplements_url (Optional[str]): URL of supplementary materials
                                - created_at (datetime): Application creation timestamp
                                - updated_at (datetime): Last update timestamp
        Raises:
            HTTPException: Returns a 404 status code if the application_id doesn't
                          exist in the system, or a 500 status code for other errors
                          like database connection issues or validation problems.
        
        Example:
            >>> application = await get_application("app-uuid-here")
            >>> print(f"Application Status: {application.status}")
            >>> print(f"Helper Message: {application.introduction_message}")
        """
        try:
            result = await application_service.get_application(application_id)
            if not result:
                return HTTPException(status_code=404, detail="Application not found")
            
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
    
    
@tool
async def get_task_applications(task_id: str) -> ApplicationListResponse:
        """Retrieve all applications submitted for a specific task.
        
        This function allows AI agents to fetch all applications that have been
        submitted for a particular task. This is useful for clients who want to
        review all applications for their task, AI agents helping with application
        evaluation, or administrators monitoring application activity. The function
        returns applications in a structured format with pagination support.
        
        Args:
            task_id (str): The unique identifier of the task to retrieve
                          applications for. Must be a valid UUID string that exists
                          in the system. This will return all applications
                          submitted for this specific task, regardless of status.
        
        Returns:
            ApplicationListResponse: A structured response containing a list of
                                    all applications for the specified task. Fields include:
                                    - applications (List[ApplicationResponse]): List of applications
                                    - total_count (int): Total number of applications for the task
                                    
                                    Each ApplicationResponse includes:
                                    - application (ApplicationInfo): Application details
                                    - helper (HelperResponse): Helper information
                                    - task (Optional[TaskResponse]): Task information
        
        Raises:
            HTTPException: Returns a 404 status code if the task_id doesn't exist
                          in the system, or a 500 status code for other errors
                          like database connection issues or validation problems.
        
        Example:
            >>> applications = await get_task_applications("task-uuid-here")
            >>> print(f"Total applications: {len(applications.applications)}")
            >>> for app in applications.applications:
            ...     print(f"Helper {app.helper_id}: {app.status}")
        """
        try:
            result = await application_service.get_task_applications(task_id)
            if not result:
                return HTTPException(status_code=404, detail="No applications found for this task")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_helper_applications(helper_id: str) -> ApplicationListResponse:
        """Retrieve all applications submitted by a specific helper.
        
        This function allows AI agents to fetch all applications that a particular
        helper has submitted across different tasks. This is useful for helpers
        who want to review their application history, AI agents helping with
        helper profile management, or administrators monitoring helper activity.
        The function provides a comprehensive view of a helper's application
        activity and success rates.
        
        Args:
            helper_id (str): The unique identifier of the helper whose applications
                            to retrieve. Must be a valid UUID string that exists
                            in the system. This will return all applications
                            submitted by this specific helper, regardless of status
                            or task. If the user is a helper, it will be the user's id.
        
        Returns:
            ApplicationListResponse: A structured response containing a list of
                                    all applications submitted by the specified
                                    helper. Fields include:
                                    - applications (List[ApplicationResponse]): List of applications
                                    - total_count (int): Total number of applications by the helper
                                    
                                    Each ApplicationResponse includes:
                                    - application (ApplicationInfo): Application details
                                    - helper (HelperResponse): Helper information
                                    - task (Optional[TaskResponse]): Task information
        
        Raises:
            HTTPException: Returns a 404 status code if the helper_id doesn't exist
                          in the system, or a 500 status code for other errors
                          like database connection issues or validation problems.
        
        Example:
            >>> helper_apps = await get_helper_applications("helper-uuid-here")
            >>> print(f"Helper has submitted {len(helper_apps.applications)} applications")
            >>> pending_apps = [app for app in helper_apps.applications if app.status == 'pending']
            >>> print(f"Pending applications: {len(pending_apps)}")
        """
        try:    
            result = await application_service.get_helper_applications(helper_id)
            if not result:
                return HTTPException(status_code=500, detail="Failed to get helper applications")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def invite_helper_to_task(task_id: str, helper_id: str) -> InvitationResponse:
        """Send a direct invitation to a specific helper for a task.
        
        This function allows AI agents to send direct invitations to specific
        helpers for tasks, inviting them to apply for the task. This is
        useful when clients want to proactively reach out to qualified helpers,
        when AI agents identify good matches between tasks and helpers. 
        Invitations can increase the likelihood of getting qualified helpers 
        for important or urgent tasks.
        
        Args:
            task_id (str): The unique identifier of the task to invite the
                          helper to. Must be a valid UUID string that exists
                          in the system and is currently open (not completed).
                          Only open tasks can have new invitations sent.
            helper_id (str): The unique identifier of the helper to invite
                            to the task. Must be a valid UUID string that
                            exists in the system. This helper will receive
                            a direct invitation to apply for the specified task.
        
        Returns:
            InvitationResponse: A complete invitation object containing all
                                the invitation details. Fields include:
                                - id (str): Unique invitation identifier
                                - task_id (str): ID of the task being invited to
                                - helper_id (str): ID of the helper being invited
                                - created_at (datetime): Invitation creation timestamp
                                - updated_at (datetime): Last update timestamp
                                - helpers (Optional[HelperResponse]): Helper information
                                - task (Optional[TaskResponse]): Task information
        
        Raises:
            HTTPException: Returns a 404 status code if the task_id or helper_id
                          doesn't exist in the system, a 400 status code if the
                          task is not open for invitations, or a 500 status code
                          for other system errors like database connection issues.
                          Common errors include: helper already invited, task not
                          found, or task is no longer accepting invitations.
        
        Example:
            >>> invitation = await invite_helper_to_task(
            ...     task_id="task-uuid-here",
            ...     helper_id="helper-uuid-here"
            ... )
            >>> print(f"Invitation sent with ID: {invitation.id}")
        """
        try:
            result = await application_service.invite_helper_to_task(task_id, helper_id)
            if not result:
                return HTTPException(status_code=500, detail="Failed to invite helper to task")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_task_invitations(task_id: str) -> InvitationListResponse:
        """Retrieve all invitations sent for a specific task.
        
        This function allows AI agents to fetch all invitations that have been
        sent for a particular task. This is useful for clients who want to see
        which helpers they've proactively invited, AI agents helping with
        invitation management, or administrators monitoring invitation activity.
        The function provides visibility into the proactive outreach efforts
        for a specific task.
        
        Args:
            task_id (str): The unique identifier of the task to retrieve
                          invitations for. Must be a valid UUID string that
                          exists in the system. This will return all invitations
                          sent for this specific task, regardless of status.
        
        Returns:
            InvitationListResponse: A structured response containing a list of
                                    all invitations sent for the specified task. Fields include:
                                    - invitations (List[InvitationResponse]): List of invitations
                                    - total_count (int): Total number of invitations for the task
                                    
                                    Each InvitationResponse includes:
                                    - id (str): Unique invitation identifier
                                    - task_id (str): ID of the task being invited to
                                    - helper_id (str): ID of the helper being invited
                                    - created_at (datetime): Invitation creation timestamp
                                    - updated_at (datetime): Last update timestamp
                                    - helpers (Optional[HelperResponse]): Helper information
                                    - task (Optional[TaskResponse]): Task information
        
        Raises:
            HTTPException: Returns a 404 status code if the task_id doesn't exist
                          in the system, or a 500 status code for other errors
                          like database connection issues or validation problems.
        
        Example:
            >>> invitations = await get_task_invitations("task-uuid-here")
            >>> print(f"Total invitations sent: {len(invitations.invitations)}")
            >>> accepted_invites = [inv for inv in invitations.invitations if inv.status == 'accepted']
            >>> print(f"Accepted invitations: {len(accepted_invites)}")
        """
        try:
            result = await application_service.get_task_invitations(task_id)
            if not result:
                return HTTPException(status_code=404, detail="No invitations found for this task")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_helper_invitations(helper_id: str) -> InvitationListResponse:
        """Retrieve all invitations received by a specific helper.
        
        This function allows AI agents to fetch all invitations that a particular
        helper has received across different tasks. This is useful for helpers
        who want to review their invitation history, AI agents helping with
        helper profile management, or administrators monitoring invitation activity.
        The function provides a comprehensive view of a helper's invitation
        activity and response rates.
        
        Args:
            helper_id (str): The unique identifier of the helper whose invitations
                            to retrieve. Must be a valid UUID string that exists
                            in the system. This will return all invitations
                            received by this specific helper, regardless of status
                            or task.
        
        Returns:
            InvitationListResponse: A structured response containing a list of
                                    all invitations received by the specified
                                    helper. Fields include:
                                    - invitations (List[InvitationResponse]): List of invitations
                                    - total_count (int): Total number of invitations received by the helper
                                    
                                    Each InvitationResponse includes:
                                    - id (str): Unique invitation identifier
                                    - task_id (str): ID of the task being invited to
                                    - helper_id (str): ID of the helper being invited
                                    - created_at (datetime): Invitation creation timestamp
                                    - updated_at (datetime): Last update timestamp
                                    - helpers (Optional[HelperResponse]): Helper information
                                    - task (Optional[TaskResponse]): Task information
        
        Raises:
            HTTPException: Returns a 404 status code if the helper_id doesn't exist
                          in the system, or a 500 status code for other errors
                          like database connection issues or validation problems.
        
        Example:
            >>> helper_invites = await get_helper_invitations("helper-uuid-here")
            >>> print(f"Helper has received {len(helper_invites.invitations)} invitations")
            >>> pending_invites = [inv for inv in helper_invites.invitations if inv.status == 'sent']
            >>> print(f"Pending invitations: {len(pending_invites)}")
        """
        try:
            result = await application_service.get_helper_invitations(helper_id)
            if not result:
                return HTTPException(status_code=404, detail="No invitations found for this helper")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
