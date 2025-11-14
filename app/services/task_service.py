from typing import Optional
from supabase import Client
from fastapi import HTTPException
import json

import asyncio
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskSearchRequest,
    TaskSearchResponse,
    TaskUpdate,
    TaskListResponse,
    TaskSearchListResponse,
    PublicTask,
    PublicTaskResponse,
    ClientInfo,
    GetZipCodesRequest,
    PublicTaskZipCodeResponse,
    PublicTaskZipCode,
)

import stripe


from app.schemas.sms import TaskCreationNotification
from app.services.stripe_service import StripeService
from app.utils.emailer import EmailUtils
from app.utils.sms import SMSUtils
from app.core.config import settings

class TaskService:
    """Service for handling task operations and business logic"""

    ENUM_LOCATION_TYPE = ["remote", "in_person"]

    def __init__(self, admin_client: Client, stripe_service: StripeService):
        self.admin_client = admin_client
        self.stripe_service = stripe_service
        self.emailer = EmailUtils()
        self.smser = SMSUtils()

    async def create_task(self, client_id: str, request: TaskCreate) -> TaskResponse:
        """Create a new task with validation"""
        try:
            # Check if user is a client            
            client = self.admin_client.table("clients").select("*").eq("id", client_id).execute()
            if not client.data:
                raise HTTPException(status_code=404, detail="Client not found")

            # Check if user has reached post limit
            client_posts_remaining = await self.stripe_service.get_client_posts_remaining(client_id)
            if client_posts_remaining < 1:
                raise HTTPException(
                    status_code=400, detail="Client has reached post limit."
                )

            task_payload = request.model_dump()
            task_payload["client_id"] = client_id

            # Create the task
            if request.location_type not in self.ENUM_LOCATION_TYPE:
                raise HTTPException(status_code=400, detail="Invalid location type, location type must be one of the following: " + ", ".join(self.ENUM_LOCATION_TYPE))
            
        
            result = self.admin_client.table("tasks").insert(task_payload).execute()
            

            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create task")

            # Update client's post count (fire and forget) and notify people
            asyncio.create_task(self.update_client_post_count(client_id))
            asyncio.create_task(self.emailer.send_task_notification_email(client.data[0]["email"], client.data[0]["first_name"], result.data[0]["title"], "task_created", result.data[0]["description"]))
            asyncio.create_task(self.emailer.send_task_notification_email(settings.EMAIL_SENDER, client.data[0]["first_name"], result.data[0]["title"], "task_created", result.data[0]["description"]))
            asyncio.create_task(self.smser.send_task_creation_notification(TaskCreationNotification(task_id=result.data[0]["id"], client_phone=client.data[0]["phone"], task_title=result.data[0]["title"], task_description=result.data[0]["description"])))
            # Return the created task
            created_task = result.data[0]
            return TaskResponse(**created_task)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create task: {str(e)}"
            )

    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """Get a single task by ID"""
        try:
            # create join with clients table
            result = self.admin_client.table("tasks").select("*, client:client_id (*)").eq("id", task_id).execute()
            if not result.data:
                return None

            return TaskResponse(**result.data[0])

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")

    async def update_task(
        self, task_id: str, user_id: str, request: TaskUpdate
    ) -> TaskResponse:
        """Update task (only client who created it can update)"""
        try:
            # Verify task exists and user owns it
            task = await self.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            if task.client_id != user_id:
                raise HTTPException(
                    status_code=403, detail="Only task owner can update task"
                )

            if task.completed_at is not None:
                raise HTTPException(
                    status_code=400, detail="Cannot update completed task"
                )

            # Update the task
            result = self.admin_client.table("tasks").update(request.model_dump()).eq("id", task_id).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to update task")

            # Return updated task
            updated_task = result.data[0]
            return TaskResponse(**updated_task)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to update task: {str(e)}"
            )

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete task (only client who created it can delete)"""
        try:
            # Verify task exists and user owns it
            task = await self.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            if task.client_id != user_id:
                raise HTTPException(
                    status_code=403, detail="Only task owner can delete task"
                )

            # Check if task can be deleted (not assigned/completed)
            if task.completed_at is not None:
                raise HTTPException(
                    status_code=400, detail="Cannot delete task in current status"
                )

            # Delete the task
            result = self.admin_client.table("tasks").delete().eq("id", task_id).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to delete task")

            return True

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete task: {str(e)}"
            )

    async def get_user_tasks(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> TaskListResponse:
        """Get tasks for a specific user (client)"""
        try:
            # Get total count

            count_result = (
                self.admin_client.table("tasks")
                .select("id", count="exact")
                .eq("client_id", user_id)
                .execute()
            )
            total_count = count_result.count if hasattr(count_result, "count") else 0

            # Get paginated tasks
            result = (
                self.admin_client.table("tasks")
                .select("*")
                .eq("client_id", user_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            tasks = []
            for task in result.data:
                tasks.append(TaskResponse(**task))

            return TaskListResponse(
                tasks=tasks, total_count=total_count, limit=limit, offset=offset
            )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get user tasks: {str(e)}"
            )

    async def search_tasks(
        self, search_request: TaskSearchRequest
    ) -> TaskSearchListResponse:
        """Search tasks with filters using efficient count and data queries"""
        try:
            search_request_dict = search_request.model_dump()
            print(search_request_dict)
            sort_by = search_request_dict.pop("sort_by", "post_date")
            print(sort_by)
            # Route to the correct SQL function based on sort_by
            if sort_by == "distance":
                result = self.admin_client.rpc(
                    "get_tasks_with_distance",
                    search_request_dict
                    ).execute()
            else:
                result = self.admin_client.rpc(
                    "get_tasks_by_post_date",
                    search_request_dict
                ).execute()

            if not result.data:
                return TaskSearchListResponse(
                    tasks=[],
                    limit=search_request.search_limit,
                    offset=search_request.search_offset,
                )

            
            # Convert to TaskSearchResponse objects
            tasks = [TaskSearchResponse(**task_data) for task_data in result.data]

            return TaskSearchListResponse(
                tasks=tasks,
                limit=search_request.search_limit,
                offset=search_request.search_offset,
            )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to search tasks: {str(e)}"
            )

    async def complete_task(self, task_id: str, user_id: str) -> TaskResponse:
        """Mark task as completed (only client can do this)"""
        try:
            # Verify task exists and belongs to client
            task = await self.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            if task.client_id != user_id:
                raise HTTPException(
                    status_code=403, detail="Only task owner can complete task"
                )

            if task.completed_at is not None:
                raise HTTPException(status_code=400, detail="Task already completed")

            # Update task status
            result = self.admin_client.table("tasks").update({
                "completed_at": "now()",
            }).eq("id", task_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to complete task")

            # Return updated task
            updated_task = result.data[0]
            return TaskResponse(**updated_task)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to complete task: {str(e)}"
            )

    async def update_client_post_count(self, client_id: str) -> None:
        """Update client's post count"""
        try:
            # First get the current count
            current_result = self.admin_client.table("clients").select("number_of_posts").eq("id", client_id).execute()
            
            if not current_result.data:
                raise HTTPException(status_code=404, detail="Client not found")
            
            current_count = current_result.data[0].get("number_of_posts", 0)
            new_count = current_count + 1
            
            # Update client's post count
            result = self.admin_client.table("clients").update({
                "number_of_posts": new_count
            }).eq("id", client_id).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=500, detail="Failed to update client post count"
                )

            return True

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to update client post count: {str(e)}"
            )

    async def get_available_tasks(self) -> Optional[PublicTaskResponse]:
        try:
            # query non sensitive information from tasks table
            result = (
                self.admin_client.table("tasks")
                .select(
                    "id, title, description, location_type, zip_code, hourly_rate, created_at, dates"
                )
                .is_("completed_at", None)
                .order("created_at", desc=True)
                .limit(20)
                .execute()
            )

            if not result or not result.data:
                return PublicTaskResponse(
                    result=[],
                    limit=20,
                    total_count=0,
                )

            tasks = [PublicTask(**task) for task in result.data]
            response = PublicTaskResponse(
                result=tasks,
                limit=20,
                total_count=len(tasks) if len(tasks) else 0,
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch available tasks: {str(e)}"
            )

    async def get_zip_codes(self, zip_codes: GetZipCodesRequest) -> Optional[PublicTaskZipCodeResponse]:
        try:
            # batch query all zip codes from request
            result = self.admin_client.table("zip_codes").select("*").in_("zip_code", zip_codes.zip_codes).execute()
            if not result.data:
                return PublicTaskZipCodeResponse(
                    result=[],
                    limit=len(zip_codes.zip_codes),
                    total_count=0,
                )

            zip_codes = [PublicTaskZipCode(**zip_code) for zip_code in result.data]
            response = PublicTaskZipCodeResponse(result=zip_codes)

            return response

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get zip codes: {str(e)}"
            )
    async def create_task_from_onetime_payment(self, payload: bytes, sig_header: str) -> TaskResponse:
        """Create a task from a one-time payment"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            client_id = event.data.object.metadata.user_id
            if not client_id:
                raise HTTPException(status_code=400, detail="Client ID is required")
            # Parse JSON string from metadata back to dict before creating TaskCreate
            task_payload = json.loads(event.data.object.metadata.task_data)
            task_payload["client_id"] = client_id
  
            result = self.admin_client.table("tasks").insert(task_payload).execute()
        
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create task")

            # Update client's post count (fire and forget)
            asyncio.create_task(self.update_client_post_count(client_id))
            asyncio.create_task(self.emailer.send_task_notification_email(client.data[0]["email"], client.data[0]["first_name"], result.data[0]["title"], "task_created", result.data[0]["description"]))
            asyncio.create_task(self.emailer.send_task_notification_email(settings.EMAIL_SENDER, client.data[0]["first_name"], result.data[0]["title"], "task_created", result.data[0]["description"]))
            asyncio.create_task(self.smser.send_task_creation_notification(TaskCreationNotification(task_id=result.data[0]["id"], client_phone=client.data[0]["phone"], task_title=result.data[0]["title"], task_description=result.data[0]["description"])))
            # Return the created task
            created_task = result.data[0]
            return TaskResponse(**created_task)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create task from one-time payment: {str(e)}")