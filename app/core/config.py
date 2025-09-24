from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PREMIUM_PRICE_ID: str
    
    # Frontend Configuration
    FRONTEND_URL: str       
    
    # OpenPhone Configuration
    OPENPHONE_API_KEY: str
    OPENPHONE_FROM_NUMBER: str

    OPENAI_API_KEY: str
    
    # Email Configuration
    EMAIL_SENDER: str = "info@helperu.com"
    EMAIL_PASSWORD: str
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    # Apple app bundle information
    HELPER_MOBILE_APP_BUNDLE_ID: str
    HELPER_PUSH_NOTIFICATION_P8_ID: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings() 
