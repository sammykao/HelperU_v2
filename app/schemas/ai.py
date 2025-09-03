from pydantic import BaseModel
from typing import Optional, Dict, Any


class AIRequest(BaseModel):
    """Request model for AI assistant"""
    message: str
    thread_id: Optional[str] = None


class AIResponse(BaseModel):
    """Response model for AI assistant"""
    response: str
    thread_id: Optional[str] = None
    agent_used: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
