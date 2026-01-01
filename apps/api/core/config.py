"""
Core Configuration Settings
Loads environment variables and provides application-wide settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    DATABASE_ASYNC_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours for development
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api/v1"
    
    # CORS - Can be set as JSON array string or comma-separated list
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8000"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS into a list of strings"""
        import json
        origins = self.CORS_ORIGINS.strip()
        # Try parsing as JSON array first
        if origins.startswith('[') and origins.endswith(']'):
            try:
                return json.loads(origins)
            except json.JSONDecodeError:
                pass
        # Fall back to comma-separated list
        return [origin.strip() for origin in origins.split(',') if origin.strip()]
    
    # File Storage (S3-Compatible, including Cloudflare R2)
    # For Cloudflare R2: Use R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL
    # For AWS S3/DigitalOcean Spaces: Use S3_ENDPOINT_URL, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_BUCKET_NAME
    S3_ENDPOINT_URL: str = ""  # S3-compatible endpoint (e.g., R2_ENDPOINT_URL for Cloudflare)
    S3_ACCESS_KEY_ID: str = ""  # Access key (e.g., R2_ACCESS_KEY_ID for Cloudflare)
    S3_SECRET_ACCESS_KEY: str = ""  # Secret key (e.g., R2_SECRET_ACCESS_KEY for Cloudflare)
    S3_BUCKET_NAME: str = ""  # Bucket name (e.g., R2_BUCKET_NAME for Cloudflare)
    S3_REGION: str = "auto"  # Region (use "auto" for Cloudflare R2)
    S3_PUBLIC_URL: str = ""  # Public URL for accessing files (e.g., R2_PUBLIC_URL for Cloudflare)
    
    # Cloudflare R2 (alternative naming for clarity)
    R2_ENDPOINT_URL: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = ""
    R2_PUBLIC_URL: str = ""
    
    # Email Configuration
    SEND_EMAILS: bool = False
    EMAIL_PROVIDER: str = "smtp"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: str = "noreply@inara.org"
    FROM_NAME: str = "INARA HR System"
    APP_URL: str = "http://localhost:3002"
    
    # Legacy SMTP fields (backward compatibility)
    SMTP_USER: str = ""
    SMTP_FROM: str = ""
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Organization
    ORG_NAME: str = "INARA"
    ORG_TIMEZONE: str = "UTC"
    DEFAULT_COUNTRY: str = "US"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_AUTH_PER_MINUTE: int = 5  # Stricter for auth endpoints
    
    # File Upload Limits
    MAX_FILE_SIZE_MB: int = 10  # 10 MB default
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB in bytes
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".xlsx", ".xls"]
    
    # Request Timeouts
    REQUEST_TIMEOUT_SECONDS: int = 30
    UPLOAD_TIMEOUT_SECONDS: int = 300  # 5 minutes for file uploads
    
    # Error Tracking (Sentry)
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings
settings = Settings()
