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
from app.schemas.task import ADHDImpactSize


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
        Create a new task with ADHD-friendly features including impact classification.
        
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
        
        # Generate dopamine reward based on impact size
        impact_size = task_data.get("impact_size", "pebbles")
        reward = self._generate_impact_based_reward(impact_size)
        
        new_task = {
            "id": self.task_counter,
            "title": task_data["title"],
            "description": task_data.get("description", ""),
            "task_type": task_data.get("task_type", "routine"),
            "priority": task_data.get("priority", "medium"),
            "status": "todo",
            "complexity": task_data.get("complexity", "medium"),
            "impact_size": impact_size,  # New field for Rock/Pebbles/Sand
            "created_at": datetime.now().isoformat(),
            "due_date": task_data.get("due_date"),
            "estimated_duration": duration_info["estimated"],
            "adhd_features": {
                "dopamine_reward": reward["message"],
                "break_reminder": True,
                "chunked": len(subtasks) > 1,
                "subtasks": subtasks,
                "energy_level_required": self._determine_energy_from_impact(impact_size),
                "best_time_of_day": self._suggest_time_by_impact(impact_size),
                "focus_duration": self._get_focus_duration_by_impact(impact_size),
                "hyperfocus_risk": impact_size == "rock",
                "collaboration_boost": False
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
        impact_size: Optional[str] = None,  # New filter parameter
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get tasks with filtering and ADHD-friendly presentation including impact classification.
        
        Args:
            status: Filter by task status
            priority: Filter by priority level
            task_type: Filter by ADHD task type
            impact_size: Filter by Rock/Pebbles/Sand classification
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
        if impact_size:
            filtered_tasks = [t for t in filtered_tasks if t["impact_size"] == impact_size]
        
        # Sort by impact: Rocks first, then Pebbles, then Sand
        impact_order = {"rock": 0, "pebbles": 1, "sand": 2}
        filtered_tasks.sort(key=lambda x: impact_order.get(x.get("impact_size", "pebbles"), 1))
        
        # Limit results to prevent overwhelm
        limited_tasks = filtered_tasks[:limit]
        
        # Add ADHD-friendly tips based on current task load and impact distribution
        adhd_tip = self._get_impact_aware_tip(limited_tasks)
        
        return {
            "tasks": limited_tasks,
            "total": len(filtered_tasks),
            "showing": len(limited_tasks),
            "adhd_tip": adhd_tip,
            "focus_suggestion": self._get_impact_based_focus_suggestion(limited_tasks),
            "impact_distribution": self._analyze_impact_distribution(limited_tasks)
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
    
    def _generate_impact_based_reward(self, impact_size: str) -> Dict[str, str]:
        """Generate dopamine reward based on impact size."""
        rewards = {
            "rock": {
                "message": "🏔️ MASSIVE IMPACT! You're tackling the big stuff!",
                "emoji": "🏔️", 
                "celebration_level": "epic"
            },
            "pebbles": {
                "message": "⚡ Solid progress! Building great momentum!",
                "emoji": "⚡",
                "celebration_level": "high"
            },
            "sand": {
                "message": "✨ Nice touch! Every detail matters!",
                "emoji": "✨",
                "celebration_level": "medium"
            }
        }
        return rewards.get(impact_size, rewards["pebbles"])

    def _determine_energy_from_impact(self, impact_size: str) -> str:
        """Determine energy requirement based on impact size."""
        energy_map = {
            "rock": "high",      # Rocks need your best energy
            "pebbles": "medium", # Pebbles are manageable
            "sand": "low"        # Sand can be done anytime
        }
        return energy_map.get(impact_size, "medium")

    def _suggest_time_by_impact(self, impact_size: str) -> str:
        """Suggest optimal time based on impact size."""
        time_map = {
            "rock": "morning",    # Rocks deserve peak hours
            "pebbles": "flexible", # Pebbles fit anywhere
            "sand": "afternoon"   # Sand fills the gaps
        }
        return time_map.get(impact_size, "flexible")

    def _get_focus_duration_by_impact(self, impact_size: str) -> int:
        """Get recommended focus duration based on impact size."""
        duration_map = {
            "rock": 45,      # Rocks might need longer focus sessions
            "pebbles": 25,   # Standard pomodoro for pebbles
            "sand": 15       # Quick bursts for sand tasks
        }
        return duration_map.get(impact_size, 25)

    def _get_impact_aware_tip(self, tasks: List[Dict[str, Any]]) -> str:
        """Get ADHD tip based on task impact distribution."""
        if not tasks:
            return "🎉 All caught up! Perfect time to plan your next rocks and pebbles."
        
        rock_count = sum(1 for t in tasks if t.get("impact_size") == "rock")
        pebbles_count = sum(1 for t in tasks if t.get("impact_size") == "pebbles")
        sand_count = sum(1 for t in tasks if t.get("impact_size") == "sand")
        
        if rock_count > 2:
            return "🏔️ You have many ROCK tasks! Focus on just 1-2 rocks per day for maximum impact."
        elif rock_count >= 1 and pebbles_count >= 1:
            return "⚡ Perfect mix! Start with a rock during peak energy, then build momentum with pebbles."
        elif pebbles_count > 5:
            return "🔄 Lots of pebbles! Group similar ones together for efficient momentum building."
        elif sand_count > 10:
            return "🌊 High sand volume detected! Consider delegating or batching these tasks."
        else:
            return "👌 Great task balance! Focus on impact order: rocks first, then pebbles, sand fills gaps."

    def _get_impact_based_focus_suggestion(self, tasks: List[Dict[str, Any]]) -> str:
        """Get focus suggestion based on available tasks and their impact."""
        if not tasks:
            return "Time to add some tasks or enjoy the moment! 🌟"
        
        # Find the highest impact task available
        rock_tasks = [t for t in tasks if t.get("impact_size") == "rock" and t["status"] == "todo"]
        pebbles_tasks = [t for t in tasks if t.get("impact_size") == "pebbles" and t["status"] == "todo"] 
        
        if rock_tasks:
            return f"🏔️ ROCK FOCUS: Start with '{rock_tasks[0]['title']}' - this will have massive impact!"
        elif pebbles_tasks:
            return f"⚡ PEBBLES MOMENTUM: '{pebbles_tasks[0]['title']}' is perfect for building progress!"
        else:
            sand_tasks = [t for t in tasks if t.get("impact_size") == "sand" and t["status"] == "todo"]
            if sand_tasks:
                return f"✨ SAND SWEEP: '{sand_tasks[0]['title']}' - a nice task to fill some time!"
            else:
                return "🚀 All tasks in progress! Great job staying on track!"

    def _analyze_impact_distribution(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the distribution of tasks by impact size."""
        rock_count = sum(1 for t in tasks if t.get("impact_size") == "rock")
        pebbles_count = sum(1 for t in tasks if t.get("impact_size") == "pebbles")
        sand_count = sum(1 for t in tasks if t.get("impact_size") == "sand")
        
        total = len(tasks)
        if total == 0:
            return {"rock": 0, "pebbles": 0, "sand": 0, "balance_assessment": "No tasks available"}
        
        rock_percentage = (rock_count / total) * 100
        pebbles_percentage = (pebbles_count / total) * 100
        sand_percentage = (sand_count / total) * 100
        
        # Assess balance (ideal: 10-20% rocks, 60-70% pebbles, 10-30% sand)
        balance_assessment = "Good balance"
        if rock_percentage > 30:
            balance_assessment = "Too many rocks - consider breaking some down"
        elif rock_percentage == 0 and total > 0:
            balance_assessment = "No rocks found - add some high-impact tasks"
        elif sand_percentage > 50:
            balance_assessment = "Too much sand - focus on higher impact tasks"
        
        return {
            "rock": rock_count,
            "pebbles": pebbles_count, 
            "sand": sand_count,
            "percentages": {
                "rock": round(rock_percentage, 1),
                "pebbles": round(pebbles_percentage, 1),
                "sand": round(sand_percentage, 1)
            },
            "balance_assessment": balance_assessment
        }
    
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
