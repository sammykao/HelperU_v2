from supabase import Client
from fastapi import HTTPException, status
from app.schemas.helper import HelperResponse, HelperListResponse, HelperSearchRequest

class HelperService:

    def __init__(self, admin_client: Client):
        self.admin_client = admin_client
        ## Keep these fields out of the response, but make sure this is synced with HelperResponse schema
        self.exclude_fields = ["phone_number", "email", "number_of_applications", "invited_count", "created_at", "updated_at"]

    async def get_helper(self, helper_id: str) -> HelperResponse:
        """Get a helper by id"""
        try:
            helper_result = self.admin_client.table("helpers").select("*").eq("id", helper_id).execute()
            if not helper_result.data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Helper not found")
            
            helper_data = helper_result.data[0]
            return HelperResponse(**helper_data)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_helpers(self, limit: int = 20, offset: int = 0) -> HelperListResponse:
        try:
            helpers_result = self.admin_client.table("helpers").select("*").limit(limit).offset(offset).execute()
            if not helpers_result.data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No helpers found")
            
            helpers = [HelperResponse(**helper) for helper in helpers_result.data]
            return HelperListResponse(helpers=helpers, total_count=len(helpers))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def search_helpers(self, search_request: HelperSearchRequest) -> HelperListResponse:
        try:
            # Map parameters to match database function signature
            count_params = {
                "search_query": search_request.search_query,
                "search_college": search_request.search_college,
                "search_graduation_year": search_request.search_graduation_year,
                "search_zip_code": search_request.search_zip_code,
            }

            count_result = self.admin_client.rpc(
                "count_helpers_matching_criteria",
                count_params
            ).execute()
            total_count = count_result.data if count_result.data else 0
            
            if total_count == 0:
                return HelperListResponse(helpers=[], total_count=0, limit=search_request.limit, offset=search_request.offset)
            
            # Map parameters for the get function
            search_params = {
                "search_query": search_request.search_query,
                "search_college": search_request.search_college,
                "search_graduation_year": search_request.search_graduation_year,
                "search_zip_code": search_request.search_zip_code,
                "search_limit": search_request.limit,
                "search_offset": search_request.offset,
            }
            
            result = self.admin_client.rpc(
                "get_helpers_matching_criteria",
                search_params
            ).execute()
            
            helpers = [HelperResponse(**helper) for helper in result.data]

            return HelperListResponse(helpers=helpers, total_count=total_count, limit=search_request.limit, offset=search_request.offset)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))