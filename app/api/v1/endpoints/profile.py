from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.deps.supabase import get_current_user, get_profile_service
from app.services.profile_service import ProfileService
from app.schemas.auth import ClientProfileUpdateRequest, HelperProfileUpdateRequest

router = APIRouter()
security = HTTPBearer()


@router.get("/")
async def get_user_profile(
    current_user: str = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Get current user's profile"""
    try:
        profile_status = await profile_service.get_user_profile_status(current_user.id)

        if profile_status.user_type == "client":
            profile = { "client": await profile_service.get_client_profile(current_user.id) }
        elif profile_status.user_type == "helper":
            profile = { "helper": await profile_service.get_helper_profile(current_user.id) }
        else:
            # Both user types; no concrete profile to return
            profile = { 
                "client": await profile_service.get_client_profile(current_user.id) or None, 
                "helper": await profile_service.get_helper_profile(current_user.id) or Nonex    
            }

        return {
            "success": True,
            "profile_status": profile_status.model_dump(),
            "profile": profile,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}",
        )


@router.put("/client")
async def update_client_profile(
    request: ClientProfileUpdateRequest,
    current_user: str = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Update client profile"""
    try:
        # Verify user is actually a client
        profile_status = await profile_service.get_user_profile_status(current_user.id)
        if profile_status.user_type != "client":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only clients can update client profiles",
            )

        pfp_url = request.pfp_url or None
        profile_data = ProfileUpdateData(
            first_name=request.first_name,
            last_name=request.last_name,
            pfp_url=pfp_url,
        )

        result = await profile_service.update_client_profile(
            current_user.id, profile_data
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}",
        )


@router.put("/helper")
async def update_helper_profile(
    request: HelperProfileUpdateRequest,
    current_user: str = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Update helper profile"""
    try:
        # Verify user is actually a helper
        profile_status = await profile_service.get_user_profile_status(current_user.id)
        if profile_status.user_type != "helper":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only helpers can update helper profiles",
            )
        pfp_url = request.pfp_url or None

        profile_data = ProfileUpdateData(
            first_name=request.first_name,
            last_name=request.last_name,
            college=request.college,
            bio=request.bio,
            graduation_year=request.graduation_year,
            zip_code=request.zip_code,
            pfp_url=pfp_url,
        )

        result = await profile_service.update_helper_profile(
            current_user.id, profile_data
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}",
        )


@router.get("/status")
async def get_profile_status(
    current_user: str = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    """Get current user's profile completion status"""
    try:
        profile_status = await profile_service.get_user_profile_status(current_user.id)
        return {"success": True, "profile_status": profile_status.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile status: {str(e)}",
        )


@router.post("/delete-profile")
async def delete_profile(
    current_user: str = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
):
    try:
        await profile_service.delete_profile(current_user.id)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}",
        )
