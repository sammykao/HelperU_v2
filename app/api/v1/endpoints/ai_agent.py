from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.deps.supabase import get_current_user
from app.ai_agent.router_agent import HelperURouter
from app.schemas import AIRequest, AIResponse

router = APIRouter()
security = HTTPBearer(auto_error=False)





AI_AGENT = HelperURouter()


@router.post("/chat", response_model=AIResponse)
async def ai_assistant(
    request: AIRequest,
    credentials: HTTPBearer = Depends(security)
):
    """
    AI Assistant endpoint that handles both authenticated and anonymous users.
    
    - If user is authenticated: Routes to appropriate specialized agents
    - If user is not authenticated: Provides FAQs and platform information
    """
    try:
        current_user = None
        try:
            current_user = get_current_user(credentials)
        except Exception:
            pass
        
        result = await AI_AGENT.run(
            message=request.message,
            current_user=current_user,
            thread_id=request.thread_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Assistant error: {str(e)}"
        )

