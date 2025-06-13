#!/usr/bin/env python3
"""
Test MySQL connection for ADHD Task Manager
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.config.settings import config
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mysql_connection():
    """Test the MySQL database connection."""
    try:
        logger.info(f"Testing connection to: {config.DATABASE_URL.split('@')[0]}@***")
        
        # Create engine
        engine = create_engine(config.DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION() as version"))
            version = result.fetchone()
            logger.info(f"✅ MySQL connection successful!")
            logger.info(f"MySQL version: {version[0]}")
            
            # Test database access
            result = connection.execute(text("SELECT DATABASE() as db"))
            db = result.fetchone()
            logger.info(f"Connected to database: {db[0]}")
            
            # Test user privileges
            result = connection.execute(text("SHOW GRANTS"))
            grants = result.fetchall()
            logger.info("User privileges:")
            for grant in grants:
                logger.info(f"  {grant[0]}")
                
        return True
        
    except Exception as e:
        logger.error(f"❌ MySQL connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧠 ADHD Task Manager - MySQL Connection Test")
    print("=" * 50)
    
    success = test_mysql_connection()
    
    if success:
        print("\n✅ Database connection test passed!")
        print("You can now run Alembic migrations.")
    else:
        print("\n❌ Database connection test failed!")
        print("Please check your MySQL setup and credentials.")
        sys.exit(1)
