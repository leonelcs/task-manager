"""
AI Service for ADHD-specific task management and insights.
This module will handle AI-powered features like task suggestions,
pattern recognition, and personalized recommendations.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import random


class ADHDAIService:
    """
    AI service specifically designed for ADHD task management.
    
    This service provides:
    - Intelligent task suggestions based on energy levels
    - Pattern recognition from historical data
    - Personalized recommendations
    - Adaptive difficulty adjustments
    """
    
    def __init__(self):
        self.user_patterns = {}
        self.task_history = []
    
    async def get_task_suggestions(
        self, 
        current_energy: str = "medium",
        available_time: int = 30,
        user_preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate AI-powered task suggestions based on current context.
        
        Args:
            current_energy: Current energy level ("low", "medium", "high")
            available_time: Available time in minutes
            user_preferences: User's ADHD preferences and settings
            
        Returns:
            List of suggested tasks with reasoning and ADHD benefits
        """
        suggestions = []
        
        # Energy-based task suggestions
        energy_tasks = {
            "high": [
                {
                    "task": "Tackle your most challenging project",
                    "reason": "Your energy is peak - perfect for complex tasks!",
                    "duration": min(45, available_time),
                    "adhd_benefits": ["Maximum focus utilization", "Big dopamine reward", "Momentum building"]
                },
                {
                    "task": "Organize and declutter workspace",
                    "reason": "High energy is great for physical organization",
                    "duration": min(30, available_time),
                    "adhd_benefits": ["Visual clarity", "Reduced distractions", "Sense of control"]
                }
            ],
            "medium": [
                {
                    "task": "Review and plan tomorrow's priorities",
                    "reason": "Good focus for planning without overwhelm",
                    "duration": min(20, available_time),
                    "adhd_benefits": ["Reduces morning anxiety", "Clear direction", "Executive function support"]
                },
                {
                    "task": "Complete routine maintenance tasks",
                    "reason": "Steady energy perfect for consistent tasks",
                    "duration": min(25, available_time),
                    "adhd_benefits": ["Habit reinforcement", "Quick wins", "Momentum maintenance"]
                }
            ],
            "low": [
                {
                    "task": "Simple sorting or filing",
                    "reason": "Low-energy tasks that still provide accomplishment",
                    "duration": min(15, available_time),
                    "adhd_benefits": ["Easy dopamine hit", "No decision fatigue", "Gentle productivity"]
                },
                {
                    "task": "Listen to educational podcast while tidying",
                    "reason": "Passive learning + easy physical activity",
                    "duration": min(20, available_time),
                    "adhd_benefits": ["Multitasking satisfaction", "Learning + doing", "Low pressure"]
                }
            ]
        }
        
        # Get suggestions based on energy level
        energy_suggestions = energy_tasks.get(current_energy, energy_tasks["medium"])
        
        # Filter by available time and add confidence scores
        for suggestion in energy_suggestions:
            if suggestion["duration"] <= available_time:
                suggestion["confidence"] = self._calculate_confidence_score(
                    suggestion, current_energy, available_time
                )
                suggestions.append(suggestion)
        
        # Add motivational message
        motivation_messages = [
            "💪 You've got this! Every small step counts.",
            "🚀 Perfect timing to make some progress!",
            "✨ Your future self will thank you for this!",
            "🎯 Focus on progress, not perfection!",
            "🧠 Working with your ADHD brain, not against it!"
        ]
        
        return {
            "suggestions": suggestions[:3],  # Limit to prevent overwhelm
            "energy_level": current_energy,
            "available_time": available_time,
            "motivation": random.choice(motivation_messages),
            "adhd_tip": self._get_energy_specific_tip(current_energy)
        }
    
    def _calculate_confidence_score(
        self, 
        suggestion: Dict[str, Any], 
        energy: str, 
        available_time: int
    ) -> float:
        """Calculate confidence score for task suggestion."""
        base_confidence = 0.7
        
        # Boost confidence if task duration matches available time well
        time_match = 1 - abs(suggestion["duration"] - available_time) / available_time
        time_bonus = min(0.2, time_match * 0.2)
        
        # Energy level matching bonus
        energy_bonus = 0.1 if energy in ["high", "medium"] else 0.05
        
        return min(0.95, base_confidence + time_bonus + energy_bonus)
    
    def _get_energy_specific_tip(self, energy_level: str) -> str:
        """Get ADHD-specific tip based on energy level."""
        tips = {
            "high": "🔥 High energy is precious - use it for your biggest challenges!",
            "medium": "⚖️ Balanced energy is perfect for steady progress and planning.",
            "low": "🌱 Low energy doesn't mean no progress - gentle tasks still count!"
        }
        return tips.get(energy_level, "🧠 Listen to your brain and work with its natural rhythms!")
    
    async def analyze_task_patterns(self, user_id: int) -> Dict[str, Any]:
        """
        Analyze user's task completion patterns for ADHD insights.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with pattern analysis and recommendations
        """
        # This would typically query a database
        # For now, return mock analysis
        return {
            "patterns_found": [
                "🌅 Most productive between 8-10 AM",
                "📅 Tuesdays show highest completion rates",
                "⏰ Tasks under 30 minutes have 85% success rate",
                "🔄 Break reminders improve focus by 40%"
            ],
            "recommendations": [
                "Schedule important tasks in the morning",
                "Use Tuesday energy for challenging projects", 
                "Break large tasks into 25-minute chunks",
                "Maintain current break schedule"
            ],
            "adhd_insights": {
                "hyperfocus_frequency": "2-3 times per week",
                "optimal_task_duration": "25 minutes",
                "energy_peak_time": "8:30 AM",
                "procrastination_triggers": [
                    "Unclear task descriptions",
                    "Tasks estimated over 45 minutes",
                    "More than 5 pending tasks visible"
                ]
            }
        }
    
    async def get_motivational_boost(self, context: str = "general") -> Dict[str, str]:
        """
        Generate ADHD-friendly motivational messages.
        
        Args:
            context: Context for the motivation ("task_start", "task_complete", "break", "general")
            
        Returns:
            Motivational message with emoji and encouragement
        """
        motivations = {
            "task_start": [
                "🚀 Ready to launch into this task? You've got the energy!",
                "💪 One task at a time - that's how mountains get moved!",
                "🎯 Focus mode activated! Your ADHD superpowers are ready!"
            ],
            "task_complete": [
                "🎉 Task crushed! Your dopamine receptors are doing a happy dance!",
                "⭐ Another win in the books! You're building unstoppable momentum!",
                "🏆 ADHD brain for the win! Look at that accomplished task!"
            ],
            "break": [
                "🌸 Break time! Your brain deserves this recharge moment.",
                "☕ Perfect break timing - you're mastering the art of sustainable focus!",
                "🧘 Rest is productive too. Your future focused self will thank you!"
            ],
            "general": [
                "🧠 Your ADHD brain is unique and powerful - embrace it!",
                "✨ Progress over perfection, always. You're doing great!",
                "🌟 Every task completed is a victory worth celebrating!"
            ]
        }
        
        context_messages = motivations.get(context, motivations["general"])
        selected_message = random.choice(context_messages)
        
        return {
            "message": selected_message,
            "context": context,
            "adhd_affirmation": "Your brain works differently, and that's your strength! 🧠💫"
        }


# Singleton instance for easy access
ai_service = ADHDAIService()
