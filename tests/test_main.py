"""
Test file for the ADHD Task Manager API.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "ADHD Task Manager API" in data["message"]
    assert data["status"] == "running"

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "adhd-task-manager-api"

def test_get_tasks():
    """Test getting tasks with ADHD features."""
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "adhd_tip" in data
    assert len(data["tasks"]) > 0
    
    # Check ADHD-specific features in tasks
    first_task = data["tasks"][0]
    assert "adhd_features" in first_task
    assert "dopamine_reward" in first_task["adhd_features"]

def test_get_specific_task():
    """Test getting a specific task by ID."""
    response = client.get("/api/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "adhd_features" in data
    assert "completion_history" in data

def test_task_not_found():
    """Test getting a non-existent task."""
    response = client.get("/api/tasks/999")
    assert response.status_code == 404

def test_complete_task():
    """Test completing a task with ADHD celebrations."""
    response = client.put("/api/tasks/1/complete")
    assert response.status_code == 200
    data = response.json()
    assert "dopamine_boost" in data
    assert "streak_info" in data
    assert "🎉" in data["message"]

def test_ai_suggestions():
    """Test AI-powered task suggestions."""
    response = client.get("/api/tasks/suggestions/ai")
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert "energy_level" in data
    assert "motivation_message" in data
    assert len(data["suggestions"]) > 0

def test_user_profile():
    """Test getting user profile with ADHD settings."""
    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert "adhd_profile" in data
    assert "energy_patterns" in data["adhd_profile"]
    assert "focus_duration" in data["adhd_profile"]
    assert "preferences" in data["adhd_profile"]

def test_analytics_dashboard():
    """Test ADHD analytics dashboard."""
    response = client.get("/api/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "adhd_insights" in data
    assert "dopamine_stats" in data
    assert "patterns" in data["adhd_insights"]

def test_behavioral_patterns():
    """Test behavioral patterns analysis."""
    response = client.get("/api/analytics/patterns")
    assert response.status_code == 200
    data = response.json()
    assert "energy_patterns" in data
    assert "task_patterns" in data
    assert "focus_analysis" in data
    assert "recommendations" in data

if __name__ == "__main__":
    pytest.main([__file__])
