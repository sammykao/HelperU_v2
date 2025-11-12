from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime



class ClientInfo(BaseModel):
    """Client information for task display"""
    id: str
    first_name: str
    last_name: str
    phone: str
    email: str
    pfp_url: Optional[str] = None

    # This will ignore extra fields not defined in the schema
    class Config:
        extra = "ignore"

class TaskCreate(BaseModel):
    """Request model for creating a new task"""

    title: str = Field(..., min_length=1, max_length=200)
    dates: List[str] = Field(..., description="List of dates in YYYY-MM-DD format")
    location_type: str = Field(..., description="Type of location (remote, in_person, etc.)")
    zip_code: Optional[str] = Field(None, description="ZIP code for the task")
    hourly_rate: float = Field(None, description="Hourly rate for the task")
    description: str = Field(..., min_length=10, max_length=2000)
    tools_info: Optional[str] = Field(None, description="Information about required tools")
    public_transport_info: Optional[str] = Field(None, description="Public transportation information")


class TaskResponse(BaseModel):
    """Response model for task data"""

    id: str
    client_id: str
    title: str
    hourly_rate: float
    dates: List[str]
    location_type: str
    zip_code: Optional[str] = None
    description: str
    tools_info: Optional[str] = None
    public_transport_info: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    client: Optional[ClientInfo] = Field(None, description="Client information")

    class Config:
        extra = "ignore"


class TaskSearchRequest(BaseModel):
    """Request model for task search filtering"""
    search_zip_code: str = Field(..., description="Base location for distance calculations")
    search_query: Optional[str] = Field(None, description="Text search in title and description")
    search_location_type: Optional[str] = Field(None, description="Filter by location type (remote, in_person, etc.)")
    min_hourly_rate: Optional[float] = Field(None, ge=0, description="Minimum hourly rate filter")
    max_hourly_rate: Optional[float] = Field(None, ge=0, description="Maximum hourly rate filter")
    search_limit: int = Field(20, ge=1, le=100, description="Number of tasks to return")
    search_offset: int = Field(0, ge=0, description="Number of tasks to skip")
    sort_by: Optional[str] = Field('post_date', description="Sort mode: 'distance' or 'post_date'")
    distance_radius: Optional[float] = Field(100, ge=0, le=500, description="Distance radius in miles for distance sorting, default is 100 miles")

    @validator("max_hourly_rate")
    def validate_hourly_rate_range(cls, v, values):
        """Ensure max_hourly_rate is greater than min_hourly_rate when both are provided"""
        if (
            v is not None
            and "min_hourly_rate" in values
            and values["min_hourly_rate"] is not None
        ):
            if v <= values["min_hourly_rate"]:
                raise ValueError("max_hourly_rate must be greater than min_hourly_rate")
        return v





class TaskSearchResponse(BaseModel):
    """Response model for task search results with distance"""

    id: str
    client_id: str
    title: str
    hourly_rate: float
    dates: List[str]
    location_type: str
    zip_code: Optional[str] = None
    description: str
    tools_info: Optional[str] = None
    public_transport_info: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    distance: Optional[float] = Field(
        None, description="Distance in miles from search location"
    )
    client: ClientInfo


class TaskUpdate(BaseModel):
    """Request model for updating a task"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    dates: Optional[List[str]] = Field(
        None, description="List of dates in YYYY-MM-DD format"
    )
    location_type: Optional[str] = Field(
        None, description="Type of location (remote, in_person, etc.)"
    )
    zip_code: Optional[str] = Field(None, description="ZIP code for the task")
    hourly_rate: Optional[float] = Field(None, description="Hourly rate for the task")
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    tools_info: Optional[str] = Field(
        None, description="Information about required tools"
    )
    public_transport_info: Optional[str] = Field(
        None, description="Public transportation information"
    )


class TaskListResponse(BaseModel):
    """Response model for list of tasks"""

    tasks: List[TaskResponse]
    total_count: int
    limit: int
    offset: int


class TaskSearchListResponse(BaseModel):
    """Response model for list of searched tasks with distance"""

    tasks: List[TaskSearchResponse]
    limit: int
    offset: int


class PublicTask(BaseModel):
    """Response model for fetching public facing tasks"""

    id: str
    title: str
    description: str
    location_type: str
    zip_code: Optional[str]
    hourly_rate: int
    created_at: str


class PublicTaskResponse(BaseModel):
    """Response model for a list of public facing tasks"""

    result: List[PublicTask]
    limit: int
    total_count: int

class GetZipCodesRequest(BaseModel):
    """Request model for getting zip codes"""

    zip_codes: List[str]


class PublicTaskZipCode(BaseModel):
    """Response model for a public facing task zip code"""

    zip_code: str
    city: str
    state: str
    lat: float
    lng: float

class PublicTaskZipCodeResponse(BaseModel):
    """Response model for a list of public facing tasks"""

    result: List[PublicTaskZipCode]

