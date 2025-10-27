from pydantic import BaseModel, Field
from typing import Optional, List



class HelperSearchRequest(BaseModel):
    """Request model for searching helpers"""
    search_query: Optional[str] = Field(None, description="Text search in name, bio, and college")
    search_college: Optional[str] = Field(None, description="Filter by college name")
    search_graduation_year: Optional[int] = Field(None, ge=1900, le=2100, description="Filter by graduation year")
    search_zip_code: Optional[str] = Field(None, min_length=5, max_length=10, description="Filter by zip code")
    limit: int = Field(20, ge=1, le=100, description="Number of helpers to return")
    offset: int = Field(0, ge=0, description="Number of helpers to skip")


class HelperResponse(BaseModel):
    """Response model for helper data"""
    id: str
    first_name: str
    last_name: str
    college: str
    bio: str
    graduation_year: int
    zip_code: Optional[str]
    pfp_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        # This will ignore extra fields not defined in the schema
        extra = "ignore"

class HelperListResponse(BaseModel):
    """Response model for list of helpers"""
    helpers: List[HelperResponse]
    total_count: int
    limit: int
    offset: int