from fastapi import APIRouter, Depends, HTTPException, status
from app.deps.supabase import get_current_user, get_application_service
from app.services.application_service import ApplicationService
from app.schemas.applications import (
    ApplicationCreateRequest,
    ApplicationCreateData,
    ApplicationResponse,
    ApplicationListResponse,
)
from app.schemas.invitations import InvitationResponse, InvitationListResponse
from app.schemas.auth import CurrentUser

router = APIRouter()


@router.get("/task/{task_id}", response_model=ApplicationListResponse)
async def get_applications_by_task(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Get all applications for a specific task (only task owner can view)"""
    try:
        return await application_service.get_applications_by_task(
            current_user.id, task_id
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get applications: {str(e)}",
        )


@router.get("/client", response_model=ApplicationListResponse)
async def get_applications_by_client(
    current_user: CurrentUser = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
    limit: int = 20,
    offset: int = 0,
):
    """Get all applications for tasks owned by the current client user"""
    try:
        return await application_service.get_applications_by_client(
            current_user.id, limit, offset
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get client applications: {str(e)}",
        )


@router.get("/helper", response_model=ApplicationListResponse)
async def get_applications_by_helper(
    current_user: CurrentUser = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Get all applications submitted by the current helper user"""
    try:
        return await application_service.get_applications_by_helper(current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get helper applications: {str(e)}",
        )

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application_data: ApplicationCreateData,
    current_user: CurrentUser = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service)
):
    """Create a new application for a task (only helpers can apply)"""
    try:
        # Construct the full request with task_id from the request body
        application_create_request = ApplicationCreateRequest(
            task_id=application_data.task_id,
            helper_id=current_user.id,
            introduction_message=application_data.introduction_message,
            supplements_url=application_data.supplements_url
        )
        
        return await application_service.create_application(
            current_user.id, 
            application_create_request.task_id, 
            application_create_request
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )
        
# @router.post("/", response_model=ApplicationResponse)
# async def create_application(
# <<<<<<< notifications
#     # task_id: str,
#     application_create_request: ApplicationCreateRequest,
# =======
#     application_data: ApplicationCreateData,
# >>>>>>> main
#     current_user: CurrentUser = Depends(get_current_user),
#     application_service: ApplicationService = Depends(get_application_service),
# ):
#     """Create a new application for a task (only helpers can apply)"""
#     try:
# <<<<<<< notifications
#         print(application_create_request)
#         return await application_service.create_application(
#             current_user.id,
#             application_create_request.task_id,
#             application_create_request,
# =======
#         # Construct the full request with task_id from the request body
#         application_create_request = ApplicationCreateRequest(
#             task_id=application_data.task_id,
#             helper_id=current_user.id,
#             introduction_message=application_data.introduction_message,
#             supplements_url=application_data.supplements_url
#         )
        
#         return await application_service.create_application(
#             current_user.id, 
#             application_create_request.task_id, 
#             application_create_request
# >>>>>>> main
#         )
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to create application: {str(e)}",
#         )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Get a specific application by ID"""
    try:
        return await application_service.get_application(application_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get application: {str(e)}",
        )


# Invitation endpoints


@router.get("/task/{task_id}/invitations", response_model=InvitationListResponse)
async def get_invitations_by_task(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Get all invitations for a specific task (only task owner can view)"""
    try:
        return await application_service.get_invitations_by_task(
            current_user.id, task_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task invitations: {str(e)}",
        )


@router.get("/helper/invitations", response_model=InvitationListResponse)
async def get_invitations_by_helper(
    current_user: CurrentUser = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Get all invitations received by the current helper user"""
    try:
        return await application_service.get_invitations_by_helper(current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get helper invitations: {str(e)}",
        )


@router.post("/task/{task_id}/invite/{helper_id}", response_model=InvitationResponse)
async def invite_helper_to_task(
    task_id: str,
    helper_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    application_service: ApplicationService = Depends(get_application_service),
):
    """Invite a helper to a task (only task owner can invite)"""
    try:
        return await application_service.invite_helper_to_task(
            current_user.id, task_id, helper_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invite helper: {str(e)}",
        )
