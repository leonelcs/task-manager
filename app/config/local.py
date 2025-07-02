from .base import BaseConfig
import os

class LocalConfig(BaseConfig):
    """Local development configuration."""
    
    DEBUG: bool = True
    
    # Local SQLite database for development (temporary fix)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./adhd_tasks.db")
    
    # For local MySQL testing - using the MySQL setup (disabled temporarily)
    # DATABASE_URL: str = "mysql+pymysql://adhd_tasksmanager:TaskManager2024!@localhost:30306/adhd_tasks_dev"
    
    # Local development CORS - allow all origins for development
    # This will be overridden by the base class's os.getenv("ALLOWED_ORIGINS") call
    
    # Local development settings
    # This will be overridden by the base class's os.getenv("SECRET_KEY") call
    
    class Config:
        env_file = ".env.local"
