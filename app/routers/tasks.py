from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from enum import Enum

router = APIRouter()

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"

class ADHDTaskType(str, Enum):
    ROUTINE = "routine"  # Daily habits
    PROJECT = "project"  # Larger goals
    MAINTENANCE = "maintenance"  # Regular upkeep
    EMERGENCY = "emergency"  # Urgent items
    HYPERFOCUS = "hyperfocus"  # Deep work sessions

@router.get("/", summary="Get all tasks")
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    task_type: Optional[ADHDTaskType] = Query(None, description="Filter by ADHD task type"),
    limit: int = Query(50, ge=1, le=100, description="Number of tasks to return")
):
    """
    Get all tasks with optional filtering.
    
    **ADHD-Friendly Features:**
    - Limited results to prevent overwhelm
    - Status-based filtering for focus
    - Priority-based organization
    - Task type categorization
    """
    # Mock data for now
    tasks = [
        {
            "id": 1,
            "title": "Morning routine checklist",
            "description": "Complete morning routine: medication, breakfast, vitamins",
            "status": TaskStatus.TODO,
            "priority": TaskPriority.HIGH,
            "task_type": ADHDTaskType.ROUTINE,
            "estimated_duration": 30,
            "created_at": "2025-06-11T08:00:00Z",
            "due_date": "2025-06-11T09:00:00Z",
            "adhd_features": {
                "dopamine_reward": "🌟 Great start to the day!",
                "break_reminder": True,
                "chunked": True
            }
        },
        {
            "id": 2,
            "title": "Project: Organize workspace",
            "description": "Break down and organize the workspace into manageable sections",
            "status": TaskStatus.IN_PROGRESS,
            "priority": TaskPriority.MEDIUM,
            "task_type": ADHDTaskType.PROJECT,
            "estimated_duration": 120,
            "created_at": "2025-06-10T14:00:00Z",
            "due_date": "2025-06-12T17:00:00Z",
            "adhd_features": {
                "dopamine_reward": "🎯 Making progress on the big picture!",
                "break_reminder": True,
                "chunked": True,
                "subtasks": [
                    "Clear desk surface",
                    "Organize cables",
                    "Sort papers",
                    "Arrange supplies"
                ]
            }
        }
    ]
    
    # Apply filters
    filtered_tasks = tasks
    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
    if priority:
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]
    if task_type:
        filtered_tasks = [t for t in filtered_tasks if t["task_type"] == task_type]
    
    return {
        "tasks": filtered_tasks[:limit],
        "total": len(filtered_tasks),
        "adhd_tip": "🧠 Remember: Focus on one task at a time. You've got this!"
    }

@router.post("/", summary="Create a new task")
async def create_task():
    """
    Create a new task with ADHD-specific features.
    
    **ADHD-Friendly Features:**
    - Automatic task breakdown suggestions
    - Dopamine reward assignment
    - Duration estimation with breaks
    - Priority assessment help
    """
    return {
        "message": "Task creation endpoint - to be implemented",
        "adhd_tip": "🎯 Break large tasks into smaller, manageable chunks!"
    }

@router.get("/{task_id}", summary="Get a specific task")
async def get_task(task_id: int):
    """
    Get a specific task by ID with full ADHD support details.
    """
    if task_id == 1:
        return {
            "id": 1,
            "title": "Morning routine checklist",
            "description": "Complete morning routine: medication, breakfast, vitamins",
            "status": TaskStatus.TODO,
            "priority": TaskPriority.HIGH,
            "task_type": ADHDTaskType.ROUTINE,
            "estimated_duration": 30,
            "created_at": "2025-06-11T08:00:00Z",
            "due_date": "2025-06-11T09:00:00Z",
            "adhd_features": {
                "dopamine_reward": "🌟 Great start to the day!",
                "break_reminder": True,
                "chunked": True,
                "energy_level_required": "low",
                "best_time_of_day": "morning",
                "focus_duration": 10
            },
            "completion_history": [
                {"date": "2025-06-10", "completed": True, "time_taken": 25},
                {"date": "2025-06-09", "completed": True, "time_taken": 35},
                {"date": "2025-06-08", "completed": False, "reason": "overslept"}
            ]
        }
    
    raise HTTPException(status_code=404, detail="Task not found")

@router.put("/{task_id}/complete", summary="Mark task as completed")
async def complete_task(task_id: int):
    """
    Mark a task as completed with ADHD-friendly celebration.
    
    **ADHD-Friendly Features:**
    - Instant dopamine reward
    - Progress tracking
    - Streak counting
    - Celebration messages
    """
    return {
        "message": f"🎉 Awesome! Task {task_id} completed!",
        "dopamine_boost": "🚀 You're on fire! Keep the momentum going!",
        "streak_info": {
            "current_streak": 3,
            "longest_streak": 7,
            "streak_bonus": "🔥 Hot streak bonus!"
        },
        "next_suggestion": "Take a 5-minute break to celebrate this win!"
    }

@router.get("/suggestions/ai", summary="Get AI-powered task suggestions")
async def get_ai_suggestions():
    """
    Get AI-powered task suggestions based on historical data and ADHD patterns.
    
    **ADHD-Specific AI Features:**
    - Energy level matching
    - Time-of-day optimization
    - Difficulty adjustment
    - Motivation boosting
    """
    return {
        "suggestions": [
            {
                "task": "Quick 10-minute room tidy",
                "reason": "Your energy is high right now, perfect for a quick win!",
                "confidence": 0.85,
                "adhd_benefits": ["Quick dopamine hit", "Visible progress", "Low commitment"]
            },
            {
                "task": "Review tomorrow's schedule",
                "reason": "Evening planning reduces morning anxiety",
                "confidence": 0.78,
                "adhd_benefits": ["Reduces decision fatigue", "Improves sleep", "Morning routine prep"]
            }
        ],
        "energy_level": "medium",
        "optimal_task_duration": "15-30 minutes",
        "motivation_message": "💪 You're doing great! Small consistent actions lead to big results."
    }
