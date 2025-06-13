from .base import BaseConfig

class LocalConfig(BaseConfig):
    """Local development configuration."""
    
    DEBUG: bool = True
    
    # Local SQLite database for development (commented out)
    # DATABASE_URL: str = "sqlite:///./adhd_tasks.db"
    
    # For local MySQL testing - using the MySQL setup
    DATABASE_URL: str = "mysql+pymysql://adhd_tasksmanager:My:S3cr3t@localhost:30306/adhd_tasks_dev"
    
    # Local development CORS - allow all origins for development
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001"
    
    # Local development settings
    SECRET_KEY: str = "local-dev-secret-key-not-for-production"
    
    class Config:
        env_file = ".env.local"
