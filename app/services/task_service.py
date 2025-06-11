"""
Task Service for ADHD Task Manager.
Handles business logic for task management with ADHD-specific features.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.utils.helpers import (
    estimate_task_duration, 
    generate_dopamine_reward,
    break_down_large_task,
    calculate_focus_score
)


class TaskService:
    """
    Service class for managing tasks with ADHD-specific features.
    """
    
    def __init__(self):
        # This would typically connect to a database
        # For now, we'll use in-memory storage
        self.tasks = []
        self.task_counter = 1
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task with ADHD-friendly features.
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            Created task with ADHD enhancements
        """
        # Estimate duration with ADHD buffer
        duration_info = estimate_task_duration(
            task_data.get("complexity", "medium"),
            task_data.get("task_type", "routine")
        )
        
        # Break down large tasks automatically
        subtasks = []
        if duration_info["estimated"] > 45:
            subtasks = break_down_large_task(
                task_data["title"], 
                duration_info["estimated"]
            )
        
        # Generate dopamine reward
        reward = generate_dopamine_reward(task_data.get("task_type", "routine"))
        
        new_task = {
            "id": self.task_counter,
            "title": task_data["title"],
            "description": task_data.get("description", ""),
            "task_type": task_data.get("task_type", "routine"),
            "priority": task_data.get("priority", "medium"),
            "status": "todo",
            "complexity": task_data.get("complexity", "medium"),
            "created_at": datetime.now().isoformat(),
            "due_date": task_data.get("due_date"),
            "estimated_duration": duration_info["estimated"],
            "adhd_features": {
                "dopamine_reward": reward["message"],
                "break_reminder": True,
                "chunked": len(subtasks) > 1,
                "subtasks": subtasks,
                "energy_level_required": self._determine_energy_requirement(
                    task_data.get("complexity", "medium"),
                    task_data.get("task_type", "routine")
                ),
                "best_time_of_day": self._suggest_optimal_time(
                    task_data.get("task_type", "routine")
                )
            },
            "completion_history": []
        }
        
        self.tasks.append(new_task)
        self.task_counter += 1
        
        return new_task
    
    async def get_tasks(
        self, 
        status: Optional[str] = None,
        priority: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get tasks with filtering and ADHD-friendly presentation.
        
        Args:
            status: Filter by task status
            priority: Filter by priority level
            task_type: Filter by ADHD task type
            limit: Maximum number of tasks to return
            
        Returns:
            Filtered tasks with ADHD tips
        """
        filtered_tasks = self.tasks.copy()
        
        # Apply filters
        if status:
            filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]
        if task_type:
            filtered_tasks = [t for t in filtered_tasks if t["task_type"] == task_type]
        
        # Limit results to prevent overwhelm
        limited_tasks = filtered_tasks[:limit]
        
        # Add ADHD-friendly tips based on current task load
        adhd_tip = self._get_task_load_tip(len(limited_tasks))
        
        return {
            "tasks": limited_tasks,
            "total": len(filtered_tasks),
            "showing": len(limited_tasks),
            "adhd_tip": adhd_tip,
            "focus_suggestion": self._get_focus_suggestion(limited_tasks)
        }
    
    async def complete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Complete a task with ADHD-friendly celebration.
        
        Args:
            task_id: ID of the task to complete
            
        Returns:
            Completion confirmation with dopamine boost
        """
        task = self._find_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task status
        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        
        # Add to completion history
        completion_entry = {
            "date": datetime.now().date().isoformat(),
            "completed": True,
            "completion_time": datetime.now().isoformat()
        }
        task["completion_history"].append(completion_entry)
        
        # Calculate streak information
        streak_info = self._calculate_completion_streak(task)
        
        # Generate enhanced dopamine reward
        enhanced_reward = generate_dopamine_reward(
            task["task_type"], 
            streak_info["current_streak"]
        )
        
        return {
            "message": f"🎉 Awesome! Task '{task['title']}' completed!",
            "task": task,
            "dopamine_boost": enhanced_reward["message"],
            "streak_info": streak_info,
            "celebration_level": enhanced_reward["celebration_level"],
            "next_suggestion": self._get_post_completion_suggestion(task),
            "achievement_unlocked": self._check_achievements(streak_info)
        }
    
    def _find_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Find a task by its ID."""
        return next((task for task in self.tasks if task["id"] == task_id), None)
    
    def _determine_energy_requirement(self, complexity: str, task_type: str) -> str:
        """Determine required energy level for a task."""
        energy_map = {
            ("low", "routine"): "low",
            ("low", "maintenance"): "low",
            ("medium", "routine"): "low",
            ("medium", "maintenance"): "medium",
            ("medium", "project"): "medium",
            ("high", "project"): "high",
            ("high", "emergency"): "high"
        }
        return energy_map.get((complexity, task_type), "medium")
    
    def _suggest_optimal_time(self, task_type: str) -> str:
        """Suggest optimal time of day for task type."""
        time_suggestions = {
            "routine": "morning",
            "project": "morning",
            "maintenance": "afternoon",
            "emergency": "anytime"
        }
        return time_suggestions.get(task_type, "flexible")
    
    def _get_task_load_tip(self, task_count: int) -> str:
        """Get ADHD tip based on current task load."""
        if task_count == 0:
            return "🎉 All caught up! Perfect time to plan or take a well-deserved break."
        elif task_count <= 3:
            return "👌 Great task load! Focus on one at a time for maximum effectiveness."
        elif task_count <= 7:
            return "⚡ Moderate task load. Consider prioritizing the top 3 for today."
        else:
            return "🧠 High task load detected. Break it down - focus on just 2-3 priorities today."
    
    def _get_focus_suggestion(self, tasks: List[Dict[str, Any]]) -> str:
        """Get focus suggestion based on available tasks."""
        if not tasks:
            return "Time to add some tasks or enjoy the moment! 🌟"
        
        high_priority = [t for t in tasks if t["priority"] == "high"]
        if high_priority:
            return f"🎯 Focus suggestion: Start with '{high_priority[0]['title']}' - it's high priority!"
        
        quick_tasks = [t for t in tasks if t["estimated_duration"] <= 15]
        if quick_tasks:
            return f"⚡ Quick win available: '{quick_tasks[0]['title']}' takes only {quick_tasks[0]['estimated_duration']} minutes!"
        
        return f"🚀 Good time to tackle '{tasks[0]['title']}' - you've got this!"
    
    def _calculate_completion_streak(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate completion streak for the task type."""
        # This would typically query database for streak information
        # For now, return mock streak data
        return {
            "current_streak": 3,
            "longest_streak": 7,
            "task_type_streak": 2,
            "total_completions": len(task["completion_history"])
        }
    
    def _get_post_completion_suggestion(self, completed_task: Dict[str, Any]) -> str:
        """Get suggestion for what to do after completing a task."""
        suggestions = [
            "Take a 5-minute celebration break! 🎉",
            "Hydrate and stretch - your brain deserves it! 💧",
            "Quick dopamine hit: check something off your personal list! ✅",
            "Perfect time for a brief walk or some fresh air! 🚶‍♀️",
            "Jot down how good this completion feels! 📝"
        ]
        return suggestions[completed_task["id"] % len(suggestions)]
    
    def _check_achievements(self, streak_info: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Check if any achievements were unlocked."""
        streak = streak_info["current_streak"]
        
        achievement_thresholds = {
            5: {"title": "Streak Starter", "description": "5 tasks in a row!"},
            10: {"title": "Consistency Champion", "description": "10-task streak!"},
            15: {"title": "Habit Hero", "description": "15-task streak!"},
            20: {"title": "Streak Superstar", "description": "20-task streak!"}
        }
        
        return achievement_thresholds.get(streak)


# Service instance
task_service = TaskService()
