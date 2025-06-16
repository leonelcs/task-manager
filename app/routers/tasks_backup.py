from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.task import Task, TaskPriority, TaskStatus, ADHDTaskType, ADHDImpactSize
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskComplete,
    TaskImpactClassification, TaskSuggestion
)

router = APIRouter()

@router.get("/impact-classification", response_model=TaskImpactClassification, summary="Get Rock/Pebbles/Sand classification guide")
async def get_impact_classification_guide():
    """
    Get detailed explanation of the Rock/Pebbles/Sand task classification system.
    
    **ADHD-Friendly Impact Classification:**
    - **Rocks**: Your biggest, most impactful tasks - limit to 1-2 per day
    - **Pebbles**: Important tasks that build momentum and support your rocks
    - **Sand**: Nice-to-have tasks that fill gaps but shouldn't dominate your schedule
    """
    return TaskImpactClassification()

@router.get("/", response_model=List[TaskListResponse], summary="Get all tasks")
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    task_type: Optional[ADHDTaskType] = Query(None, description="Filter by ADHD task type"),
    impact_size: Optional[ADHDImpactSize] = Query(None, description="Filter by Rock/Pebbles/Sand classification"),
    limit: int = Query(50, ge=1, le=100, description="Number of tasks to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks with optional filtering including Rock/Pebbles/Sand classification.
    
    **ADHD-Friendly Features:**
    - Limited results to prevent overwhelm
    - Status-based filtering for focus
    - Priority-based organization
    - Task type categorization
    - **NEW**: Rock/Pebbles/Sand impact classification for better prioritization
    """
    # Build query for user's tasks
    query = db.query(Task).filter(Task.created_by == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if task_type:
        query = query.filter(Task.task_type == task_type)
    if impact_size:
        query = query.filter(Task.impact_size == impact_size)
    
    # Sort by impact: Rocks first, then Pebbles, then Sand
    impact_order = {
        ADHDImpactSize.ROCK: 1,
        ADHDImpactSize.PEBBLES: 2,
        ADHDImpactSize.SAND: 3
    }
    
    # Order by impact size, then by created_at desc
    tasks = query.order_by(
        Task.impact_size,
        Task.created_at.desc()
    ).limit(limit).all()
    
    # Convert to response format
    task_responses = []
    for task in tasks:
        adhd_features = task.adhd_features or {}
        task_responses.append(TaskListResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            task_type=task.task_type,
            impact_size=task.impact_size,
            estimated_duration=task.estimated_duration,
            created_at=task.created_at.isoformat() if task.created_at else None,
            due_date=task.due_date.isoformat() if task.due_date else None,
            dopamine_reward=adhd_features.get("dopamine_reward", "🎉 Task completed!"),
            energy_level_required=adhd_features.get("energy_level_required", "medium")
        ))
    
    return task_responses
    
    return filtered_tasks[:limit]

@router.post("/", response_model=TaskResponse, summary="Create a new task")
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task with ADHD-specific features including Rock/Pebbles/Sand classification.
    
    **ADHD-Friendly Features:**
    - Automatic task breakdown suggestions
    - Dopamine reward assignment
    - Duration estimation with breaks
    - Priority assessment help
    - **NEW**: Rock/Pebbles/Sand impact classification guide
    
    **Impact Classification Tips:**
    - **Rock**: Choose 1-2 per day max - these are your big wins
    - **Pebbles**: Great for building momentum between rocks
    - **Sand**: Let these fill in naturally, don't let them crowd out rocks
    """
    # Create ADHD features based on task properties
    adhd_features = {
        "dopamine_reward": _get_impact_based_reward(task.impact_size),
        "break_reminder": True,
        "chunked": task.estimated_duration and task.estimated_duration > 45,
        "energy_level_required": _determine_energy_from_impact(task.impact_size),
        "best_time_of_day": _suggest_time_by_impact(task.impact_size),
        "focus_duration": 25,
        "hyperfocus_risk": task.impact_size == ADHDImpactSize.ROCK,
        "collaboration_boost": False
    }
    
    # Create new task
    db_task = Task(
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        priority=task.priority,
        status=TaskStatus.TODO,
        complexity=getattr(task, 'complexity', 'medium'),
        impact_size=task.impact_size,
        estimated_duration=task.estimated_duration,
        due_date=task.due_date,
        project_id=task.project_id,
        created_by=current_user.id,
        adhd_features=adhd_features,
        completion_history=[],
        focus_sessions=[]
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Return the created task
    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        task_type=db_task.task_type,
        priority=db_task.priority,
        status=db_task.status,
        complexity=db_task.complexity,
        impact_size=db_task.impact_size,
        estimated_duration=db_task.estimated_duration,
        due_date=db_task.due_date.isoformat() if db_task.due_date else None,
        project_id=db_task.project_id,
        created_by=db_task.created_by,
        assigned_user_id=db_task.assigned_user_id,
        actual_duration=db_task.actual_duration,
        created_at=db_task.created_at.isoformat() if db_task.created_at else None,
        updated_at=db_task.updated_at.isoformat() if db_task.updated_at else None,
        completed_at=db_task.completed_at.isoformat() if db_task.completed_at else None,
        adhd_features=db_task.adhd_features,
        completion_history=db_task.completion_history,
        focus_sessions=db_task.focus_sessions
    )

def _get_impact_based_reward(impact_size: ADHDImpactSize) -> str:
    """Generate dopamine reward based on impact size."""
    rewards = {
        ADHDImpactSize.ROCK: "🏔️ MASSIVE IMPACT! You're tackling the big stuff!",
        ADHDImpactSize.PEBBLES: "⚡ Solid progress! Building great momentum!",
        ADHDImpactSize.SAND: "✨ Nice touch! Every detail matters!"
    }
    return rewards[impact_size]

def _determine_energy_from_impact(impact_size: ADHDImpactSize) -> str:
    """Determine energy requirement based on impact size."""
    energy_map = {
        ADHDImpactSize.ROCK: "high",      # Rocks need your best energy
        ADHDImpactSize.PEBBLES: "medium", # Pebbles are manageable
        ADHDImpactSize.SAND: "low"        # Sand can be done anytime
    }
    return energy_map[impact_size]

def _suggest_time_by_impact(impact_size: ADHDImpactSize) -> str:
    """Suggest optimal time based on impact size."""
    time_map = {
        ADHDImpactSize.ROCK: "morning",    # Rocks deserve peak hours
        ADHDImpactSize.PEBBLES: "flexible", # Pebbles fit anywhere
        ADHDImpactSize.SAND: "afternoon"   # Sand fills the gaps
    }
    return time_map[impact_size]

@router.get("/{task_id}", response_model=TaskResponse, summary="Get a specific task")
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID with full ADHD support details including impact classification.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.created_by == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        priority=task.priority,
        status=task.status,
        complexity=task.complexity,
        impact_size=task.impact_size,
        estimated_duration=task.estimated_duration,
        due_date=task.due_date.isoformat() if task.due_date else None,
        project_id=task.project_id,
        created_by=task.created_by,
        assigned_user_id=task.assigned_user_id,
        actual_duration=task.actual_duration,
        created_at=task.created_at.isoformat() if task.created_at else None,
        updated_at=task.updated_at.isoformat() if task.updated_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
        adhd_features=task.adhd_features or {},
        completion_history=task.completion_history or [],
        focus_sessions=task.focus_sessions or []
    )
                {"date": "2025-06-12", "duration": 60, "quality": "good"},
                {"date": "2025-06-13", "duration": 45, "quality": "excellent"}
            ]
        }
    
    raise HTTPException(status_code=404, detail="Task not found")

@router.put("/{task_id}/complete", summary="Mark task as completed")
async def complete_task(
    task_id: int, 
    completion_data: Optional[TaskComplete] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a task as completed with ADHD-friendly celebration including impact-based rewards.
    
    **ADHD-Friendly Features:**
    - Impact-specific dopamine rewards
    - Progress tracking
    - Streak counting
    - Celebration messages tailored to Rock/Pebbles/Sand
    """
    # Get the task from database
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.created_by == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status == TaskStatus.COMPLETED:
        return {"message": "Task is already completed!"}
    
    # Update task status
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    
    if completion_data and completion_data.actual_duration:
        task.actual_duration = completion_data.actual_duration
    
    # Update completion history
    completion_history = task.completion_history or []
    completion_entry = {
        "date": task.completed_at.isoformat() if task.completed_at else None,
        "completed": True,
        "time_taken": completion_data.actual_duration if completion_data else None,
        "notes": completion_data.completion_notes if completion_data else None
    }
    completion_history.append(completion_entry)
    task.completion_history = completion_history
    
    db.commit()
    db.refresh(task)
    
    # Generate impact-specific rewards
    impact_rewards = {
        ADHDImpactSize.ROCK: "🏔️ INCREDIBLE! You crushed a ROCK task! This is HUGE progress! 🚀",
        ADHDImpactSize.PEBBLES: "⚡ Solid progress! Building great momentum! 💪",
        ADHDImpactSize.SAND: "✨ Nice detail work! Every little bit adds up! 🌟"
    }
    
    reward_message = impact_rewards.get(task.impact_size, "🎉 Task completed!")
    
    celebration_level = {
        ADHDImpactSize.ROCK: "epic",
        ADHDImpactSize.PEBBLES: "high", 
        ADHDImpactSize.SAND: "medium"
    }[task.impact_size]
    
    # Calculate user's current streak (simplified)
    recent_completed_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED
    ).order_by(Task.completed_at.desc()).limit(10).all()
    
    current_streak = len([t for t in recent_completed_tasks if t.completed_at and 
                         (task.completed_at - t.completed_at).days <= 1])
    
    return {
        "message": f"🎉 Awesome! Task '{task.title}' completed!",
        "impact_type": task.impact_size.value,
        "dopamine_boost": reward_message,
        "celebration_level": celebration_level,
        "streak_info": {
            "current_streak": current_streak,
            "impact_streak": f"Great {task.impact_size.value} task completed!"
        },
        "next_suggestion": _get_post_completion_suggestion(task.impact_size.value),
        "actual_duration": task.actual_duration,
        "completion_notes": completion_data.completion_notes if completion_data else None
    }

def _get_post_completion_suggestion(impact_type: str) -> str:
    """Get suggestion based on what type of task was just completed."""
    suggestions = {
        "rock": "🏔️ AMAZING! Take a real break - you earned it! Consider a walk or some fresh air to celebrate this major win!",
        "pebbles": "⚡ Great momentum! Perfect time for another pebble task or a quick 5-minute celebration break!",
        "sand": "✨ Nice tidying up! Ready for something bigger, or want to knock out another quick sand task?"
    }
    return suggestions[impact_type]

@router.get("/by-impact/{impact_size}", response_model=List[TaskListResponse], summary="Get tasks by impact classification")
async def get_tasks_by_impact(
    impact_size: ADHDImpactSize,
    limit: int = Query(10, ge=1, le=50, description="Number of tasks to return")
):
    """
    Get tasks filtered specifically by Rock/Pebbles/Sand classification.
    
    **ADHD Impact Strategy:**
    - **Rocks**: Focus on 1-2 per day maximum - schedule during peak energy
    - **Pebbles**: Great for building momentum - perfect between rocks
    - **Sand**: Fill in gaps naturally - don't let these dominate your day
    """
    # Mock filtered data based on impact size
    all_tasks = [
        {
            "id": 2,
            "title": "Complete quarterly performance review",
            "task_type": ADHDTaskType.PROJECT,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.IN_PROGRESS,
            "impact_size": ADHDImpactSize.ROCK,
            "estimated_duration": 180,
            "due_date": "2025-06-15T17:00:00Z",
            "created_at": "2025-06-10T14:00:00Z",
            "dopamine_reward": "🏔️ MASSIVE IMPACT! You're tackling the big stuff!",
            "energy_level_required": "high"
        },
        {
            "id": 1,
            "title": "Morning routine checklist",
            "task_type": ADHDTaskType.ROUTINE,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.TODO,
            "impact_size": ADHDImpactSize.PEBBLES,
            "estimated_duration": 30,
            "due_date": "2025-06-11T09:00:00Z",
            "created_at": "2025-06-11T08:00:00Z",
            "dopamine_reward": "⚡ Solid progress! Building great momentum!",
            "energy_level_required": "low"
        },
        {
            "id": 3,
            "title": "Organize desk drawer",
            "task_type": ADHDTaskType.MAINTENANCE,
            "priority": TaskPriority.LOW,
            "status": TaskStatus.TODO,
            "impact_size": ADHDImpactSize.SAND,
            "estimated_duration": 15,
            "due_date": None,
            "created_at": "2025-06-11T10:00:00Z",
            "dopamine_reward": "✨ Nice touch! Every detail matters!",
            "energy_level_required": "low"
        }
    ]
    
    filtered_tasks = [task for task in all_tasks if task["impact_size"] == impact_size]
    
    return filtered_tasks[:limit]

@router.get("/suggestions/ai", response_model=List[TaskSuggestion], summary="Get AI-powered task suggestions")
async def get_ai_suggestions(
    current_energy: str = Query("medium", description="Current energy level: low, medium, high"),
    available_time: int = Query(30, ge=5, le=180, description="Available time in minutes")
):
    """
    Get AI-powered task suggestions based on Rock/Pebbles/Sand classification and ADHD patterns.
    
    **ADHD-Specific AI Features:**
    - Energy level matching with impact classification
    - Time-of-day optimization for different impact sizes
    - Difficulty adjustment based on current state
    - Impact-focused motivation boosting
    """
    
    suggestions = []
    
    # Rock suggestions for high energy / long time
    if current_energy == "high" and available_time >= 90:
        suggestions.append({
            "suggested_task": "Tackle your biggest, most important project task",
            "impact_size": ADHDImpactSize.ROCK,
            "reasoning": "High energy + good time block = perfect for ROCK tasks! This is when you do your most impactful work.",
            "confidence": 0.9,
            "adhd_benefits": ["Maximum impact", "Uses peak energy wisely", "Major dopamine payoff", "Moves the needle"],
            "estimated_duration": min(available_time, 120)
        })
    
    # Pebbles suggestions for medium energy
    if current_energy in ["medium", "high"] and available_time >= 15:
        suggestions.append({
            "suggested_task": "Complete an important but manageable task from your list",
            "impact_size": ADHDImpactSize.PEBBLES,
            "reasoning": "Perfect energy and time for meaningful progress! Pebbles build great momentum.",
            "confidence": 0.85,
            "adhd_benefits": ["Builds momentum", "Solid progress", "Good dopamine hit", "Supports bigger goals"],
            "estimated_duration": min(available_time, 45)
        })
    
    # Sand suggestions for low energy or short time
    if available_time <= 30 or current_energy == "low":
        suggestions.append({
            "suggested_task": "Organize something small or handle quick administrative tasks",
            "impact_size": ADHDImpactSize.SAND, 
            "reasoning": "Great for low energy or short time slots! Still feels productive without being overwhelming.",
            "confidence": 0.75,
            "adhd_benefits": ["Low pressure", "Easy completion", "Feels productive", "Fills time well"],
            "estimated_duration": min(available_time, 20)
        })
    
    # Fallback suggestion
    if not suggestions:
        suggestions.append({
            "suggested_task": "Take a mindful 5-minute break to reset and plan",
            "impact_size": ADHDImpactSize.SAND,
            "reasoning": "Sometimes the best task is no task - give your brain a moment to recharge!",
            "confidence": 0.8,
            "adhd_benefits": ["Mental reset", "Prevents burnout", "Improves next task performance", "Self-care"],
            "estimated_duration": 5
        })
    
    return suggestions
