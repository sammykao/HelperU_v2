from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.helper import HelperResponse


class InvitationResponse(BaseModel):
    """Response model for inviting a helper to a task"""
    id: str
    task_id: str
    helper_id: str
    created_at: datetime
    updated_at: datetime
    helpers: Optional[HelperResponse] = None

class InvitationListResponse(BaseModel):
    """Response model for list of invitations"""
    invitations: List[InvitationResponse]
    total_count: int

