#!/usr/bin/env python3
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_task_creation():
    """Test task creation with different payloads to identify 422 issues"""
    
    # First, let's try to get a valid auth token
    # You'll need to replace this with actual authentication
    headers = {
        'Content-Type': 'application/json',
        # 'Authorization': 'Bearer YOUR_TOKEN_HERE'  # Add this when you have a token
    }
    
    # Test different payloads
    test_cases = [
        {
            "name": "Minimal valid task",
            "payload": {
                "title": "Test Task",
                "impact_size": "pebbles"
            }
        },
        {
            "name": "Complete task with all fields",
            "payload": {
                "title": "Complete Task Test",
                "description": "A test task with all fields",
                "task_type": "project",
                "priority": "medium",
                "complexity": "medium",
                "impact_size": "pebbles",
                "estimated_duration": 30,
                "due_date": "2025-06-20"
            }
        },
        {
            "name": "Task with project_id",
            "payload": {
                "title": "Task with Project",
                "impact_size": "rock",
                "project_id": 1
            }
        },
        {
            "name": "Frontend-like payload",
            "payload": {
                "title": "Frontend Test Task",
                "description": "Testing from frontend format",
                "priority": "medium",
                "task_type": "project",
                "impact_size": "pebbles",
                "estimated_duration": 45,
                "due_date": "2025-06-20"
            }
        }
    ]
    
    print("🧪 Testing Task Creation API")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print(f"📤 Payload: {json.dumps(test_case['payload'], indent=2)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/tasks",
                json=test_case['payload'],
                headers=headers
            )
            
            print(f"📥 Status Code: {response.status_code}")
            
            if response.status_code == 422:
                print("❌ Validation Error (422):")
                try:
                    error_detail = response.json()
                    print(f"   Details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"   Raw response: {response.text}")
            elif response.status_code == 401:
                print("🔐 Authentication required (401)")
            elif response.status_code == 200 or response.status_code == 201:
                print("✅ Success!")
                try:
                    result = response.json()
                    print(f"   Created task ID: {result.get('id', 'N/A')}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_task_creation()
