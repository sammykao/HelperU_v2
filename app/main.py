from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.cors import CORS_KWARGS
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.profile import router as profile_router
from app.api.v1.endpoints.subscriptions import router as subscriptions_router
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.applications import router as applications_router
from app.api.v1.endpoints.helper import router as helper_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.ai_agent import router as ai_agent_router

app = FastAPI(title="HelperU Backend Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    **CORS_KWARGS,
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(profile_router, prefix="/api/v1/profile", tags=["users"])
app.include_router(
    subscriptions_router, prefix="/api/v1/subscriptions", tags=["subscriptions"]
)
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(
    applications_router, prefix="/api/v1/applications", tags=["applications"]
)
app.include_router(helper_router, prefix="/api/v1/helpers", tags=["helpers"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(ai_agent_router, prefix="/api/v1/ai", tags=["ai-agent"])


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    return {
        "message": "HelperU Backend API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/test-public")
def test_public() -> dict:
    print("DEBUG: test-public endpoint called - no auth required")
    return {"message": "This is a public test endpoint"}
