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
    AI service for ADHD-specific task management with Rock/Pebbles/Sand awareness.
    """
    
    def __init__(self):
        self.user_patterns = {}
        self.task_history = []

    async def get_impact_aware_suggestions(
        self,
        current_energy: str = "medium",
        available_time: int = 30,
        current_time_of_day: str = "afternoon",
        user_preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get task suggestions based on Rock/Pebbles/Sand classification and current context.
        
        Args:
            current_energy: User's current energy level
            available_time: Available time in minutes
            current_time_of_day: Current time of day
            user_preferences: User's ADHD preferences
            
        Returns:
            List of task suggestions with impact classification
        """
        suggestions = []
        
        # Rock suggestions - for high energy and good time blocks
        if current_energy == "high" and available_time >= 60:
            rock_suggestions = [
                {
                    "task_type": "rock",
                    "title": "Work on your most important project milestone",
                    "description": "Tackle the big, high-impact task that will move your major goals forward",
                    "reasoning": f"🏔️ ROCK TIME! High energy ({current_energy}) + good time block ({available_time}min) = perfect for your most impactful work",
                    "confidence": 0.9,
                    "estimated_duration": min(available_time, 90),
                    "adhd_benefits": [
                        "Maximum impact on your goals",
                        "Uses your peak energy wisely", 
                        "Major dopamine payoff when completed",
                        "Moves the needle on important outcomes"
                    ],
                    "energy_match": "perfect",
                    "time_match": "excellent"
                }
            ]
            suggestions.extend(rock_suggestions)
        
        # Pebbles suggestions - for medium energy or when building momentum
        if current_energy in ["medium", "high"] and available_time >= 15:
            pebbles_suggestions = [
                {
                    "task_type": "pebbles", 
                    "title": "Complete an important routine or follow-up task",
                    "description": "Handle meaningful tasks that support your bigger goals and build momentum",
                    "reasoning": f"⚡ PEBBLES PERFECT! Your energy ({current_energy}) and time ({available_time}min) are ideal for solid progress",
                    "confidence": 0.85,
                    "estimated_duration": min(available_time, 45),
                    "adhd_benefits": [
                        "Builds productive momentum",
                        "Solid sense of accomplishment", 
                        "Supports your bigger goals",
                        "Good dopamine hit without overwhelm"
                    ],
                    "energy_match": "good",
                    "time_match": "good"
                }
            ]
            suggestions.extend(pebbles_suggestions)
        
        # Sand suggestions - for low energy, short time, or filling gaps
        if available_time <= 20 or current_energy == "low":
            sand_suggestions = [
                {
                    "task_type": "sand",
                    "title": "Handle quick organizational or administrative tasks", 
                    "description": "Take care of small, low-pressure tasks that still feel productive",
                    "reasoning": f"✨ SAND SWEEP! Low pressure tasks perfect for your current state - {current_energy} energy, {available_time}min available",
                    "confidence": 0.75,
                    "estimated_duration": min(available_time, 15),
                    "adhd_benefits": [
                        "Low mental load",
                        "Easy sense of completion",
                        "Fills time productively", 
                        "No pressure or overwhelm"
                    ],
                    "energy_match": "perfect",
                    "time_match": "perfect"
                }
            ]
            suggestions.extend(sand_suggestions)
        
        # Time-of-day specific suggestions
        if current_time_of_day == "morning" and current_energy == "high":
            suggestions.insert(0, {
                "task_type": "rock",
                "title": "Your #1 priority task for today",
                "description": "This is prime time - tackle your most important, high-impact work",
                "reasoning": "🌅 GOLDEN HOUR! Morning + high energy = rock task time. This is when magic happens!",
                "confidence": 0.95,
                "estimated_duration": min(available_time, 120),
                "adhd_benefits": [
                    "Peak brain performance",
                    "Maximum focus capacity",
                    "Sets positive tone for whole day",
                    "Highest impact potential"
                ],
                "energy_match": "perfect",
                "time_match": "optimal"
            })
        
        # Fallback for any situation
        if not suggestions:
            suggestions.append({
                "task_type": "sand",
                "title": "Take a mindful 5-minute reset break",
                "description": "Sometimes the best 'task' is giving your brain a moment to recharge",
                "reasoning": "🧠 BRAIN CARE! Taking a break is productive too - it improves your next task performance",
                "confidence": 0.8,
                "estimated_duration": 5,
                "adhd_benefits": [
                    "Mental reset and clarity",
                    "Prevents burnout",
                    "Improves focus for next task",
                    "Self-care is productive"
                ],
                "energy_match": "restorative", 
                "time_match": "flexible"
            })
        
        return suggestions[:3]  # Return top 3 suggestions

    async def analyze_impact_patterns(self, user_id: int, tasks_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze user's task completion patterns specifically for Rock/Pebbles/Sand distribution.
        
        Args:
            user_id: User identifier
            tasks_history: Historical task data
            
        Returns:
            Analysis with Rock/Pebbles/Sand insights
        """
        # Mock analysis - in reality this would query actual user data
        return {
            "impact_distribution_analysis": {
                "current_balance": {
                    "rocks_percentage": 15,  # Good - not too many
                    "pebbles_percentage": 65,  # Perfect - majority
                    "sand_percentage": 20   # Good - manageable amount
                },
                "completion_rates_by_impact": {
                    "rock": 78,      # Rock tasks get done less often but have huge impact
                    "pebbles": 89,   # Pebbles have highest completion rate
                    "sand": 67       # Sand tasks often get delayed
                },
                "optimal_daily_distribution": {
                    "rocks": "1-2 maximum",
                    "pebbles": "3-5 for momentum", 
                    "sand": "Fill gaps naturally"
                }
            },
            "energy_impact_correlation": {
                "best_time_for_rocks": "8:00-10:00 AM (peak energy)",
                "pebbles_sweet_spot": "Throughout day between rocks",
                "sand_filler_times": "Low energy periods, transition times"
            },
            "recommendations": [
                "🏔️ Schedule your 1-2 rock tasks during peak energy hours",
                "⚡ Use pebbles tasks to build momentum between big tasks",
                "✨ Let sand tasks fill natural gaps - don't schedule them first",
                "🎯 When overwhelmed, focus only on rocks and pebbles",
                "💡 Break large rocks into smaller rocks or pebbles"
            ],
            "adhd_insights": {
                "hyperfocus_tendency": "Moderate risk with rock tasks",
                "optimal_task_switching": "Rock → Break → Pebbles → Sand",
                "procrastination_pattern": "Tends to delay rocks when overwhelmed",
                "momentum_builder": "Completing pebbles increases rock completion rate by 40%"
            }
        }

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
