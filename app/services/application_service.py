from supabase import Client
from app.schemas.applications import (
    ApplicationInfo,
    ApplicationResponse,
    ApplicationCreateRequest,
    ApplicationListResponse
)
from app.schemas.helper import HelperResponse
from app.schemas.sms import ApplicationReceivedNotification, InvitationNotification
from app.schemas.invitations import InvitationResponse, InvitationListResponse
from app.services.task_service import TaskService, TaskResponse
from app.services.helper_service import HelperService
from fastapi import HTTPException, status
from typing import List
import asyncio
from app.utils.sms import SMSUtils


class ApplicationService:
    def __init__(self, admin_client: Client, task_service: TaskService, helper_service: HelperService):
        self.admin_client = admin_client
        self.task_service = task_service
        self.helper_service = helper_service
        self.smser = SMSUtils()


    async def get_applications_by_task(self, user_id: str, task_id: str) -> ApplicationListResponse:
        """Get applications by task id and user id"""
        try:
            # Check if the task exists and belongs to the user
            task = await self.task_service.get_task(task_id)
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
            if task.client_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this task")
            
            # Get the applications for the task using embedded relation
            applications_result = self.admin_client.table("applications")\
                .select(
                    "*",
                    "helpers:helper_id (*)"
                )\
                .eq("task_id", task_id).execute()

            if not applications_result.data:
                return ApplicationListResponse(applications=[], total_count=0)
            
            applications = [
                ApplicationResponse(
                    application=ApplicationInfo(**application), 
                    helper=HelperResponse(**application["helpers"])
                )
                for application in applications_result.data
            ]
            return ApplicationListResponse(applications=applications, total_count=len(applications))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_applications_by_client(self, user_id: str, limit: int = 20, offset: int = 0) -> ApplicationListResponse:
        """Get all applications for the tasks of the current client user"""
        try:
            tasks = await self.task_service.get_user_tasks(user_id, limit, offset)
            if not tasks:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found")

            applications = []
            for task in tasks:
                applications_result = await self.get_applications_by_task(user_id, task.id)
                applications.extend(applications_result.applications)

            return ApplicationListResponse(applications=applications, total_count=len(applications))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_applications_by_helper(self, helper_id: str) -> ApplicationListResponse:
         
        """Get all applications submitted by the current helper user"""
        try:

            # Join statement for tasks and applications
            applications_result = (self.admin_client
                .table("applications")
                .select("*, tasks:task_id (*, client:client_id (*))")
                .eq("helper_id", helper_id)
                .execute()
            )

            print(applications_result)
            if not applications_result.data:
                return ApplicationListResponse(applications=[], total_count=0)

            
            helper = await self.helper_service.get_helper(helper_id)
            applications = [
                ApplicationResponse(
                    application=ApplicationInfo(**application), 
                    helper=helper,
                    task=TaskResponse(**application["tasks"])
                )
                for application in applications_result.data
            ]
            return ApplicationListResponse(applications=applications, total_count=len(applications))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    async def create_application(self, helper_id: str, task_id: str, application_create_request: ApplicationCreateRequest) -> ApplicationResponse:
        """Create an application for the current helper user"""
        try:
            # Check if the task exists
            task = await self.task_service.get_task(task_id)
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
            
            helper = await self.helper_service.get_helper(helper_id)
            if not helper:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Helper not found")
            
            # Check if the helper has already applied to the task
            applications_result = self.admin_client.table("applications").select("*").eq("helper_id", helper_id).eq("task_id", task_id).execute()
            if applications_result.data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already applied to this task")
            
            # Create the application with helper_id from authenticated user
            application = self.admin_client.table("applications").insert({
                "task_id": application_create_request.task_id,
                "helper_id": helper_id,
                "introduction_message": application_create_request.introduction_message,
                "supplements_url": application_create_request.supplements_url
            }).execute()
            if not application.data:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create application")
            
            # Update helper's application count (fire and forget)
            asyncio.create_task(self.update_helper_application_count(helper_id))
            asyncio.create_task(self.send_application_received_notification(client_id=task.client_id, helper_name=helper.first_name + " " + helper.last_name, task_title=task.title))
            # Return the application    
            return ApplicationResponse(
                application=ApplicationInfo(**application.data[0]),
                helper=helper
            )

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    async def update_helper_application_count(self, helper_id: str) -> bool:
        """Update helper's total application count (fire and forget)"""
        try:
            result = self.admin_client.rpc("increment_helper_application_count", {"helper_uuid": helper_id}).execute()
            if not result.data:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update helper application count")
            return True
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    async def get_application(self, application_id: str) -> ApplicationResponse:
        """Get an application by id"""
        try:
            application_result = self.admin_client\
                .table("applications")\
                .select(
                    "*",
                    "helpers:helper_id (*)"
                )\
                .eq("id", application_id)\
                .single()\
                .execute()

            if not application_result.data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
            return ApplicationResponse(
                application=ApplicationInfo(**application_result.data[0]), 
                helper=HelperResponse(**application_result.data[0]["helpers"])
            )
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


    async def get_invitations_by_task(self, user_id: str, task_id: str) -> InvitationListResponse:
        """Get all invitations for a task"""
        try:
            # Check if the task exists
            task = await self.task_service.get_task(task_id)
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
            if task.client_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this task")
            
            # Get all invitations for the task with helper information
            invitations_result = self.admin_client.table("invitations").select("*, helpers:helper_id(*)").eq("task_id", task_id).execute()
            if not invitations_result.data:
                return InvitationListResponse(invitations=[], total_count=0)

            invitations = [InvitationResponse(**invitation) for invitation in invitations_result.data]
            return InvitationListResponse(invitations=invitations, total_count=len(invitations))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    async def get_invitations_by_helper(self, helper_id: str) -> InvitationListResponse:
        """Get all invitations for a helper"""
        try:
            # Check if the helper exists
            helper = await self.helper_service.get_helper(helper_id)
            if not helper:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Helper not found")
            
            # Get all invitations for the helper, join statement for tasks and invitations
            invitations_result = (
                self.admin_client
                    .table("invitations")
                    .select("*, tasks:task_id (*, client:client_id (*))")
                    .eq("helper_id", helper_id)
                    .execute()
                )

            if not invitations_result.data:
                return InvitationListResponse(invitations=[], total_count=0)
            
            invitations = []
            for invitation in invitations_result.data:
                invitations.append(InvitationResponse(**invitation, task=TaskResponse(**invitation["tasks"])))
            
            return InvitationListResponse(invitations=invitations, total_count=len(invitations))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def invite_helper_to_task(self, user_id: str, task_id: str, helper_id: str) -> InvitationResponse:
        """Invite a helper to a task"""
        try:
            # Check if the task exists
            task = await self.task_service.get_task(task_id)
            if not task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
            if task.client_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this task")
            
            # Check if the helper has already been invited to the task
            invitations_result = self.admin_client.table("invitations").select("*").eq("task_id", task_id).eq("helper_id", helper_id).execute()
            if invitations_result.data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Helper has already been invited to this task")
            
            # Create the invitation
            invitation = self.admin_client.table("invitations").insert({
                "task_id": task_id,
                "helper_id": helper_id
            }).execute()
            if not invitation.data:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create invitation")
            
            asyncio.create_task(self.send_invitation_notification(client_id=task.client_id, helper_id=helper_id, task_title=task.title))
            # Return the invitation
            return InvitationResponse(**invitation.data[0])
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    async def send_application_received_notification(self, client_id: str, helper_name: str, task_title: str) -> None:
        """Send application received notification"""
        client = self.admin_client.table("clients").select("*").eq("id", client_id).execute()
        if not client.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        await self.smser.send_application_received_notification(ApplicationReceivedNotification(client_phone=client.data[0]["phone"], helper_name=helper_name, task_title=task_title))
    
    async def send_invitation_notification(self, client_id: str, helper_id: str, task_title: str) -> None:
        """Send invitation notification"""
        #create a client helper join request
        client = self.admin_client.table("clients").select("*").eq("id", client_id).execute()
        helper = self.admin_client.table("helpers").select("*").eq("id", helper_id).execute()
        if not client.data or not helper.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        await self.smser.send_invitation_notification(InvitationNotification(client_name=client.data[0]["first_name"] + " " + client.data[0]["last_name"], helper_phone=helper.data[0]["phone"], task_title=task_title))

# from supabase import Client
# from app.schemas.applications import (
#     ApplicationInfo,
#     ApplicationResponse,
#     ApplicationCreateRequest,
#     ApplicationListResponse,
# )
# from app.schemas.helper import HelperResponse
# from app.schemas.invitations import InvitationResponse, InvitationListResponse
# from app.services.task_service import TaskService, TaskResponse
# from app.services.helper_service import HelperService
# from fastapi import HTTPException, status
# from typing import List
# import asyncio


# class ApplicationService:
#     def __init__(
#         self,
#         admin_client: Client,
#         task_service: TaskService,
#         helper_service: HelperService,
#     ):
#         self.admin_client = admin_client
#         self.task_service = task_service
#         self.helper_service = helper_service

#     async def get_applications_by_task(
#         self, user_id: str, task_id: str
#     ) -> ApplicationListResponse:
#         """Get applications by task id and user id"""
#         try:
#             # Check if the task exists and belongs to the user
#             task = await self.task_service.get_task(task_id)
#             if not task:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
#                 )
#             if task.client_id != user_id:
# <<<<<<< notifications
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You are not the owner of this task",
#                 )

#             # Get the applications for the task
#             # applications_result = (
#             #     self.admin_client.table("applications")
#             #     .join("helpers", "helpers.id = applications.helper_id")
#             #     .select("applications.*, helpers.*")
#             #     .eq("task_id", task_id)
#             #     .execute()
#             # )

#             applications_result = (
#                 self.admin_client.table("applications")
#                 .select(
#                     "id, task_id, helper_id, introduction_message, supplements_url, created_at, updated_at, helpers(*)"
#                 )
#                 .eq("task_id", task_id)
#                 .execute()
#             )

#             if not applications_result.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="No applications found",
#                 )

# =======
#                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this task")
            
#             # Get the applications for the task using embedded relation
#             applications_result = self.admin_client.table("applications")\
#                 .select(
#                     "*",
#                     "helpers:helper_id (*)"
#                 )\
#                 .eq("task_id", task_id).execute()

#             if not applications_result.data:
#                 return ApplicationListResponse(applications=[], total_count=0)
            
# >>>>>>> main
#             applications = [
#                 ApplicationResponse(
#                     application=ApplicationInfo(
#                         **{k: v for k, v in application.items() if k != "helpers"}
#                     ),
#                     helper=(
#                         HelperResponse(**application["helpers"])
#                         if application.get("helpers")
#                         else None
#                     ),
#                 )
#                 for application in applications_result.data
#             ]

#             # applications = [
#             #     ApplicationResponse(
#             #         application=ApplicationInfo(**application),
#             #         helper=HelperResponse(**application["helpers"]),
#             #     )
#             #     for application in applications_result.data
#             # ]
#             return ApplicationListResponse(
#                 applications=applications, total_count=len(applications)
#             )
#         except Exception as e:
#             print(e)
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#             )

#     async def get_applications_by_client(
#         self, user_id: str, limit: int = 20, offset: int = 0
#     ) -> ApplicationListResponse:
#         """Get all applications for the tasks of the current client user"""
#         try:
#             tasks = await self.task_service.get_user_tasks(user_id, limit, offset)
#             if not tasks:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found"
#                 )

#             applications = []
#             for task in tasks:
#                 applications_result = await self.get_applications_by_task(
#                     user_id, task.id
#                 )
#                 applications.extend(applications_result.applications)

#             return ApplicationListResponse(
#                 applications=applications, total_count=len(applications)
#             )
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#             )

# <<<<<<< notifications
#     async def get_applications_by_helper(
#         self, helper_id: str
#     ) -> List[ApplicationResponse]:
#         """Get all applications for the tasks of the current helper user"""
#         try:
#             applications_result = (
#                 self.admin_client.table("applications")
#                 .select("*")
#                 .eq("helper_id", helper_id)
#                 .execute()
#             )
#             if not applications_result.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="No applications found",
#                 )

#             helper = await self.helper_service.get_helper(helper_id)
#             applications = [
#                 ApplicationResponse(
#                     application=ApplicationInfo(**application), helper=helper
# =======
#     async def get_applications_by_helper(self, helper_id: str) -> ApplicationListResponse:
#         """Get all applications submitted by the current helper user"""
#         try:

#             # Join statement for tasks and applications
#             applications_result = self.admin_client.table("applications").select("*, tasks:task_id (*)").eq("helper_id", helper_id).execute()
#             if not applications_result.data:
#                 return ApplicationListResponse(applications=[], total_count=0)
            
#             helper = await self.helper_service.get_helper(helper_id)
#             applications = [
#                 ApplicationResponse(
#                     application=ApplicationInfo(**application), 
#                     helper=helper,
#                     task=TaskResponse(**application["tasks"])
# >>>>>>> main
#                 )
#                 for application in applications_result.data
#             ]
#             return ApplicationListResponse(
#                 applications=applications, total_count=len(applications)
#             )
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#             )

#     async def create_application(
#         self,
#         helper_id: str,
#         task_id: str,
#         application_create_request: ApplicationCreateRequest,
#     ) -> ApplicationResponse:
#         """Create an application for the current helper user"""
#         try:
#             # Check if the task exists
#             task = await self.task_service.get_task(task_id)
#             if not task:
# <<<<<<< notifications
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
#                 )

#             helper = (
#                 self.admin_client.table("helpers")
#                 .select("*")
#                 .eq("id", helper_id)
#                 .execute()
#             )
#             if not helper.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail="Helper not found"
#                 )

# =======
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
            
#             helper = await self.helper_service.get_helper(helper_id)
#             if not helper:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Helper not found")
            
# >>>>>>> main
#             # Check if the helper has already applied to the task
#             applications_result = (
#                 self.admin_client.table("applications")
#                 .select("*")
#                 .eq("helper_id", helper_id)
#                 .eq("task_id", task_id)
#                 .execute()
#             )
#             if applications_result.data:
# <<<<<<< notifications
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="You have already applied to this task",
#                 )

#             # Create the application
#             application = (
#                 self.admin_client.table("applications")
#                 .insert(application_create_request.model_dump())
#                 .execute()
#             )
# =======
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already applied to this task")
            
#             # Create the application with helper_id from authenticated user
#             application_data = {
#                 "task_id": application_create_request.task_id,
#                 "helper_id": helper_id,
#                 "introduction_message": application_create_request.introduction_message,
#                 "supplements_url": application_create_request.supplements_url
#             }
#             application = self.admin_client.table("applications").insert(application_data).execute()
# >>>>>>> main
#             if not application.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail="Failed to create application",
#                 )

#             # Update helper's application count (fire and forget)
#             asyncio.create_task(self.update_helper_application_count(helper_id))
# <<<<<<< notifications

#             application_row = application.data[0]
#             helper_row = helper.data[0]

#             return ApplicationResponse(
#                 application=ApplicationInfo(**application_row),
#                 helper=HelperResponse(**helper_row),
#             )
#             # Return the application
#             # return ApplicationResponse(**application.data[0])
# =======
            
#             # Return the application    
#             return ApplicationResponse(
#                 application=ApplicationInfo(**application.data[0]),
#                 helper=helper
#             )
# >>>>>>> main

#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#             )

#     async def update_helper_application_count(self, helper_id: str) -> bool:
#         """Update helper's total application count (fire and forget)"""
#         try:
#             result = self.admin_client.rpc(
#                 "increment_helper_application_count", {"helper_uuid": helper_id}
#             ).execute()
#             if not result.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail="Failed to update helper application count",
#                 )
#             return True
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#             )

#     async def get_application(self, application_id: str) -> ApplicationResponse:
#         """Get an application by id"""
#         try:
# <<<<<<< notifications
#             application_result = (
#                 self.admin_client.table("applications")
#                 .join("helpers", "helpers.id = applications.helper_id")
#                 .select("applications.*, helpers.*")
#                 .eq("id", application_id)
#                 .execute()
#             )
# =======
#             application_result = self.admin_client\
#                 .table("applications")\
#                 .select(
#                     "*",
#                     "helpers:helper_id (*)"
#                 )\
#                 .eq("id", application_id)\
#                 .single()\
#                 .execute()
# >>>>>>> main

#             if not application_result.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="Application not found",
#                 )

#             return ApplicationResponse(
#                 application=ApplicationInfo(**application_result.data[0]),
#                 helper=HelperResponse(**application_result.data[0]["helpers"]),
#             )
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#             )

#     async def get_invitations_by_task(
#         self, user_id: str, task_id: str
#     ) -> InvitationListResponse:
#         """Get all invitations for a task"""
#         try:
#             # Check if the task exists
#             task = await self.task_service.get_task(task_id)
#             if not task:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
#                 )
#             if task.client_id != user_id:
# <<<<<<< notifications
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You are not the owner of this task",
#                 )

#             # Get all invitations for the task
#             invitations_result = (
#                 self.admin_client.table("invitations")
#                 .select("*")
#                 .eq("task_id", task_id)
#                 .execute()
#             )
#             if not invitations_result.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail="No invitations found"
#                 )

#             invitations = [
#                 InvitationResponse(**invitation)
#                 for invitation in invitations_result.data
#             ]
#             return InvitationListResponse(
#                 invitations=invitations, total_count=len(invitations)
#             )
# =======
#                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this task")
            
#             # Get all invitations for the task with helper information
#             invitations_result = self.admin_client.table("invitations").select("*, helpers:helper_id(*)").eq("task_id", task_id).execute()
#             if not invitations_result.data:
#                 return InvitationListResponse(invitations=[], total_count=0)
            
#             invitations = [InvitationResponse(**invitation) for invitation in invitations_result.data]
#             return InvitationListResponse(invitations=invitations, total_count=len(invitations))
# >>>>>>> main
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#             )

#     async def get_invitations_by_helper(self, helper_id: str) -> InvitationListResponse:
#         """Get all invitations for a helper"""
#         try:
#             # Check if the helper exists
#             helper = await self.helper_service.get_helper(helper_id)
#             if not helper:
# <<<<<<< notifications
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail="Helper not found"
#                 )

#             # Get all invitations for the helper
#             invitations_result = (
#                 self.admin_client.table("invitations")
#                 .select("*")
#                 .eq("helper_id", helper_id)
#                 .execute()
#             )
#             if not invitations_result.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail="No invitations found"
#                 )

#             invitations = [
#                 InvitationResponse(**invitation)
#                 for invitation in invitations_result.data
#             ]
#             return InvitationListResponse(
#                 invitations=invitations, total_count=len(invitations)
#             )
# =======
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Helper not found")
            
#             # Get all invitations for the helper, join statement for tasks and invitations
#             invitations_result = self.admin_client.table("invitations").select("*, tasks:task_id (*)").eq("helper_id", helper_id).execute()
#             if not invitations_result.data:
#                 return InvitationListResponse(invitations=[], total_count=0)
            
#             invitations = []
#             for invitation in invitations_result.data:
#                 invitations.append(InvitationResponse(**invitation, task=TaskResponse(**invitation["tasks"])))
            
#             return InvitationListResponse(invitations=invitations, total_count=len(invitations))
# >>>>>>> main
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#             )

#     async def invite_helper_to_task(
#         self, user_id: str, task_id: str, helper_id: str
#     ) -> InvitationResponse:
#         """Invite a helper to a task"""
#         try:
#             # Check if the task exists
#             task = await self.task_service.get_task(task_id)
#             if not task:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
#                 )
#             if task.client_id != user_id:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="You are not the owner of this task",
#                 )

#             # Check if the helper has already been invited to the task
#             invitations_result = (
#                 self.admin_client.table("invitations")
#                 .select("*")
#                 .eq("task_id", task_id)
#                 .eq("helper_id", helper_id)
#                 .execute()
#             )
#             if invitations_result.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Helper has already been invited to this task",
#                 )

#             # Create the invitation
#             invitation = (
#                 self.admin_client.table("invitations")
#                 .insert({"task_id": task_id, "helper_id": helper_id})
#                 .execute()
#             )
#             if not invitation.data:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail="Failed to create invitation",
#                 )

#             # Return the invitation
#             return InvitationResponse(**invitation.data[0])
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#             )

