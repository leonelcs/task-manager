#!/usr/bin/env python3
"""
Test script to verify UUID implementation works correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskPriority, TaskStatus, ADHDTaskType, ADHDImpactSize
import uuid

def test_uuid_implementation():
    """Test that UUID implementation works correctly"""
    db = next(get_db())
    
    try:
        print("🧪 Testing UUID implementation...")
        
        # Test 1: Create a user with UUID
        user = User(
            email="test_uuid@example.com",
            username="uuid_test_user",
            full_name="UUID Test User"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ User created with UUID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   UUID length: {len(user.id)} (should be 36)")
        
        # Test 2: Create a project with UUID
        project = Project(
            name="UUID Test Project",
            description="Testing UUID implementation",
            owner_id=user.id
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        print(f"✅ Project created with UUID: {project.id}")
        print(f"   Name: {project.name}")
        print(f"   Owner ID: {project.owner_id}")
        print(f"   UUID length: {len(project.id)} (should be 36)")
        
        # Test 3: Create a task with UUID references
        task = Task(
            title="UUID Test Task",
            description="Testing task with UUID references",
            task_type=ADHDTaskType.FOCUS,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.TODO,
            impact_size=ADHDImpactSize.PEBBLES,
            project_id=project.id,
            created_by=user.id,
            assigned_user_id=user.id
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        print(f"✅ Task created with ID: {task.id}")
        print(f"   Title: {task.title}")
        print(f"   Project ID: {task.project_id}")
        print(f"   Created by: {task.created_by}")
        print(f"   Assigned to: {task.assigned_user_id}")
        
        # Test 4: Query relationships
        user_projects = db.query(Project).filter(Project.owner_id == user.id).all()
        project_tasks = db.query(Task).filter(Task.project_id == project.id).all()
        
        print(f"✅ User has {len(user_projects)} projects")
        print(f"✅ Project has {len(project_tasks)} tasks")
        
        # Test 5: Verify UUID format
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        
        assert re.match(uuid_pattern, user.id), f"User ID is not a valid UUID: {user.id}"
        assert re.match(uuid_pattern, project.id), f"Project ID is not a valid UUID: {project.id}"
        
        print("✅ All UUIDs have correct format")
        
        print("\n🎉 All tests passed! UUID implementation is working correctly.")
        
        # Clean up test data
        db.delete(task)
        db.delete(project)
        db.delete(user)
        db.commit()
        
        print("🧹 Test data cleaned up.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = test_uuid_implementation()
    exit(0 if success else 1)
