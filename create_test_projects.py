#!/usr/bin/env python3
"""
Create test projects for testing the project filtering functionality.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.models.project import Project, ProjectCollaboration
from app.models.group import SharedGroup, SharedGroupMembership
from app.schemas.project import ProjectType, ProjectStatus
from sqlalchemy.exc import IntegrityError

def create_test_projects():
    db = SessionLocal()
    try:
        # Get test user
        test_user = db.query(User).filter(User.email == "test@gmail.com").first()
        if not test_user:
            print("Test user not found. Run create_test_data.py first.")
            return
        
        # Get test group
        test_group = db.query(SharedGroup).filter(SharedGroup.name == "ADHD Test Group").first()
        
        # Create personal project
        personal_project = Project(
            name="Personal ADHD Management",
            description="My personal project for managing ADHD tasks and routines",
            project_type=ProjectType.PERSONAL,
            status=ProjectStatus.ACTIVE,
            owner_id=test_user.id,
            is_active=True,
            is_public_joinable=False
        )
        
        # Create shared project (with group)
        shared_project = Project(
            name="ADHD Support Group Project",
            description="Collaborative project for the ADHD support group",
            project_type=ProjectType.SHARED,
            status=ProjectStatus.ACTIVE,
            owner_id=test_user.id,
            shared_group_id=test_group.id if test_group else None,
            is_active=True,
            is_public_joinable=False
        )
        
        # Create public project
        public_project = Project(
            name="ADHD Community Resources",
            description="Public project for sharing ADHD resources and tips",
            project_type=ProjectType.PUBLIC,
            status=ProjectStatus.ACTIVE,
            owner_id=test_user.id,
            is_active=True,
            is_public_joinable=True,
            max_collaborators=50
        )
        
        # Add projects to database
        for project in [personal_project, shared_project, public_project]:
            existing = db.query(Project).filter(Project.name == project.name).first()
            if not existing:
                db.add(project)
                db.commit()
                db.refresh(project)
                print(f"Created project: {project.name} (ID: {project.id}, Type: {project.project_type.value})")
            else:
                print(f"Project already exists: {project.name}")
        
        print("Test projects created successfully!")
        
    except Exception as e:
        print(f"Error creating test projects: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_projects()
