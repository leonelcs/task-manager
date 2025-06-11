"""
Utility functions for ADHD-specific task management features.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

def estimate_task_duration(complexity: str, task_type: str) -> Dict[str, int]:
    """
    Estimate task duration with ADHD-friendly time buffers.
    
    Args:
        complexity: "low", "medium", "high"
        task_type: "routine", "project", "maintenance", "emergency"
    
    Returns:
        Dictionary with estimated, minimum, and maximum durations
    """
    base_times = {
        "routine": {"low": 10, "medium": 20, "high": 30},
        "project": {"low": 30, "medium": 60, "high": 120},
        "maintenance": {"low": 15, "medium": 30, "high": 45},
        "emergency": {"low": 5, "medium": 15, "high": 30}
    }
    
    base_time = base_times.get(task_type, {}).get(complexity, 30)
    
    # Add ADHD buffer (25% extra time)
    adhd_buffer = int(base_time * 0.25)
    
    return {
        "estimated": base_time + adhd_buffer,
        "minimum": base_time,
        "maximum": base_time + (adhd_buffer * 2),
        "break_included": True
    }

def generate_dopamine_reward(task_type: str, completion_streak: int = 0) -> Dict[str, str]:
    """
    Generate ADHD-friendly dopamine rewards and celebrations.
    
    Args:
        task_type: Type of completed task
        completion_streak: Current completion streak
    
    Returns:
        Dictionary with reward message and emoji
    """
    base_rewards = {
        "routine": ["🌟 Routine champion!", "🎯 Consistency king/queen!", "⚡ Habit hero!"],
        "project": ["🚀 Project powerhouse!", "🏗️ Building greatness!", "💪 Making it happen!"],
        "maintenance": ["🧹 Maintenance master!", "✨ Keeping things smooth!", "🔧 System superstar!"],
        "emergency": ["🚨 Crisis crusher!", "⚡ Lightning response!", "🎯 Clutch performance!"]
    }
    
    streak_bonuses = {
        5: "🔥 Hot streak!",
        10: "💎 Diamond streak!",
        15: "🏆 Legendary streak!",
        20: "🌟 Streak superstar!"
    }
    
    base_reward = random.choice(base_rewards.get(task_type, ["🎉 Task completed!"]))
    
    # Add streak bonus if applicable
    streak_bonus = ""
    for threshold in sorted(streak_bonuses.keys(), reverse=True):
        if completion_streak >= threshold:
            streak_bonus = f" {streak_bonuses[threshold]}"
            break
    
    return {
        "message": f"{base_reward}{streak_bonus}",
        "emoji": "🎉",
        "celebration_level": "high" if completion_streak >= 5 else "medium"
    }

def break_down_large_task(task_description: str, estimated_duration: int) -> List[Dict[str, Any]]:
    """
    Break down large tasks into ADHD-friendly smaller chunks.
    
    Args:
        task_description: Description of the large task
        estimated_duration: Estimated duration in minutes
    
    Returns:
        List of subtask dictionaries
    """
    if estimated_duration <= 30:
        return [{"description": task_description, "duration": estimated_duration, "order": 1}]
    
    # Generic task breakdown suggestions
    chunk_size = 25  # ADHD-friendly 25-minute chunks
    num_chunks = max(2, (estimated_duration + chunk_size - 1) // chunk_size)
    
    subtasks = []
    for i in range(num_chunks):
        subtasks.append({
            "description": f"{task_description} - Part {i + 1}",
            "duration": min(chunk_size, estimated_duration - (i * chunk_size)),
            "order": i + 1,
            "break_after": True if i < num_chunks - 1 else False
        })
    
    return subtasks

def get_optimal_task_time(energy_patterns: Dict[str, str], current_time: datetime = None) -> Dict[str, Any]:
    """
    Suggest optimal time for task based on energy patterns.
    
    Args:
        energy_patterns: Dictionary of time periods and energy levels
        current_time: Current time (defaults to now)
    
    Returns:
        Dictionary with time suggestions and reasoning
    """
    if current_time is None:
        current_time = datetime.now()
    
    current_hour = current_time.hour
    
    # Map energy patterns to recommendations
    energy_recommendations = {
        "high": {
            "task_types": ["project", "complex", "challenging"],
            "message": "Perfect time for your most important tasks!"
        },
        "medium": {
            "task_types": ["routine", "maintenance", "moderate"],
            "message": "Good time for regular tasks and planning."
        },
        "low": {
            "task_types": ["easy", "mindless", "organizing"],
            "message": "Great time for simple tasks or taking a break."
        }
    }
    
    # Simple time-based energy estimation (can be replaced with user data)
    if 6 <= current_hour < 10:
        energy_level = "high"
        time_period = "morning"
    elif 10 <= current_hour < 14:
        energy_level = "medium"
        time_period = "late_morning"
    elif 14 <= current_hour < 16:
        energy_level = "low"
        time_period = "afternoon"
    elif 16 <= current_hour < 19:
        energy_level = "medium"
        time_period = "evening"
    else:
        energy_level = "low"
        time_period = "night"
    
    recommendation = energy_recommendations.get(energy_level, energy_recommendations["medium"])
    
    return {
        "current_energy": energy_level,
        "time_period": time_period,
        "recommended_tasks": recommendation["task_types"],
        "message": recommendation["message"],
        "adhd_tip": "🧠 Work with your natural energy rhythms, not against them!"
    }

def calculate_focus_score(task_duration: int, breaks_taken: int, distractions: int = 0) -> Dict[str, Any]:
    """
    Calculate focus score for ADHD analytics.
    
    Args:
        task_duration: Duration of focus session in minutes
        breaks_taken: Number of breaks taken
        distractions: Number of distractions encountered
    
    Returns:
        Dictionary with focus score and insights
    """
    # Base score calculation
    optimal_duration = 25  # Pomodoro technique
    duration_score = max(0, 100 - abs(task_duration - optimal_duration) * 2)
    
    # Break score (1 break per 25 minutes is optimal)
    expected_breaks = max(1, task_duration // 25)
    break_score = max(0, 100 - abs(breaks_taken - expected_breaks) * 20)
    
    # Distraction penalty
    distraction_penalty = min(50, distractions * 10)
    
    # Overall focus score
    focus_score = max(0, (duration_score + break_score) / 2 - distraction_penalty)
    
    # Generate insights
    insights = []
    if focus_score >= 80:
        insights.append("🎯 Excellent focus session!")
    elif focus_score >= 60:
        insights.append("👍 Good focus, room for improvement")
    else:
        insights.append("💡 Consider shorter sessions or fewer distractions")
    
    if task_duration > 45:
        insights.append("⏰ Try breaking long sessions into smaller chunks")
    
    if breaks_taken == 0 and task_duration > 25:
        insights.append("🔄 Don't forget to take breaks!")
    
    return {
        "focus_score": round(focus_score, 1),
        "duration_score": round(duration_score, 1),
        "break_score": round(break_score, 1),
        "insights": insights,
        "recommendation": "Keep sessions around 25 minutes with regular breaks"
    }
