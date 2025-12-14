from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App settings
    APP_NAME: str = "SAHASplit"
    DEBUG: bool = False
    API_VERSION: str = "v1"

    # Database settings
    DATABASE_URL: str
    DB_HOST: Optional[str] = "localhost"
    DB_PORT: int = 3306
    DB_USER: Optional[str] = "sahasplit"
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = "sahasplit"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600 * 10  # 10 years - never expire
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3650  # 10 years - never expire

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # OAuth - Google
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # OAuth - Authentik
    AUTHENTIK_CLIENT_ID: Optional[str] = None
    AUTHENTIK_CLIENT_SECRET: Optional[str] = None
    AUTHENTIK_ISSUER: Optional[str] = None

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@sahasplit.app"
    SUPPORT_EMAIL: Optional[str] = None

    # S3/R2 Storage
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: Optional[str] = None
    R2_PUBLIC_URL: Optional[str] = None

    # AWS S3 (alternative)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_S3_BUCKET_NAME: Optional[str] = None

    # Bank integrations
    PLAID_CLIENT_ID: Optional[str] = None
    PLAID_SECRET: Optional[str] = None
    PLAID_ENV: str = "sandbox"

    GOCARDLESS_SECRET_ID: Optional[str] = None
    GOCARDLESS_SECRET_KEY: Optional[str] = None

    # Currency rates
    CURRENCY_API_KEY: Optional[str] = None

    # Push notifications
    WEB_PUSH_PUBLIC_KEY: Optional[str] = None
    WEB_PUSH_PRIVATE_KEY: Optional[str] = None
    WEB_PUSH_EMAIL: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

