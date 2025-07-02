from .base import BaseConfig
import os

class ProductionConfig(BaseConfig):
    """Production configuration for GCP deployment."""
    
    DEBUG: bool = False
    
    # GCP Cloud SQL MySQL configuration
    # Format: mysql+pymysql://username:password@/database?unix_socket=/cloudsql/project:region:instance
    
    # Database connection settings
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "adhd_tasks_prod")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # GCP Cloud SQL instance connection name (project:region:instance)
    CLOUD_SQL_CONNECTION_NAME: str = os.getenv("CLOUD_SQL_CONNECTION_NAME", "")
    
    # Pool settings optimized for Cloud SQL
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    @property
    def DATABASE_URL(self) -> str:
        """Build database URL based on environment."""
        if self.CLOUD_SQL_CONNECTION_NAME:
            # Cloud SQL Unix socket connection (for App Engine, Cloud Run)
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@/{self.DB_NAME}?unix_socket=/cloudsql/{self.CLOUD_SQL_CONNECTION_NAME}"
        else:
            # Direct TCP connection (for Compute Engine or external)
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Production CORS - restrict to your domain
    # This will be overridden by the base class's os.getenv("ALLOWED_ORIGINS") call
    
    # Security settings - these should be set via environment variables
    # These will be overridden by the base class's environment variable handling
    
    # Alpha Release Configuration - IMPORTANT: Update for production
    # Keep whitelist enabled for initial production deployment
    # These will be overridden by the base class's environment variable handling
    
    class Config:
        env_file = ".env.production"
