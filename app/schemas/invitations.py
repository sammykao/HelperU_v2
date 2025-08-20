from typing import List
from pydantic import BaseModel


class InvitationResponse(BaseModel):
    """Response model for inviting a helper to a task"""
    id: str
    task_id: str
    helper_id: str
    created_at: str
    updated_at: str

class InvitationListResponse(BaseModel):
    """Response model for list of invitations"""
    invitations: List[InvitationResponse]
    total_count: int

