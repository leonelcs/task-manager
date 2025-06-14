"""
Script to create a test user for authentication testing.
"""
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.auth import get_password_hash

def create_test_user():
    """Create a test user for authentication testing."""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@adhdtasks.com").first()
        if existing_user:
            print("✅ Test user already exists!")
            print(f"   Email: {existing_user.email}")
            print(f"   Username: {existing_user.username}")
            print(f"   Provider: {existing_user.provider}")
            return existing_user
        
        # Create test user
        test_user = User(
            username="adhd_test_user",
            email="test@adhdtasks.com",
            full_name="ADHD Test User",
            hashed_password=get_password_hash("testpassword123"),
            provider="local",
            is_active=True,
            # ADHD profile with default values
            adhd_profile={
                "energy_patterns": {
                    "morning": "high",
                    "afternoon": "medium", 
                    "evening": "low"
                },
                "focus_duration": {
                    "optimal": 25,
                    "maximum": 45,
                    "minimum": 10
                },
                "preferences": {
                    "break_reminders": True,
                    "dopamine_rewards": True,
                    "task_chunking": True,
                    "deadline_buffers": True,
                    "hyperfocus_alerts": True
                },
                "triggers": {
                    "overwhelm_threshold": 5,
                    "complexity_limit": "medium",
                    "notification_frequency": "gentle"
                }
            },
            stats={
                "tasks_completed_today": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "total_tasks_completed": 0
            }
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("🎉 Test user created successfully!")
        print(f"   Email: {test_user.email}")
        print(f"   Username: {test_user.username}")
        print(f"   Password: testpassword123")
        print(f"   Provider: {test_user.provider}")
        print(f"   User ID: {test_user.id}")
        
        return test_user
        
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
