from pydantic_settings import BaseSettings
from typing import Optional
import os

class BaseConfig(BaseSettings):
    """Base configuration class with common settings."""
    
    # App settings
    APP_NAME: str = "ADHD Task Manager API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    
    # CORS settings
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # AI Service settings
    OPENAI_API_KEY: Optional[str] = None
    
    # Email settings
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"
