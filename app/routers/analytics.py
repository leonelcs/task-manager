from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard", summary="Get ADHD analytics dashboard")
async def get_dashboard():
    """
    Get comprehensive analytics dashboard with ADHD-focused insights.
    
    **Analytics Include:**
    - Task completion patterns
    - Energy level correlations
    - Productivity insights
    - Habit formation tracking
    - Dopamine reward effectiveness
    """
    return {
        "overview": {
            "today": {
                "tasks_completed": 3,
                "tasks_pending": 2,
                "energy_level": "medium",
                "focus_sessions": 2,
                "break_compliance": 85  # percentage
            },
            "this_week": {
                "tasks_completed": 18,
                "average_completion_rate": 72,
                "best_day": "Tuesday",
                "productivity_trend": "improving"
            }
        },
        "adhd_insights": {
            "patterns": [
                "🌅 You're 40% more productive in the morning",
                "🎯 Tasks under 30 minutes have 90% completion rate",
                "🔄 Tuesday is your most consistent day",
                "⚡ You maintain focus best with 25-minute work blocks"
            ],
            "recommendations": [
                "Schedule important tasks between 8-10 AM",
                "Break large tasks into 25-minute chunks",
                "Use Tuesday energy for challenging projects",
                "Take breaks every 25 minutes to maintain focus"
            ]
        },
        "dopamine_stats": {
            "rewards_earned_today": 5,
            "streak_bonus": 3,
            "celebration_moments": 8,
            "motivation_level": "high"
        }
    }

@router.get("/patterns", summary="Get behavioral patterns analysis")
async def get_patterns(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze")
):
    """
    Get detailed behavioral patterns analysis for ADHD management.
    
    **Pattern Analysis:**
    - Energy level fluctuations
    - Task completion timing
    - Procrastination triggers
    - Hyperfocus episodes
    - Break effectiveness
    """
    return {
        "analysis_period": f"Last {days} days",
        "energy_patterns": {
            "peak_hours": ["08:00-10:00", "16:00-17:30"],
            "low_energy_periods": ["13:00-15:00", "20:00-22:00"],
            "average_focus_duration": 28,  # minutes
            "best_focus_days": ["Tuesday", "Wednesday", "Thursday"]
        },
        "task_patterns": {
            "completion_by_type": {
                "routine": 85,
                "project": 65,
                "maintenance": 75,
                "emergency": 95
            },
            "completion_by_time": {
                "morning": 78,
                "afternoon": 55,
                "evening": 45
            },
            "procrastination_triggers": [
                "Tasks longer than 45 minutes",
                "Unclear task descriptions",
                "Low energy + high complexity",
                "Multiple urgent tasks"
            ]
        },
        "focus_analysis": {
            "hyperfocus_episodes": 12,
            "average_hyperfocus_duration": 3.5,  # hours
            "hyperfocus_recovery_time": 45,  # minutes
            "focus_session_success_rate": 72
        },
        "recommendations": [
            "🎯 Schedule complex tasks during peak energy hours",
            "⏰ Limit single tasks to 30 minutes max",
            "🔄 Build in recovery time after hyperfocus sessions",
            "📝 Always clarify task requirements before starting"
        ]
    }

@router.get("/progress", summary="Get progress tracking")
async def get_progress():
    """
    Get detailed progress tracking with ADHD-friendly metrics.
    
    **Progress Metrics:**
    - Habit formation progress
    - Consistency tracking
    - Difficulty adaptation
    - Goal achievement
    - Personal growth indicators
    """
    return {
        "habit_tracking": {
            "morning_routine": {
                "current_streak": 5,
                "longest_streak": 12,
                "completion_rate": 78,
                "trend": "improving"
            },
            "task_planning": {
                "current_streak": 3,
                "longest_streak": 8,
                "completion_rate": 65,
                "trend": "stable"
            },
            "break_taking": {
                "current_streak": 7,
                "longest_streak": 15,
                "completion_rate": 85,
                "trend": "excellent"
            }
        },
        "achievements": [
            {"title": "Morning Warrior", "description": "5-day morning routine streak", "earned": "2025-06-11"},
            {"title": "Break Master", "description": "Taking breaks 85% of the time", "earned": "2025-06-10"},
            {"title": "Task Crusher", "description": "Completed 3 tasks today", "earned": "2025-06-11"}
        ],
        "growth_indicators": {
            "executive_function": {
                "planning": 7.5,  # out of 10
                "organization": 6.8,
                "time_management": 7.2,
                "task_initiation": 6.5
            },
            "improvement_areas": [
                "Task initiation could improve with better energy matching",
                "Organization benefits from consistent daily tidying",
                "Time management is strong with break reminders"
            ]
        },
        "celebration": "🎉 You've completed 147 tasks total! That's incredible progress! 🚀"
    }

@router.get("/focus-sessions", summary="Get focus session analytics")
async def get_focus_sessions():
    """
    Get detailed analytics about focus sessions and deep work periods.
    
    **Focus Session Data:**
    - Session duration effectiveness
    - Break timing optimization
    - Hyperfocus pattern recognition
    - Attention span trends
    """
    return {
        "recent_sessions": [
            {
                "date": "2025-06-11",
                "start_time": "09:00",
                "duration": 25,
                "task_type": "routine",
                "effectiveness": 9,
                "break_taken": True
            },
            {
                "date": "2025-06-11",
                "start_time": "10:30",
                "duration": 45,
                "task_type": "project",
                "effectiveness": 7,
                "break_taken": True
            }
        ],
        "session_analytics": {
            "optimal_duration": 28,  # minutes
            "success_rate_by_duration": {
                "15_min": 95,
                "25_min": 90,
                "45_min": 70,
                "60_min": 45
            },
            "break_effectiveness": {
                "5_min_break": 85,
                "10_min_break": 90,
                "15_min_break": 75
            }
        },
        "insights": [
            "🎯 Your sweet spot is 25-30 minute focus sessions",
            "🔄 10-minute breaks give you the best recovery",
            "⚡ Morning sessions are 35% more effective",
            "📈 Your focus stamina is improving over time!"
        ]
    }
