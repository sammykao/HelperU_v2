from typing import List
from pydantic import BaseModel
from datetime import datetime


class InvitationResponse(BaseModel):
    """Response model for inviting a helper to a task"""
    id: str
    task_id: str
    helper_id: str
    created_at: datetime
    updated_at: datetime

class InvitationListResponse(BaseModel):
    """Response model for list of invitations"""
    invitations: List[InvitationResponse]
    total_count: int

