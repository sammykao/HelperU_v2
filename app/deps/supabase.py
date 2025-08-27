from supabase import Client
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.supabase_client import get_public_supabase, get_admin_supabase
from app.services.profile_service import ProfileService
from app.services.stripe_service import StripeService
from app.services.task_service import TaskService
from app.services.auth_service import AuthService
from app.services.helper_service import HelperService
from app.services.application_service import ApplicationService
from app.services.chat_service import ChatService
from app.services.openphone_service import OpenPhoneService
from app.schemas.auth import CurrentUser
security = HTTPBearer()


def get_supabase_public() -> Client:
    return get_public_supabase()


def get_supabase_admin() -> Client:
    return get_admin_supabase()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""

    try:
        public_client = get_public_supabase()
        user = public_client.auth.get_user(credentials.credentials)
        
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        

        return CurrentUser(
            id=user.user.id,
            email=user.user.email,
            phone=user.user.phone,
            email_confirmed_at=user.user.email_confirmed_at,
            phone_confirmed_at=user.user.phone_confirmed_at,
            created_at=user.user.created_at
        )
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

def get_stripe_service() -> StripeService:
    """Dependency to get Stripe service"""
    admin_client = get_supabase_admin()
    return StripeService(admin_client) 

def get_profile_service() -> ProfileService:
    """Dependency to get profile service with Supabase admin client"""
    admin_client = get_supabase_admin()
    return ProfileService(admin_client)
    
def get_auth_service()-> AuthService:
    """Dependency to get auth service with Supabase clients"""
    public_client = get_public_supabase()
    admin_client = get_supabase_admin()
    return AuthService(public_client, admin_client)


def get_task_service() -> TaskService:
    """Dependency to get task service with Supabase admin client"""
    admin_client = get_supabase_admin()
    stripe_service = get_stripe_service()
    task_service = TaskService(admin_client, stripe_service)
    return task_service

def get_helper_service() -> HelperService:
    """Dependency to get helper service with Supabase admin client"""
    admin_client = get_supabase_admin()
    return HelperService(admin_client)

def get_application_service() -> ApplicationService:
    """Dependency to get application service with Supabase admin client and task service"""
    admin_client = get_supabase_admin()
    task_service = get_task_service()
    helper_service = get_helper_service()
    return ApplicationService(admin_client, task_service, helper_service)


def get_chat_service() -> ChatService:
    """Dependency to get chat service with Supabase admin client"""
    admin_client = get_supabase_admin()
    openphone_service = get_openphone_service()
    return ChatService(admin_client, openphone_service)


def get_openphone_service() -> OpenPhoneService:
    """Dependency to get OpenPhone service for SMS notifications"""
    return OpenPhoneService()