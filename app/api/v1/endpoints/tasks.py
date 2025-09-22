from fastapi import APIRouter, Depends, HTTPException, status
from app.deps.supabase import get_current_user, get_task_service
from app.services.task_service import TaskService
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TaskListResponse,
    TaskSearchRequest,
    TaskSearchListResponse,
    PublicTaskResponse,
)
from app.schemas.auth import CurrentUser

router = APIRouter()


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: CurrentUser = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Create a new task (post) with subscription limit checking"""
    try:
        return await task_service.create_task(current_user.id, task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}",
        )


@router.get("/", response_model=TaskSearchListResponse)
async def get_tasks(
    search_zip_code: str,
    search_query: str = None,
    search_location_type: str = None,
    min_hourly_rate: float = None,
    max_hourly_rate: float = None,
    search_limit: int = 20,
    search_offset: int = 0,
    task_service: TaskService = Depends(get_task_service),
):
    """Get tasks with pagination, filtering, and distance-based sorting"""
    try:
        # Create TaskSearchRequest object from individual parameters
        search_request = TaskSearchRequest(
            search_zip_code=search_zip_code,
            search_query=search_query,
            search_location_type=search_location_type,
            min_hourly_rate=min_hourly_rate,
            max_hourly_rate=max_hourly_rate,
            search_limit=search_limit,
            search_offset=search_offset
        )
        return await task_service.search_tasks(search_request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}",
        )


@router.get("/fetch_available_tasks", response_model=PublicTaskResponse)
async def get_available_tasks(task_service: TaskService = Depends(get_task_service)):
    """Fetch available tasks for display"""
    try:
        return await task_service.get_available_tasks()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available tasks: {str(e)}",
        )


@router.get("/my-tasks", response_model=TaskListResponse)
async def get_my_tasks(
    current_user: CurrentUser = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    limit: int = 20,
    offset: int = 0,
):
    """Get current user's own tasks with pagination"""
    try:
        return await task_service.get_user_tasks(
            user_id=current_user.id, limit=limit, offset=offset
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}",
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, task_service: TaskService = Depends(get_task_service)):
    """Get a specific task by ID"""
    try:
        task = await task_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task: {str(e)}",
        )


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Delete a task (only by the creator)"""
    try:
        success = await task_service.delete_task(task_id, current_user.id)
        if success:
            return {"message": "Task deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}",
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Update a task (only by the creator)"""
    try:
        return await task_service.update_task(task_id, current_user.id, task_update)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}",
        )


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Mark a task as completed"""
    try:
        return await task_service.complete_task(task_id, current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}",
        )
