from fastapi import APIRouter, Depends, HTTPException, status
from app.services.helper_service import HelperService
from app.schemas.helper import HelperSearchRequest, HelperListResponse, HelperResponse
from app.deps.supabase import get_helper_service

router = APIRouter()

@router.get("/search", response_model=HelperListResponse)
async def search_helpers(
    search_query: str = None,
    search_college: str = None,
    search_graduation_year: int = None,
    search_zip_code: str = None,
    limit: int = 20,
    offset: int = 0,
    helper_service: HelperService = Depends(get_helper_service),
) -> HelperListResponse:
    try:
        search_request = HelperSearchRequest(
            search_query=search_query,
            search_college=search_college,
            search_graduation_year=search_graduation_year,
            search_zip_code=search_zip_code,
            limit=limit,
            offset=offset
        )
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
