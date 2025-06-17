#!/usr/bin/env python3
"""
Generate a test JWT token for API testing.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routers.auth import create_access_token
from app.database import SessionLocal
from app.models.user import User
from datetime import timedelta

def generate_test_token():
    db = SessionLocal()
    try:
        # Get the test user
        test_user = db.query(User).filter(User.email == "test@gmail.com").first()
        if not test_user:
            print("Test user not found. Run create_test_data.py first.")
            return None
        
        # Generate token for test user
        token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(hours=24)
        )
        
        print(f"Test token for user {test_user.email} (ID: {test_user.id}):")
        print(token)
        return token
        
    except Exception as e:
        print(f"Error generating token: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    generate_test_token()
