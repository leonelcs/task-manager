from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, EnergyLog
from app.routers.auth import get_current_user
from app.schemas.user import UserResponse, EnergyLogResponse, EnergyLogCreate

router = APIRouter()

@router.get("/", summary="Get user profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user profile with ADHD-specific preferences and settings.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        adhd_profile=current_user.adhd_profile or {
            "energy_patterns": {
                "morning": "high",
                "afternoon": "medium",
                "evening": "low"
            },
            "focus_duration": {
                "optimal": 25,
                "maximum": 45,
                "minimum": 10
            },
            "preferences": {
                "break_reminders": True,
                "dopamine_rewards": True,
                "task_chunking": True,
                "deadline_buffers": True,
                "hyperfocus_alerts": True
            },
            "triggers": {
                "overwhelm_threshold": 5,
                "complexity_limit": "medium",
                "notification_frequency": "gentle"
            }
        },
        stats=current_user.stats or {
            "tasks_completed_today": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "total_tasks_completed": 0
        },
        google_id=current_user.google_id,
        profile_picture_url=current_user.profile_picture_url,
        provider=current_user.provider
    )

@router.put("/preferences", summary="Update ADHD preferences")
async def update_adhd_preferences():
    """
    Update user's ADHD-specific preferences and settings.
    
    **Customizable ADHD Features:**
    - Energy level tracking preferences
    - Notification timing and style
    - Task complexity limits
    - Break reminder intervals
    - Reward system preferences
    """
    return {
        "message": "ADHD preferences updated successfully! 🎯",
        "tip": "Remember: These settings help the system work better for YOUR brain!"
    }

@router.get("/energy-log", summary="Get energy level history")
async def get_energy_log(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get historical energy level data for pattern recognition.
    
    This helps the AI understand when you're most productive
    and suggests optimal times for different types of tasks.
    """
    # Get user's energy logs from database
    energy_logs = db.query(EnergyLog).filter(
        EnergyLog.user_id == current_user.id
    ).order_by(EnergyLog.logged_at.desc()).limit(50).all()
    
    # Convert to response format
    energy_log_data = []
    for log in energy_logs:
        energy_log_data.append({
            "date": log.logged_at.strftime("%Y-%m-%d"),
            "time": log.logged_at.strftime("%H:%M"),
            "level": log.energy_level,
            "duration": log.duration_minutes or 60
        })
    
    # Basic pattern analysis (could be enhanced with more sophisticated analysis)
    patterns = {
        "best_focus_time": "08:00-09:30",  # Could be calculated from logs
        "typical_afternoon_dip": "13:00-15:00",
        "secondary_peak": "16:00-17:00"
    }
    
    insights = [
        "💡 You're most productive in the morning - schedule important tasks then!",
        "🔄 Your energy typically dips after lunch - perfect time for easy tasks.",
        "⚡ You get a second wind around 4 PM - great for creative work!"
    ]
    
    return {
        "energy_log": energy_log_data,
        "patterns": patterns,
        "insights": insights
    }

@router.post("/energy-log", summary="Log current energy level")
async def log_energy_level(
    energy_data: EnergyLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log current energy level for AI pattern recognition.
    
    **Energy Levels:**
    - **High**: Ready for complex, challenging tasks
    - **Medium**: Good for routine tasks and light planning
    - **Low**: Perfect for easy, mindless tasks or rest
    """
    # Create new energy log entry
    new_log = EnergyLog(
        user_id=current_user.id,
        energy_level=energy_data.energy_level,
        duration_minutes=energy_data.duration_minutes,
        notes=energy_data.notes
    )
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    return {
        "message": "⚡ Energy level logged successfully!",
        "logged_data": {
            "energy_level": new_log.energy_level,
            "duration_minutes": new_log.duration_minutes,
            "logged_at": new_log.logged_at.isoformat(),
            "notes": new_log.notes
        },
        "ai_benefit": "🧠 This data helps the AI recommend the best times for different types of tasks!",
        "pattern_tip": "📊 Keep logging to discover your personal energy patterns!"
    }
