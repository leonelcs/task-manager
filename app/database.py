from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database engine configuration
def create_database_engine():
    """Create SQLAlchemy engine with appropriate configuration."""
    
    database_url = config.DATABASE_URL
    logger.info(f"Connecting to database: {database_url.split('@')[0]}@***")
    
    # Engine arguments based on database type
    engine_args = {
        "pool_size": config.DB_POOL_SIZE,
        "max_overflow": config.DB_MAX_OVERFLOW,
        "pool_timeout": config.DB_POOL_TIMEOUT,
        "pool_recycle": config.DB_POOL_RECYCLE,
        "echo": config.DEBUG,  # Log SQL queries in debug mode
    }
    
    # SQLite specific settings (for local development)
    if "sqlite" in database_url:
        engine_args["connect_args"] = {"check_same_thread": False}
        # Remove pool settings for SQLite
        engine_args.pop("pool_size")
        engine_args.pop("max_overflow")
        engine_args.pop("pool_timeout")
        engine_args.pop("pool_recycle")
    
    # MySQL specific settings
    elif "mysql" in database_url:
        engine_args["connect_args"] = {
            "charset": "utf8mb4",
            "connect_timeout": 60,
            "read_timeout": 30,
            "write_timeout": 30,
        }
        
        # Add SSL settings for production
        if not config.DEBUG:
            engine_args["connect_args"]["ssl_disabled"] = False
    
    return create_engine(database_url, **engine_args)

# Create engine
engine = create_database_engine()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Dependency function to get database session.
    This will be used in FastAPI route dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    """
    Create all tables in the database.
    This should be called during application startup.
    """
    Base.metadata.create_all(bind=engine)
