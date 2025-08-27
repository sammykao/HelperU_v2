from fastapi import APIRouter, Depends, HTTPException, status
from app.deps.supabase import get_task_service
from app.services.task_service import TaskService
from app.schemas.task import (
    PublicTaskResponse,
)

router = APIRouter()


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
            detail=f"Failed to complete task: {str(e)}",
        )
