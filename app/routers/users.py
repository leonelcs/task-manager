from fastapi import APIRouter, HTTPException
from typing import List, Optional

router = APIRouter()

@router.get("/", summary="Get user profile")
async def get_user_profile():
    """
    Get user profile with ADHD-specific preferences and settings.
    """
    return {
        "id": 1,
        "username": "adhd_warrior",
        "email": "user@example.com",
        "adhd_profile": {
            "energy_patterns": {
                "morning": "high",
                "afternoon": "medium",
                "evening": "low"
            },
            "focus_duration": {
                "optimal": 25,  # minutes
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
                "overwhelm_threshold": 5,  # max tasks visible at once
                "complexity_limit": "medium",
                "notification_frequency": "gentle"
            }
        },
        "stats": {
            "tasks_completed_today": 3,
            "current_streak": 5,
            "longest_streak": 12,
            "total_tasks_completed": 147
        }
    }

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
async def get_energy_log():
    """
    Get historical energy level data for pattern recognition.
    
    This helps the AI understand when you're most productive
    and suggests optimal times for different types of tasks.
    """
    return {
        "energy_log": [
            {"date": "2025-06-11", "time": "08:00", "level": "high", "duration": 90},
            {"date": "2025-06-11", "time": "10:30", "level": "medium", "duration": 60},
            {"date": "2025-06-11", "time": "14:00", "level": "low", "duration": 120},
            {"date": "2025-06-11", "time": "16:30", "level": "medium", "duration": 45},
        ],
        "patterns": {
            "best_focus_time": "08:00-09:30",
            "typical_afternoon_dip": "13:00-15:00",
            "secondary_peak": "16:00-17:00"
        },
        "insights": [
            "💡 You're most productive in the morning - schedule important tasks then!",
            "🔄 Your energy typically dips after lunch - perfect time for easy tasks.",
            "⚡ You get a second wind around 4 PM - great for creative work!"
        ]
    }

@router.post("/energy-log", summary="Log current energy level")
async def log_energy_level():
    """
    Log current energy level for AI pattern recognition.
    
    **Energy Levels:**
    - **High**: Ready for complex, challenging tasks
    - **Medium**: Good for routine tasks and light planning
    - **Low**: Perfect for easy, mindless tasks or rest
    """
    return {
        "message": "Energy level logged! 📊",
        "ai_suggestion": "Based on your current energy, here are some good task options...",
        "thank_you": "Thanks for helping the AI learn your patterns! 🤖✨"
    }
