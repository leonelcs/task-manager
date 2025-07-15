from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User, EnergyLog
from app.models.task import Task, TaskStatus, ADHDTaskType, ADHDImpactSize
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/dashboard", summary="Get ADHD analytics dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics dashboard with ADHD-focused insights.
    
    **Analytics Include:**
    - Task completion patterns
    - Energy level correlations
    - Productivity insights
    - Habit formation tracking
    - Dopamine reward effectiveness
    """
    # Get user's task statistics from database
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    # Today's stats
    tasks_completed_today = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        func.date(Task.completed_at) == today
    ).count()
    
    tasks_pending_today = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
        and_(
            Task.due_date.isnot(None),
            func.date(Task.due_date) >= today
        )
    ).count()
    
    # Week stats
    tasks_completed_week = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        Task.completed_at >= week_start
    ).count()
    
    total_tasks_week = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.created_at >= week_start
    ).count()
    
    average_completion_rate = (tasks_completed_week / total_tasks_week * 100) if total_tasks_week > 0 else 0
    
    # Get today's energy level
    latest_energy = db.query(EnergyLog).filter(
        EnergyLog.user_id == current_user.id,
        func.date(EnergyLog.logged_at) == today
    ).order_by(EnergyLog.logged_at.desc()).first()
    
    current_energy = latest_energy.energy_level if latest_energy else "medium"
    
    # Calculate best day of week from historical data
    weekly_completion_stats = db.query(
        extract('dow', Task.completed_at).label('day_of_week'),
        func.count(Task.id).label('completion_count')
    ).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        Task.completed_at >= datetime.now() - timedelta(days=30)
    ).group_by(extract('dow', Task.completed_at)).all()
    
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    best_day = "Tuesday"  # default
    if weekly_completion_stats:
        best_day_num = max(weekly_completion_stats, key=lambda x: x.completion_count).day_of_week
        best_day = day_names[int(best_day_num)]
    
    # Generate personalized insights based on data
    insights = []
    recommendations = []
    
    # Task duration analysis
    avg_duration_query = db.query(func.avg(Task.actual_duration)).filter(
        Task.created_by == current_user.id,
        Task.actual_duration.isnot(None),
        Task.status == TaskStatus.COMPLETED
    ).scalar()
    
    if avg_duration_query:
        avg_duration = int(avg_duration_query)
        if avg_duration <= 30:
            insights.append("🎯 You excel at short tasks - they have high completion rates")
            recommendations.append("Continue breaking large tasks into 30-minute chunks")
        else:
            insights.append("⏰ Your tasks tend to run longer than optimal for ADHD focus")
            recommendations.append("Try breaking tasks into smaller, more manageable pieces")
    
    # Energy pattern analysis
    if latest_energy:
        energy_tasks_today = db.query(Task).filter(
            Task.created_by == current_user.id,
            Task.status == TaskStatus.COMPLETED,
            func.date(Task.completed_at) == today
        ).count()
        
        if current_energy == "high" and energy_tasks_today > 0:
            insights.append("⚡ High energy correlates with productive days!")
            recommendations.append("Schedule your most challenging tasks during high energy periods")
    
    # Completion rate insights
    if average_completion_rate > 80:
        insights.append("🌟 Excellent task completion consistency this week")
    elif average_completion_rate > 60:
        insights.append("📈 Good progress - building momentum steadily")
        recommendations.append("Focus on maintaining your current pace")
    else:
        insights.append("🎯 Opportunity to improve task completion rate")
        recommendations.append("Consider reducing task complexity or breaking them down further")
    
    # Add Tuesday insight if it's the best day
    if best_day == "Tuesday":
        insights.append("🔄 Tuesday is your most productive day of the week")
        recommendations.append("Schedule your most important tasks on Tuesdays")
    
    return {
        "overview": {
            "today": {
                "tasks_completed": tasks_completed_today,
                "tasks_pending": tasks_pending_today,
                "energy_level": current_energy,
                "focus_sessions": 0,  # TODO: Implement focus session tracking
                "break_compliance": 85  # TODO: Calculate from session data
            },
            "this_week": {
                "tasks_completed": tasks_completed_week,
                "average_completion_rate": round(average_completion_rate),
                "best_day": best_day,
                "productivity_trend": "improving" if average_completion_rate > 60 else "stable"
            }
        },
        "adhd_insights": {
            "patterns": insights,
            "recommendations": recommendations
        },
        "dopamine_stats": {
            "rewards_earned_today": tasks_completed_today,  # Each completed task is a reward
            "streak_bonus": 0,  # TODO: Calculate completion streaks
            "celebration_moments": max(0, tasks_completed_today - 3),  # Bonus celebrations for >3 tasks
            "motivation_level": "high" if tasks_completed_today >= 3 else "medium" if tasks_completed_today >= 1 else "low"
        }
    }

@router.get("/patterns", summary="Get behavioral patterns analysis")
async def get_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
    start_date = datetime.now() - timedelta(days=days)
    
    # Energy patterns analysis
    energy_logs = db.query(EnergyLog).filter(
        EnergyLog.user_id == current_user.id,
        EnergyLog.logged_at >= start_date
    ).all()
    
    # Group energy logs by hour to find peak hours
    hour_energy_map = {}
    for log in energy_logs:
        hour = log.logged_at.hour
        if hour not in hour_energy_map:
            hour_energy_map[hour] = []
        # Convert energy level to numeric for analysis
        energy_value = {"low": 1, "medium": 2, "high": 3}.get(log.energy_level, 2)
        hour_energy_map[hour].append(energy_value)
    
    # Calculate average energy by hour
    avg_energy_by_hour = {}
    for hour, values in hour_energy_map.items():
        avg_energy_by_hour[hour] = sum(values) / len(values)
    
    # Find peak and low energy periods
    peak_hours = []
    low_energy_periods = []
    
    if avg_energy_by_hour:
        sorted_hours = sorted(avg_energy_by_hour.items(), key=lambda x: x[1], reverse=True)
        # Top 25% of hours are peak hours
        peak_count = max(1, len(sorted_hours) // 4)
        peak_hours = [f"{hour:02d}:00-{hour+1:02d}:00" for hour, _ in sorted_hours[:peak_count]]
        
        # Bottom 25% are low energy periods
        low_energy_periods = [f"{hour:02d}:00-{hour+1:02d}:00" for hour, _ in sorted_hours[-peak_count:]]
    else:
        # Default patterns if no energy data
        peak_hours = ["08:00-10:00", "16:00-17:30"]
        low_energy_periods = ["13:00-15:00", "20:00-22:00"]
    
    # Calculate average focus duration from task data
    completed_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        Task.actual_duration.isnot(None),
        Task.completed_at >= start_date
    ).all()
    
    avg_focus_duration = 28  # default
    if completed_tasks:
        durations = [task.actual_duration for task in completed_tasks if task.actual_duration]
        if durations:
            avg_focus_duration = int(sum(durations) / len(durations))
    
    # Find best focus days
    daily_completions = db.query(
        extract('dow', Task.completed_at).label('day_of_week'),
        func.count(Task.id).label('completion_count')
    ).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        Task.completed_at >= start_date
    ).group_by(extract('dow', Task.completed_at)).all()
    
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    best_focus_days = ["Tuesday", "Wednesday", "Thursday"]  # default
    
    if daily_completions and len(daily_completions) >= 3:
        # Sort by completion count and get top 3
        sorted_days = sorted(daily_completions, key=lambda x: x.completion_count, reverse=True)
        best_focus_days = [day_names[int(day.day_of_week)] for day in sorted_days[:3]]
    
    # Task completion patterns by type
    task_type_completions = db.query(
        Task.task_type,
        func.count(Task.id).label('total'),
        func.sum(func.case([(Task.status == TaskStatus.COMPLETED, 1)], else_=0)).label('completed')
    ).filter(
        Task.created_by == current_user.id,
        Task.created_at >= start_date
    ).group_by(Task.task_type).all()
    
    completion_by_type = {}
    for stat in task_type_completions:
        if stat.total > 0:
            completion_rate = int((stat.completed / stat.total) * 100)
            completion_by_type[stat.task_type.value] = completion_rate
    
    # Task completion patterns by time of day
    morning_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.completed_at >= start_date,
        extract('hour', Task.completed_at).between(6, 11)
    ).count()
    
    afternoon_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.completed_at >= start_date,
        extract('hour', Task.completed_at).between(12, 17)
    ).count()
    
    evening_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.completed_at >= start_date,
        extract('hour', Task.completed_at).between(18, 23)
    ).count()
    
    total_time_tasks = morning_tasks + afternoon_tasks + evening_tasks
    completion_by_time = {}
    
    if total_time_tasks > 0:
        completion_by_time = {
            "morning": int((morning_tasks / total_time_tasks) * 100),
            "afternoon": int((afternoon_tasks / total_time_tasks) * 100),
            "evening": int((evening_tasks / total_time_tasks) * 100)
        }
    else:
        completion_by_time = {"morning": 78, "afternoon": 55, "evening": 45}
    
    # Identify procrastination triggers
    procrastination_triggers = []
    
    # Check for overdue tasks
    overdue_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.due_date < datetime.now(),
        Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
    ).count()
    
    if overdue_tasks > 0:
        procrastination_triggers.append("Tasks with approaching deadlines")
    
    # Check for long-duration tasks
    long_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.estimated_duration > 45,
        Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
    ).count()
    
    if long_tasks > 0:
        procrastination_triggers.append("Tasks longer than 45 minutes")
    
    # Check for unclear tasks (no description)
    unclear_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.description.is_(None),
        Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
    ).count()
    
    if unclear_tasks > 0:
        procrastination_triggers.append("Unclear task descriptions")
    
    if not procrastination_triggers:
        procrastination_triggers = ["No major procrastination triggers detected"]
    
    # Hyperfocus analysis
    hyperfocus_episodes = 0
    hyperfocus_duration = 3.5
    
    # Look for tasks that took much longer than estimated (potential hyperfocus)
    hyperfocus_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.actual_duration.isnot(None),
        Task.estimated_duration.isnot(None),
        Task.actual_duration > Task.estimated_duration * 2,  # 2x longer than estimated
        Task.completed_at >= start_date
    ).all()
    
    if hyperfocus_tasks:
        hyperfocus_episodes = len(hyperfocus_tasks)
        avg_hyperfocus_duration = sum(task.actual_duration for task in hyperfocus_tasks) / len(hyperfocus_tasks)
        hyperfocus_duration = round(avg_hyperfocus_duration / 60, 1)  # Convert to hours
    
    # Generate recommendations based on patterns
    recommendations = []
    
    if peak_hours:
        recommendations.append(f"🎯 Schedule complex tasks during your peak hours: {', '.join(peak_hours[:2])}")
    
    if avg_focus_duration < 30:
        recommendations.append("⏰ Your optimal focus duration is short - embrace quick wins!")
    else:
        recommendations.append("⏰ Consider breaking tasks into smaller chunks for better focus")
    
    if hyperfocus_episodes > 0:
        recommendations.append("🔄 Build in recovery time after intense work sessions")
    
    recommendations.append("📝 Keep task descriptions clear to avoid procrastination")
    
    return {
        "analysis_period": f"Last {days} days",
        "energy_patterns": {
            "peak_hours": peak_hours,
            "low_energy_periods": low_energy_periods,
            "average_focus_duration": avg_focus_duration,
            "best_focus_days": best_focus_days
        },
        "task_patterns": {
            "completion_by_type": completion_by_type,
            "completion_by_time": completion_by_time,
            "procrastination_triggers": procrastination_triggers
        },
        "focus_analysis": {
            "hyperfocus_episodes": hyperfocus_episodes,
            "average_hyperfocus_duration": hyperfocus_duration,
            "hyperfocus_recovery_time": 45,
            "focus_session_success_rate": min(100, int((len(completed_tasks) / max(1, len(completed_tasks) + overdue_tasks)) * 100))
        },
        "recommendations": recommendations
    }

@router.get("/progress", summary="Get progress tracking")
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed progress tracking with ADHD-friendly metrics.
    
    **Progress Metrics:**
    - Habit formation progress
    - Consistency tracking
    - Difficulty adaptation
    - Goal achievement
    - Personal growth indicators
    """
    # Get user's task completion stats
    total_completed = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED
    ).count()
    
    # Get recent completion data for streaks (last 30 days)
    today = datetime.now().date()
    last_30_days = today - timedelta(days=30)
    
    recent_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        Task.completed_at >= last_30_days
    ).order_by(Task.completed_at.desc()).all()
    
    # Calculate habit tracking metrics
    def calculate_habit_streak(task_type_filter=None):
        """Calculate current and longest streak for specific task types"""
        query = db.query(func.date(Task.completed_at)).filter(
            Task.created_by == current_user.id,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= last_30_days
        )
        
        if task_type_filter:
            query = query.filter(Task.task_type == task_type_filter)
        
        completion_dates = [date[0] for date in query.distinct().all()]
        completion_dates.sort(reverse=True)
        
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        if completion_dates:
            # Calculate current streak (consecutive days from today)
            current_date = today
            for date in completion_dates:
                if date == current_date or (current_date - date).days == 1:
                    current_streak += 1
                    current_date = date
                else:
                    break
            
            # Calculate longest streak
            prev_date = None
            for date in sorted(completion_dates):
                if prev_date is None or (date - prev_date).days == 1:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 1
                prev_date = date
        
        # Calculate completion rate
        total_days = 30
        completion_rate = int((len(completion_dates) / total_days) * 100)
        
        # Determine trend
        recent_half = completion_dates[:15] if len(completion_dates) >= 15 else completion_dates
        older_half = completion_dates[15:] if len(completion_dates) >= 15 else []
        
        trend = "stable"
        if len(recent_half) > len(older_half):
            trend = "improving"
        elif len(recent_half) < len(older_half):
            trend = "declining"
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completion_rate": min(100, completion_rate),
            "trend": trend
        }
    
    # Calculate habits for different task types
    routine_habits = calculate_habit_streak(ADHDTaskType.ROUTINE)
    project_habits = calculate_habit_streak(ADHDTaskType.PROJECT)
    maintenance_habits = calculate_habit_streak(ADHDTaskType.MAINTENANCE)
    
    # Generate achievements based on real data
    achievements = []
    
    # Task completion achievements
    today_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        func.date(Task.completed_at) == today
    ).count()
    
    if today_tasks > 0:
        achievements.append(f"🎯 Completed {today_tasks} task{'s' if today_tasks != 1 else ''} today!")
    
    # Streak achievements
    max_streak = max(routine_habits["current_streak"], project_habits["current_streak"], maintenance_habits["current_streak"])
    if max_streak >= 7:
        achievements.append(f"🔥 {max_streak}-day completion streak!")
    elif max_streak >= 3:
        achievements.append(f"⭐ {max_streak}-day momentum building!")
    
    # Task type completion achievements
    rocks_completed = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.impact_size == ADHDImpactSize.ROCK,
        Task.status == TaskStatus.COMPLETED,
        Task.completed_at >= last_30_days
    ).count()
    
    if rocks_completed > 0:
        achievements.append(f"🪨 Tackled {rocks_completed} high-impact task{'s' if rocks_completed != 1 else ''} this month!")
    
    # Weekly completion achievement
    week_start = today - timedelta(days=today.weekday())
    weekly_tasks = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        Task.completed_at >= week_start
    ).count()
    
    if weekly_tasks >= 5:
        achievements.append(f"⚡ {weekly_tasks} tasks completed this week!")
    
    if not achievements:
        achievements.append("🌱 Every step forward is progress - keep going!")
    
    # Calculate executive function scores based on task patterns
    def calculate_executive_score(metric_type):
        """Calculate a score (1-10) for executive function metrics"""
        base_score = 5.0
        
        if metric_type == "planning":
            # Based on tasks with due dates and estimated durations
            planned_tasks = db.query(Task).filter(
                Task.created_by == current_user.id,
                Task.due_date.isnot(None),
                Task.estimated_duration.isnot(None),
                Task.created_at >= last_30_days
            ).count()
            
            total_recent_tasks = db.query(Task).filter(
                Task.created_by == current_user.id,
                Task.created_at >= last_30_days
            ).count()
            
            if total_recent_tasks > 0:
                planning_rate = planned_tasks / total_recent_tasks
                base_score = 5.0 + (planning_rate * 5.0)
        
        elif metric_type == "organization":
            # Based on task categorization (type, priority, impact size)
            categorized_tasks = db.query(Task).filter(
                Task.created_by == current_user.id,
                Task.task_type.isnot(None),
                Task.priority.isnot(None),
                Task.impact_size.isnot(None),
                Task.created_at >= last_30_days
            ).count()
            
            total_recent_tasks = db.query(Task).filter(
                Task.created_by == current_user.id,
                Task.created_at >= last_30_days
            ).count()
            
            if total_recent_tasks > 0:
                organization_rate = categorized_tasks / total_recent_tasks
                base_score = 5.0 + (organization_rate * 5.0)
        
        elif metric_type == "time_management":
            # Based on task completion vs. estimated time
            accurate_estimates = db.query(Task).filter(
                Task.created_by == current_user.id,
                Task.actual_duration.isnot(None),
                Task.estimated_duration.isnot(None),
                Task.actual_duration <= Task.estimated_duration * 1.5,  # Within 50% of estimate
                Task.completed_at >= last_30_days
            ).count()
            
            estimated_tasks = db.query(Task).filter(
                Task.created_by == current_user.id,
                Task.actual_duration.isnot(None),
                Task.estimated_duration.isnot(None),
                Task.completed_at >= last_30_days
            ).count()
            
            if estimated_tasks > 0:
                accuracy_rate = accurate_estimates / estimated_tasks
                base_score = 5.0 + (accuracy_rate * 5.0)
        
        elif metric_type == "task_initiation":
            # Based on tasks completed vs. created
            completion_rate = routine_habits["completion_rate"] / 100
            base_score = 5.0 + (completion_rate * 5.0)
        
        return round(min(10.0, max(1.0, base_score)), 1)
    
    executive_scores = {
        "planning": calculate_executive_score("planning"),
        "organization": calculate_executive_score("organization"),
        "time_management": calculate_executive_score("time_management"),
        "task_initiation": calculate_executive_score("task_initiation")
    }
    
    # Generate improvement suggestions
    improvement_areas = []
    avg_score = sum(executive_scores.values()) / len(executive_scores)
    
    if avg_score >= 7.5:
        improvement_areas.append("🌟 Excellent executive function skills! Keep up the great work!")
    elif avg_score >= 6.5:
        improvement_areas.append("📈 Strong progress in developing ADHD management strategies")
    
    # Specific suggestions based on scores
    if executive_scores["planning"] < 6.0:
        improvement_areas.append("Consider setting estimated durations and due dates for more tasks")
    
    if executive_scores["organization"] < 6.0:
        improvement_areas.append("Try categorizing tasks by type, priority, and impact size")
    
    if executive_scores["time_management"] < 6.0:
        improvement_areas.append("Practice estimating task duration to improve time awareness")
    
    if executive_scores["task_initiation"] < 6.0:
        improvement_areas.append("Break large tasks into smaller, more manageable pieces")
    
    if not improvement_areas:
        improvement_areas.append("Focus on maintaining your current excellent momentum!")
    
    return {
        "habit_tracking": {
            "morning_routine": routine_habits,
            "task_planning": project_habits,
            "maintenance_tasks": maintenance_habits
        },
        "achievements": achievements,
        "growth_indicators": {
            "executive_function": executive_scores,
            "improvement_areas": improvement_areas
        },
        "celebration": f"🎉 You've completed {total_completed} tasks total! " + 
                      (f"That's {len(recent_tasks)} in the last 30 days! " if recent_tasks else "") +
                      "Keep up the amazing work! 🚀"
    }

@router.get("/focus-sessions", summary="Get focus session analytics")
async def get_focus_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics about focus sessions and deep work periods.
    
    **Focus Session Data:**
    - Session duration effectiveness
    - Break timing optimization
    - Hyperfocus pattern recognition
    - Attention span trends
    """
    # Get completed tasks with duration data (proxy for focus sessions)
    last_30_days = datetime.now() - timedelta(days=30)
    
    focus_sessions = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        Task.actual_duration.isnot(None),
        Task.completed_at >= last_30_days
    ).all()
    
    # Analyze session durations
    durations = [task.actual_duration for task in focus_sessions if task.actual_duration > 0]
    
    # Calculate success rates by duration ranges
    def calculate_success_rate(min_duration, max_duration):
        sessions_in_range = [d for d in durations if min_duration <= d <= max_duration]
        if not sessions_in_range:
            return 0
        
        # For now, assume all completed tasks are "successful"
        # In the future, this could be based on user satisfaction ratings
        return min(100, len(sessions_in_range) * 10)  # Scale based on frequency
    
    success_rates = {
        "15_min": calculate_success_rate(5, 15),
        "25_min": calculate_success_rate(16, 35),
        "45_min": calculate_success_rate(36, 60),
        "60_min": calculate_success_rate(61, 120)
    }
    
    # Calculate optimal duration based on most frequent successful sessions
    optimal_duration = 25  # default ADHD-friendly duration
    if durations:
        # Find the most common duration range
        duration_ranges = {
            15: len([d for d in durations if d <= 15]),
            25: len([d for d in durations if 16 <= d <= 35]),
            45: len([d for d in durations if 36 <= d <= 60]),
            60: len([d for d in durations if d > 60])
        }
        optimal_duration = max(duration_ranges, key=duration_ranges.get)
    
    # Generate insights based on actual data
    insights = []
    
    if durations:
        avg_duration = sum(durations) / len(durations)
        
        if avg_duration <= 25:
            insights.append("🎯 You excel at short focus sessions - perfect for ADHD!")
        elif avg_duration <= 45:
            insights.append("⚡ Your focus sessions are well-suited for sustained attention")
        else:
            insights.append("🔥 You can maintain longer focus periods - watch for hyperfocus")
        
        # Analyze consistency
        if len(set(durations)) / len(durations) < 0.3:  # Low variation
            insights.append("📈 Your focus duration is very consistent")
        else:
            insights.append("🔄 Your focus varies - experiment with different session lengths")
        
        # Time of day analysis
        morning_sessions = [task for task in focus_sessions if task.completed_at.hour < 12]
        if len(morning_sessions) > len(focus_sessions) * 0.6:
            insights.append("🌅 Morning sessions are your strongest focus time")
        
        afternoon_sessions = [task for task in focus_sessions if 12 <= task.completed_at.hour < 18]
        if len(afternoon_sessions) > len(focus_sessions) * 0.6:
            insights.append("☀️ Afternoon sessions work well for your rhythm")
    else:
        insights = [
            "🎯 Start with 25-minute sessions - optimal for ADHD focus",
            "🔄 Take 10-minute breaks between sessions",
            "⚡ Morning sessions tend to be most effective",
            "📈 Regular practice improves focus stamina over time!"
        ]
    
    # Calculate break effectiveness (mock data for now)
    # In the future, this could be based on energy logs between tasks
    break_effectiveness = {
        "5_min_break": 85,
        "10_min_break": 90,
        "15_min_break": 75
    }
    
    # Recent sessions summary
    recent_sessions = []
    for task in focus_sessions[-10:]:  # Last 10 sessions
        recent_sessions.append({
            "date": task.completed_at.strftime("%Y-%m-%d"),
            "duration": task.actual_duration,
            "task_title": task.title,
            "task_type": task.task_type.value if task.task_type else "unknown",
            "success": True  # Completed tasks are considered successful
        })
    
    return {
        "recent_sessions": recent_sessions,
        "session_analytics": {
            "optimal_duration": optimal_duration,
            "success_rate_by_duration": success_rates,
            "break_effectiveness": break_effectiveness,
            "total_sessions": len(focus_sessions),
            "average_duration": round(sum(durations) / len(durations)) if durations else 0
        },
        "insights": insights
    }

@router.get("/test", summary="Test analytics endpoint without auth")
async def get_test_analytics():
    """
    Test endpoint that returns sample analytics data without authentication.
    This is for testing the frontend connection.
    """
    return {
        "overview": {
            "today": {
                "tasks_completed": 5,
                "tasks_pending": 3,
                "energy_level": "medium",
                "focus_sessions": 2,
                "break_compliance": 85
            },
            "this_week": {
                "tasks_completed": 28,
                "average_completion_rate": 75,
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
            "rewards_earned_today": 3,
            "streak_bonus": 2,
            "celebration_moments": 5,
            "motivation_level": "high"
        }
    }

@router.get("/test/patterns", summary="Test patterns endpoint without auth")
async def get_test_patterns():
    """
    Test patterns endpoint that returns sample patterns data.
    """
    return {
        "analysis_period": "Last 30 days",
        "energy_patterns": {
            "peak_hours": ["08:00-10:00", "16:00-17:30"],
            "low_energy_periods": ["13:00-15:00", "20:00-22:00"],
            "average_focus_duration": 28,
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
            "average_hyperfocus_duration": 3.5,
            "hyperfocus_recovery_time": 45,
            "focus_session_success_rate": 72
        },
        "recommendations": [
            "🎯 Schedule complex tasks during peak energy hours",
            "⏰ Limit single tasks to 30 minutes max",
            "🔄 Build in recovery time after hyperfocus sessions",
            "📝 Always clarify task requirements before starting"
        ]
    }

@router.get("/test/progress", summary="Test progress endpoint without auth")
async def get_test_progress():
    """
    Test progress endpoint that returns sample progress data.
    """
    return {
        "habit_tracking": {
            "morning_routine": {
                "current_streak": 7,
                "longest_streak": 14,
                "completion_rate": 80,
                "trend": "improving"
            },
            "task_planning": {
                "current_streak": 5,
                "longest_streak": 12,
                "completion_rate": 70,
                "trend": "stable"
            },
            "break_taking": {
                "current_streak": 3,
                "longest_streak": 8,
                "completion_rate": 60,
                "trend": "improving"
            }
        },
        "achievements": [
            "🎯 Completed 5 tasks today!",
            "🔥 7-day morning routine streak!",
            "⚡ 2 successful focus sessions!"
        ],
        "growth_indicators": {
            "executive_function": {
                "planning": 7.5,
                "organization": 6.8,
                "time_management": 7.2,
                "task_initiation": 6.5
            },
            "improvement_areas": [
                "Keep building momentum with consistent task completion",
                "Consider tracking energy patterns for better task scheduling",
                "Celebrate progress to maintain motivation"
            ]
        },
        "celebration": "🎉 You've completed 28 tasks this week! Keep up the great work! 🚀"
    }
