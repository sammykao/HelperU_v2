from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .helper import HelperResponse

class ApplicationInfo(BaseModel):
    """Response model for list of applications"""
    id: str
    task_id: str
    helper_id: str
    introduction_message: str
    supplements_url: Optional[str] = Field(None, description="URL of supplements")
    created_at: datetime
    updated_at: datetime

    class Config:
        # This will ignore extra fields not defined in the schema
        extra = "ignore"


class ApplicationResponse(BaseModel):
    """Response model for a single application"""
    application: ApplicationInfo
    helper: HelperResponse

class ApplicationListResponse(BaseModel):
    """Response model for list of applications"""
    applications: List[ApplicationResponse]
    total_count: int


class ApplicationCreateRequest(BaseModel):
    """Request model for creating an application"""
    task_id: str = Field(..., description="ID of the task")
    helper_id: str = Field(..., description="ID of the helper")
    introduction_message: str = Field(..., description="Introduction message")
    supplements_url: Optional[str] = Field(None, description="URL of supplements")