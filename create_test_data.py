#!/usr/bin/env python3
"""
Create test data for testing the group invitation functionality.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.models.group import SharedGroup, SharedGroupMembership
from sqlalchemy.exc import IntegrityError
import json

def create_test_data():
    db = SessionLocal()
    try:
        # Create test user if doesn't exist
        test_email = "test@gmail.com"
        existing_user = db.query(User).filter(User.email == test_email).first()
        if not existing_user:
            test_user = User(
                email=test_email,
                full_name="Test User",
                is_active=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"Created test user: {test_user.email} (ID: {test_user.id})")
        else:
            test_user = existing_user
            print(f"Using existing test user: {test_user.email} (ID: {test_user.id})")

        # Create test group if doesn't exist
        group_name = "ADHD Test Group"
        existing_group = db.query(SharedGroup).filter(SharedGroup.name == group_name).first()
        if not existing_group:
            test_group = SharedGroup(
                name=group_name,
                description="A test group for ADHD support and collaboration",
                created_by=test_user.id,
                is_active=True,
                group_focus_sessions=True,
                shared_energy_tracking=True,
                group_dopamine_celebrations=True,
                collaborative_task_chunking=True,
                group_break_reminders=True,
                accountability_features=True
            )
            db.add(test_group)
            db.commit()
            db.refresh(test_group)
            print(f"Created test group: {test_group.name} (ID: {test_group.id})")
            
            # Add creator as group member
            membership = SharedGroupMembership(
                shared_group_id=test_group.id,
                user_id=test_user.id,
                role="owner",
                is_active=True
            )
            db.add(membership)
            db.commit()
            print(f"Added test user as group owner")
        else:
            test_group = existing_group
            print(f"Using existing test group: {test_group.name} (ID: {test_group.id})")

        print("\nTest data created successfully!")
        print(f"User ID: {test_user.id}")
        print(f"Group ID: {test_group.id}")
        print(f"Group is_active: {test_group.is_active}")
        
        return test_user, test_group
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
        return None, None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
