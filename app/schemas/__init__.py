# Import all schema models for easy access
from .auth import (
    PhoneOTPRequest,
    PhoneOTPVerifyRequest,
    ClientSignupRequest,
    ClientProfileUpdateRequest,
    HelperSignupRequest,
    HelperProfileUpdateRequest,
    AuthResponse,
    ProfileStatusResponse,
    OTPResponse,
    ClientProfileResponse,
    HelperAccountResponse,
    HelperProfileResponse,
    HelperVerificationResponse,
    HelperVerificationWebhookData,
    LogoutResponse,
    CurrentUser,
    UserProfileResponse
)

from .profile import (
    ClientProfileData,
    HelperProfileData,
    ProfileUpdateData,
    UserProfileStatusResponse,
    ProfileUpdateResponse
)

from .subscription import (
    SubscriptionStatus,
    CreateSubscriptionRequest,
    CreateSubscriptionResponse,
    CancelSubscriptionResponse,
    StripeCustomerData,
    StripeSubscriptionData,
    SubscriptionData,
    SubscriptionEventData,
    PostLimitInfo,
    WebhookResult
)

from .task import (
    TaskCreate,
    TaskResponse,
    TaskSearchRequest,
    TaskSearchResponse,
    TaskUpdate,
    TaskListResponse,
    TaskSearchListResponse
)

from .account import (
    PasswordChangeRequest,
    NotificationSettings,
    AccountStats,
    AccountProfileResponse,
    PasswordChangeResponse,
    NotificationSettingsResponse,
    AccountActivityResponse,
    AccountDeletionResponse
)


from .applications import (
    ApplicationResponse,
    ApplicationCreateRequest,
    ApplicationListResponse,
    ApplicationInfo
)

from .helper import (
    HelperResponse,
    HelperListResponse,
    HelperSearchRequest
)

from .invitations import (
    InvitationResponse,
    InvitationListResponse,
)

from .chat import (
    ChatCreateRequest,
    ChatResponse,
    ChatListResponse,
    MessageCreateRequest,
    MessageResponse,
    MessageListResponse,
    ChatMarkReadRequest,
    ChatWithParticipantsResponse,
    ChatParticipantInfo,
    WebSocketMessage,
    WebSocketChatMessage,
    WebSocketReadReceipt
)

from .openphone import (
    OpenPhoneMessageRequest,
    OpenPhoneMessageResponse,
    OpenPhoneErrorResponse,
    OpenPhoneMessageStatus,
    OpenPhoneServiceHealth,
    TaskCreationNotification,
    ApplicationReceivedNotification,
    ApplicationStatusNotification,
    MessageNotification,
    TaskCompletionNotification,
    PaymentReminderNotification,
    VerificationCodeNotification,
    WelcomeMessageNotification,
    BulkNotificationRequest,
    BulkNotificationResponse
)

__all__ = [
    # Auth schemas
    "PhoneOTPRequest",
    "PhoneOTPVerifyRequest", 
    "ClientSignupRequest",
    "ClientProfileUpdateRequest",
    "HelperSignupRequest",
    "HelperProfileUpdateRequest",
    "AuthResponse",
    "ProfileStatusResponse",
    "OTPResponse",
    "ClientProfileResponse",
    "HelperAccountResponse",
    "HelperProfileResponse",
    "HelperVerificationResponse",
    "HelperVerificationWebhookData",
    "LogoutResponse",
    "CurrentUser",
    "UserProfileResponse",

    # Profile schemas
    "ClientProfileData",
    "HelperProfileData",
    "ProfileUpdateData",
    "UserProfileStatusResponse",
    "ProfileUpdateResponse",
    
    # Subscription schemas
    "SubscriptionStatus",
    "CreateSubscriptionRequest",
    "CreateSubscriptionResponse",
    "CancelSubscriptionResponse",
    "StripeCustomerData",
    "StripeSubscriptionData",
    "SubscriptionData",
    "SubscriptionEventData",
    "PostLimitInfo",
    "WebhookResult",
    
    # Task schemas
    "TaskCreate",
    "TaskResponse",
    "TaskSearchRequest",
    "TaskSearchResponse",
    "TaskUpdate",
    "TaskListResponse",
    "TaskSearchListResponse",
    
    # Account schemas
    "PasswordChangeRequest",
    "NotificationSettings",
    "AccountStats",
    "AccountProfileResponse",
    "PasswordChangeResponse",
    "NotificationSettingsResponse",
    "AccountActivityResponse",
    "AccountDeletionResponse",

    # Applications schemas
    "ApplicationResponse",
    "ApplicationCreateRequest",
    "ApplicationListResponse",
    "ApplicationInfo",


    # Helper schemas
    "HelperResponse",
    "HelperListResponse",
    "HelperSearchRequest",

    # Invitations schemas
    "InvitationListResponse",
    "InvitationResponse",

    # Chat schemas
    "ChatCreateRequest",
    "ChatResponse",
    "ChatListResponse",
    "MessageCreateRequest",
    "MessageResponse",
    "MessageListResponse",
    "ChatMarkReadRequest",
    "ChatWithParticipantsResponse",
    "ChatParticipantInfo",
    "WebSocketMessage",
    "WebSocketChatMessage",
    "WebSocketReadReceipt",
    
    # OpenPhone schemas
    "OpenPhoneMessageRequest",
    "OpenPhoneMessageResponse",
    "OpenPhoneErrorResponse",
    "OpenPhoneMessageStatus",
    "OpenPhoneServiceHealth",
    "TaskCreationNotification",
    "ApplicationReceivedNotification",
    "ApplicationStatusNotification",
    "MessageNotification",
    "TaskCompletionNotification",
    "PaymentReminderNotification",
    "VerificationCodeNotification",
    "WelcomeMessageNotification",
    "BulkNotificationRequest",
    "BulkNotificationResponse",
]
