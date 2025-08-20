from pydantic import BaseModel, Field, validator
from typing import List, Optional


class TaskCreate(BaseModel):
    """Request model for creating a new task"""
    title: str = Field(..., min_length=1, max_length=200)
    dates: List[str] = Field(..., description="List of dates in YYYY-MM-DD format")
    location_type: str = Field(..., description="Type of location (remote, in-person, etc.)")
    zip_code: str = Field(..., description="ZIP code for the task")
    hourly_rate: float = Field(..., description="Hourly rate for the task")
    description: str = Field(..., min_length=10, max_length=2000)
    tools_info: str = Field("", description="Information about required tools")
    public_transport_info: str = Field("", description="Public transportation information")


class TaskResponse(BaseModel):
    """Response model for task data"""
    id: str
    client_id: str
    title: str
    hourly_rate: float
    dates: List[str]
    location_type: str
    zip_code: str
    description: str
    tools_info: str
    public_transport_info: str
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str


class TaskSearchRequest(BaseModel):
    """Request model for task search filtering"""
    search_zip_code: str = Field(..., description="Base location for distance calculations")
    query: Optional[str] = Field(None, description="Text search in title and description")
    location_type: Optional[str] = Field(None, description="Filter by location type (remote, in-person, etc.)")
    min_hourly_rate: Optional[float] = Field(None, ge=0, description="Minimum hourly rate filter")
    max_hourly_rate: Optional[float] = Field(None, ge=0, description="Maximum hourly rate filter")
    status: str = Field("open", description="Filter by task status (open, completed)")
    limit: int = Field(20, ge=1, le=100, description="Number of tasks to return")
    offset: int = Field(0, ge=0, description="Number of tasks to skip")
    
    @validator('max_hourly_rate')
    def validate_hourly_rate_range(cls, v, values):
        """Ensure max_hourly_rate is greater than min_hourly_rate when both are provided"""
        if v is not None and 'min_hourly_rate' in values and values['min_hourly_rate'] is not None:
            if v <= values['min_hourly_rate']:
                raise ValueError('max_hourly_rate must be greater than min_hourly_rate')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Ensure status is a valid value"""
        valid_statuses = ['open', 'completed']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {valid_statuses}')
        return v


class TaskSearchResponse(BaseModel):
    """Response model for task search results with distance"""
    id: str
    client_id: str
    title: str
    hourly_rate: float
    dates: List[str]
    location_type: str
    zip_code: str
    description: str
    tools_info: str
    public_transport_info: str
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str
    distance: Optional[float] = Field(None, description="Distance in miles from search location")


class TaskUpdate(BaseModel):
    """Request model for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    dates: Optional[List[str]] = Field(None, description="List of dates in YYYY-MM-DD format")
    location_type: Optional[str] = Field(None, description="Type of location (remote, in-person, etc.)")
    zip_code: Optional[str] = Field(None, description="ZIP code for the task")
    hourly_rate: Optional[float] = Field(None, description="Hourly rate for the task")
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    tools_info: Optional[str] = Field(None, description="Information about required tools")
    public_transport_info: Optional[str] = Field(None, description="Public transportation information")


class TaskListResponse(BaseModel):
    """Response model for list of tasks"""
    tasks: List[TaskResponse]
    total_count: int
    limit: int
    offset: int


class TaskSearchListResponse(BaseModel):
    """Response model for list of searched tasks with distance"""
    tasks: List[TaskSearchResponse]
    total_count: int
    limit: int
    offset: int
