#!/usr/bin/env python3
"""
Generate a test authentication token for CRUD testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.auth import create_access_token
from app.database import get_db
from app.models.user import User
from datetime import timedelta

def generate_test_token():
    """Generate a test token for the existing user"""
    try:
        # Get database session
        db = next(get_db())
        
        # Get the existing user
        user = db.query(User).filter(User.email == "leonelcs@gmail.com").first()
        
        if not user:
            print("❌ User not found!")
            return None
        
        # Create token data
        token_data = {
            "user_id": user.id,  # Use user_id instead of sub
            "email": user.email,
            "username": user.username
        }
        
        # Create token (valid for 24 hours for testing)
        token = create_access_token(
            data=token_data,
            expires_delta=timedelta(hours=24)
        )
        
        print(f"✅ Generated test token for user: {user.username} ({user.email})")
        print(f"🔑 Token: {token}")
        print(f"👤 User ID: {user.id}")
        
        return token, user.id
        
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        return None, None
    finally:
        db.close()

if __name__ == "__main__":
    generate_test_token()
