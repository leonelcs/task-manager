from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Optional, Dict
from datetime import datetime
from app.database import get_db
from app.models.task import Task, TaskPriority, TaskStatus, ADHDTaskType, ADHDImpactSize
from app.models.user import User
from app.models.project import Project
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
            created_at=task.created_at,
            due_date=task.due_date,
            dopamine_reward=adhd_features.get("dopamine_reward", "🎉 Task completed!"),
            energy_level_required=adhd_features.get("energy_level_required", "medium")
        ))
    
    return task_responses

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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 80)
        logger.info("🎯 TASK CREATION STARTED")
        logger.info("=" * 80)
        logger.info(f"📥 Request from user: {current_user.id} ({current_user.email})")
        logger.info(f"📋 Task data received:")
        logger.info(f"   - Title: {task.title}")
        logger.info(f"   - Description: {task.description}")
        logger.info(f"   - Task Type: {task.task_type}")
        logger.info(f"   - Priority: {task.priority}")
        logger.info(f"   - Impact Size: {task.impact_size}")
        logger.info(f"   - Estimated Duration: {task.estimated_duration}")
        logger.info(f"   - Due Date: {task.due_date}")
        logger.info(f"   - Project ID: {task.project_id}")
        
        # Validate required fields
        if not task.title or task.title.strip() == "":
            logger.error("❌ Task creation failed: Title is required")
            raise HTTPException(status_code=400, detail="Task title is required")
        
        if not task.impact_size:
            logger.error("❌ Task creation failed: Impact size is required")
            raise HTTPException(status_code=400, detail="Impact size is required")
        
        logger.info("✅ Basic validation passed")
        
        # Create ADHD features based on task properties
        logger.info("🧠 Creating ADHD features...")
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
        logger.info(f"🧠 ADHD features created: {adhd_features}")
        
        # Validate project_id if provided
        if task.project_id:
            logger.info(f"🔍 Validating project ID: {task.project_id}")
            project = db.query(Project).filter(Project.id == task.project_id).first()
            if not project:
                logger.error(f"❌ Project not found: {task.project_id}")
                raise HTTPException(status_code=400, detail=f"Project with ID {task.project_id} not found")
            logger.info(f"✅ Project validated: {project.name}")
        
        # Create new task
        logger.info("💾 Creating task object...")
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
        logger.info("✅ Task object created successfully")
        
        # Database operations
        logger.info("💾 Adding task to database...")
        db.add(db_task)
        logger.info("💾 Committing transaction...")
        db.commit()
        logger.info("💾 Refreshing task object...")
        db.refresh(db_task)
        logger.info(f"✅ Task saved with ID: {db_task.id}")
        
    except HTTPException as he:
        logger.error(f"❌ HTTP Exception during task creation: {he.detail}")
        db.rollback()
        raise he
    except Exception as e:
        logger.error(f"❌ Unexpected error during task creation: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Stack trace: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    logger.info("🎉 Task creation completed successfully!")
    
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
        due_date=db_task.due_date,
        project_id=db_task.project_id,
        created_by=db_task.created_by,
        assigned_user_id=db_task.assigned_user_id,
        actual_duration=db_task.actual_duration,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at,
        completed_at=db_task.completed_at,
        adhd_features=db_task.adhd_features,
        completion_history=db_task.completion_history,
        focus_sessions=db_task.focus_sessions
    )

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
        due_date=task.due_date,
        project_id=task.project_id,
        created_by=task.created_by,
        assigned_user_id=task.assigned_user_id,
        actual_duration=task.actual_duration,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        adhd_features=task.adhd_features or {},
        completion_history=task.completion_history or [],
        focus_sessions=task.focus_sessions or []
    )

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

@router.put("/{task_id}", response_model=TaskResponse, summary="Update a task")
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a task with ADHD-friendly features and impact classification.
    
    **ADHD-Friendly Features:**
    - Change impact classification (Rock/Pebbles/Sand) as priorities shift
    - Update dopamine rewards based on new impact size
    - Adjust energy requirements and timing suggestions
    - Maintain completion history and focus sessions
    """
    # Get the task from database
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.created_by == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task fields
    update_data = task_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(task, field):
            setattr(task, field, value)
    
    # Update ADHD features if impact size changed
    if task_update.impact_size and task_update.impact_size != task.impact_size:
        adhd_features = task.adhd_features or {}
        adhd_features.update({
            "dopamine_reward": _get_impact_based_reward(task_update.impact_size),
            "energy_level_required": _determine_energy_from_impact(task_update.impact_size),
            "best_time_of_day": _suggest_time_by_impact(task_update.impact_size),
            "hyperfocus_risk": task_update.impact_size == ADHDImpactSize.ROCK
        })
        task.adhd_features = adhd_features
    
    db.commit()
    db.refresh(task)
    
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
        due_date=task.due_date,
        project_id=task.project_id,
        created_by=task.created_by,
        assigned_user_id=task.assigned_user_id,
        actual_duration=task.actual_duration,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        adhd_features=task.adhd_features or {},
        completion_history=task.completion_history or [],
        focus_sessions=task.focus_sessions or []
    )

@router.delete("/{task_id}", summary="Delete a task")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task. For ADHD users, sometimes removing overwhelming tasks is the right choice.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.created_by == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": f"Task '{task.title}' has been deleted. Sometimes letting go is the right choice! ✨"}

@router.get("/suggestions/impact-balance", response_model=List[TaskSuggestion], summary="Get balanced task suggestions")
async def get_impact_balanced_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered suggestions for a balanced mix of Rock/Pebbles/Sand tasks.
    
    **ADHD-Friendly Approach:**
    - Analyzes your current task distribution
    - Suggests optimal Rock/Pebbles/Sand balance
    - Considers your energy patterns and completion history
    - Provides actionable next steps
    """
    # Get user's current tasks
    current_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
    ).all()
    
    # Analyze current distribution
    rock_count = len([t for t in current_tasks if t.impact_size == ADHDImpactSize.ROCK])
    pebbles_count = len([t for t in current_tasks if t.impact_size == ADHDImpactSize.PEBBLES])
    sand_count = len([t for t in current_tasks if t.impact_size == ADHDImpactSize.SAND])
    
    suggestions = []
    
    # Rock suggestions (if less than 2)
    if rock_count < 2:
        suggestions.append(TaskSuggestion(
            suggested_task="Identify your most impactful project or goal for this week",
            impact_size=ADHDImpactSize.ROCK,
            reasoning="You need 1-2 ROCK tasks to drive meaningful progress. These should be your highest-impact activities.",
            confidence=0.9,
            adhd_benefits=[
                "Creates clear focus and direction",
                "Provides massive dopamine reward when completed",
                "Prevents getting lost in less important tasks"
            ],
            estimated_duration=120
        ))
    
    # Pebbles suggestions (optimal balance)
    if pebbles_count < 3:
        suggestions.append(TaskSuggestion(
            suggested_task="Add 2-3 momentum-building tasks that support your main goals",
            impact_size=ADHDImpactSize.PEBBLES,
            reasoning="PEBBLES tasks provide steady progress and help maintain motivation between big wins.",
            confidence=0.8,
            adhd_benefits=[
                "Builds consistent momentum",
                "Provides regular dopamine hits",
                "Creates sense of forward progress"
            ],
            estimated_duration=45
        ))
    
    # Sand management (prevent overwhelm)
    if sand_count > 5:
        suggestions.append(TaskSuggestion(
            suggested_task="Review and delegate or eliminate some SAND tasks",
            impact_size=ADHDImpactSize.SAND,
            reasoning="Too many SAND tasks can create overwhelm and distract from high-impact work.",
            confidence=0.7,
            adhd_benefits=[
                "Reduces decision fatigue",
                "Frees mental space for important work",
                "Prevents perfectionism trap"
            ],
            estimated_duration=30
        ))
    
    return suggestions

@router.get("/daily/focus-recommendations", summary="Get daily task focus recommendations")
async def get_daily_focus_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ADHD-optimized daily task recommendations using Rock/Pebbles/Sand prioritization.
    
    **Perfect for ADHD Brains:**
    - Limits overwhelming choice overload
    - Suggests optimal Rock/Pebbles/Sand balance for today
    - Considers energy levels and time of day
    - Provides clear, actionable daily focus
    """
    # Get user's active tasks
    active_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
    ).order_by(
        Task.impact_size,  # Rocks first
        Task.priority.desc(),
        Task.created_at
    ).all()
    
    # Separate by impact size
    rocks = [t for t in active_tasks if t.impact_size == ADHDImpactSize.ROCK]
    pebbles = [t for t in active_tasks if t.impact_size == ADHDImpactSize.PEBBLES]
    sand = [t for t in active_tasks if t.impact_size == ADHDImpactSize.SAND]
    
    # ADHD-optimized daily recommendations
    recommendations = {
        "daily_focus": {
            "primary_rock": rocks[0].title if rocks else "Consider creating a ROCK task - your big win for today!",
            "rock_id": rocks[0].id if rocks else None,
            "backup_rock": rocks[1].title if len(rocks) > 1 else None,
            "backup_rock_id": rocks[1].id if len(rocks) > 1 else None
        },
        "momentum_builders": [
            {
                "title": p.title,
                "id": p.id,
                "estimated_duration": p.estimated_duration,
                "energy_required": p.adhd_features.get("energy_level_required", "medium") if p.adhd_features else "medium"
            }
            for p in pebbles[:3]  # Limit to 3 to prevent overwhelm
        ],
        "quick_wins": [
            {
                "title": s.title,
                "id": s.id,
                "estimated_duration": s.estimated_duration
            }
            for s in sand[:5] if s.estimated_duration and s.estimated_duration <= 15  # Only very quick sand tasks
        ],
        "adhd_coaching": {
            "morning_focus": "🌅 Start with your ROCK task while your brain is fresh and focused!",
            "energy_management": "⚡ Use PEBBLES tasks when your energy dips but you want to stay productive.",
            "afternoon_maintenance": "🌤️ SAND tasks are perfect for lower-energy periods - they still count as progress!",
            "overwhelm_prevention": "🛡️ Remember: You don't have to do everything today. Focus on your ROCK + a few PEBBLES."
        },
        "task_counts": {
            "total_rocks": len(rocks),
            "total_pebbles": len(pebbles),
            "total_sand": len(sand),
            "balance_status": _assess_task_balance(len(rocks), len(pebbles), len(sand))
        }
    }
    
    return recommendations

def _assess_task_balance(rock_count: int, pebbles_count: int, sand_count: int) -> Dict[str, str]:
    """Assess if the user's task distribution is ADHD-optimal."""
    if rock_count == 0:
        return {
            "status": "needs_rocks",
            "message": "🎯 You need at least 1 ROCK task - what's your biggest impact opportunity?",
            "priority": "high"
        }
    elif rock_count > 3:
        return {
            "status": "too_many_rocks", 
            "message": "🏔️ Too many ROCK tasks can cause overwhelm. Consider if some are really PEBBLES.",
            "priority": "medium"
        }
    elif sand_count > pebbles_count * 2:
        return {
            "status": "sand_heavy",
            "message": "🌊 Lots of SAND tasks - great for busy work, but ensure you're not avoiding your ROCKS!",
            "priority": "low"
        }
    else:
        return {
            "status": "balanced",
            "message": "✅ Nice balance! You have clear priorities without overwhelm.",
            "priority": "good"
        }

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

def _get_post_completion_suggestion(impact_type: str) -> str:
    """Get suggestion based on what type of task was just completed."""
    suggestions = {
        "rock": "🏔️ AMAZING! Take a real break - you earned it! Consider a walk or some fresh air to celebrate this major win!",
        "pebbles": "⚡ Great momentum! Perfect time for another pebble task or a quick 5-minute celebration break!",
        "sand": "✨ Nice tidying up! Ready for something bigger, or want to knock out another quick sand task?"
    }
    return suggestions[impact_type]
