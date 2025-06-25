#!/usr/bin/env python3
"""
Create test tasks for testing the organized task display.
"""
import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

# First, let's get a token
def get_auth_token():
    """Generate authentication token for test user."""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get token: {response.status_code}")
        print(response.text)
        return None

def create_test_tasks(token):
    """Create various test tasks."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get existing projects first
    projects_response = requests.get(f"{BASE_URL}/api/projects", headers=headers, params={"project_type": ["personal", "shared", "public"]})
    projects = projects_response.json() if projects_response.status_code == 200 else []
    
    print(f"Found {len(projects)} projects")
    for project in projects:
        print(f"- {project['name']} (Type: {project['project_type']}, ID: {project['id']})")
    
    # Create personal tasks (no project)
    personal_tasks = [
        {
            "title": "Daily meditation practice",
            "description": "10 minutes mindfulness meditation",
            "task_type": "routine",
            "priority": "medium",
            "impact_size": "pebbles",
            "estimated_duration": 10
        },
        {
            "title": "Organize desk workspace",
            "description": "Clear and organize my workspace for better focus",
            "task_type": "maintenance",
            "priority": "low",
            "impact_size": "sand",
            "estimated_duration": 15
        },
        {
            "title": "Complete quarterly review",
            "description": "Review goals and progress for Q2",
            "task_type": "project",
            "priority": "high",
            "impact_size": "rock",
            "estimated_duration": 120
        }
    ]
    
    print("\nCreating personal tasks...")
    for task_data in personal_tasks:
        response = requests.post(f"{BASE_URL}/api/tasks", headers=headers, json=task_data)
        if response.status_code == 200:
            print(f"✅ Created personal task: {task_data['title']}")
        else:
            print(f"❌ Failed to create task: {task_data['title']} - {response.status_code}")
            print(response.text)
    
    # Create project-specific tasks
    for project in projects:
        project_tasks = [
            {
                "title": f"Review {project['name']} requirements",
                "description": f"Go through project requirements for {project['name']}",
                "task_type": "project",
                "priority": "high",
                "impact_size": "rock",
                "estimated_duration": 60,
                "project_id": project['id']
            },
            {
                "title": f"Update {project['name']} documentation",
                "description": f"Keep documentation current for {project['name']}",
                "task_type": "maintenance",
                "priority": "medium",
                "impact_size": "pebbles",
                "estimated_duration": 30,
                "project_id": project['id']
            },
            {
                "title": f"Test {project['name']} features",
                "description": f"Run quality checks on {project['name']}",
                "task_type": "project",
                "priority": "medium",
                "impact_size": "pebbles",
                "estimated_duration": 45,
                "project_id": project['id']
            }
        ]
        
        print(f"\nCreating tasks for project: {project['name']} ({project['project_type']})")
        for task_data in project_tasks:
            response = requests.post(f"{BASE_URL}/api/tasks", headers=headers, json=task_data)
            if response.status_code == 200:
                print(f"✅ Created project task: {task_data['title']}")
            else:
                print(f"❌ Failed to create task: {task_data['title']} - {response.status_code}")
                print(response.text)

if __name__ == "__main__":
    print("🎯 Creating test tasks for organized display...")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Could not get authentication token")
        exit(1)
    
    # Create test tasks
    create_test_tasks(token)
    
    print("\n✅ Test task creation complete!")
    print("🚀 You can now test the organized task display on the frontend!")
