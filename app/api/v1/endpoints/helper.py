from fastapi import APIRouter, Depends, HTTPException, status
from app.services.helper_service import HelperService
from app.schemas.helper import HelperSearchRequest, HelperListResponse, HelperResponse
from app.deps.supabase import get_helper_service

router = APIRouter()

@router.get("/search", response_model=HelperListResponse)
async def search_helpers(
    search_request: HelperSearchRequest,
    helper_service: HelperService = Depends(get_helper_service),
) -> HelperListResponse:
    try:
        return await helper_service.search_helpers(search_request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{helper_id}", response_model=HelperResponse)
async def get_helper(
    helper_id: str,
    helper_service: HelperService = Depends(get_helper_service),
) -> HelperResponse:
    try:
        return await helper_service.get_helper(helper_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=HelperListResponse)
async def get_helpers(
    helper_service: HelperService = Depends(get_helper_service),
) -> HelperListResponse:
    try:
        return await helper_service.get_helpers()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
