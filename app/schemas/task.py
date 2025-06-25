"""
Pydantic schemas for Task entities.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    BLOCKED = "blocked"


class ADHDTaskType(str, Enum):
    ROUTINE = "routine"
    PROJECT = "project"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"
    HYPERFOCUS = "hyperfocus"
    COLLABORATIVE = "collaborative"


class ADHDImpactSize(str, Enum):
    """
    ADHD-friendly task impact classification using the Rock/Pebbles/Sand metaphor.
    
    - ROCK: Huge and super important - these are your big, high-impact tasks that move the needle
    - PEBBLES: Small but still important - great for building momentum and getting quick wins
    - SAND: Possibly delegatable or nice-to-have - fills in the gaps but shouldn't dominate your focus
    """
    ROCK = "rock"
    PEBBLES = "pebbles"  
    SAND = "sand"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    task_type: ADHDTaskType = Field(ADHDTaskType.ROUTINE, description="ADHD task type")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority level")
    complexity: str = Field("medium", description="Task complexity: low, medium, high")
    impact_size: ADHDImpactSize = Field(ADHDImpactSize.PEBBLES, description="Rock/Pebbles/Sand classification")
    estimated_duration: Optional[int] = Field(None, ge=1, description="Estimated duration in minutes")
    due_date: Optional[Union[datetime, date, str]] = Field(None, description="Task due date")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    
    @validator('due_date', pre=True)
    def parse_due_date(cls, v):
        if isinstance(v, str):
            try:
                # Try parsing as date first (YYYY-MM-DD)
                if len(v) == 10 and v.count('-') == 2:
                    return datetime.strptime(v, '%Y-%m-%d')
                # Try parsing as datetime
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return v
        return v


class TaskCreate(TaskBase):
    """Schema for creating a new task with ADHD-friendly features."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete quarterly report",
                "description": "Write and submit Q3 performance report for team review",
                "task_type": "project",
                "priority": "high",
                "complexity": "high",
                "impact_size": "rock",
                "estimated_duration": 180,
                "due_date": "2025-06-20T17:00:00Z",
                "project_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    task_type: Optional[ADHDTaskType] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    complexity: Optional[str] = None
    impact_size: Optional[ADHDImpactSize] = None
    estimated_duration: Optional[int] = Field(None, ge=1)
    due_date: Optional[Union[datetime, date, str]] = None
    project_id: Optional[str] = None
    
    @validator('due_date', pre=True)
    def parse_due_date(cls, v):
        if isinstance(v, str):
            try:
                # Try parsing as date first (YYYY-MM-DD)
                if len(v) == 10 and v.count('-') == 2:
                    return datetime.strptime(v, '%Y-%m-%d')
                # Try parsing as datetime
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return v
        return v


class TaskResponse(TaskBase):
    """Schema for task response with full details."""
    id: int
    status: TaskStatus
    created_by: str
    assigned_user_id: Optional[str]
    actual_duration: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # ADHD-specific features
    adhd_features: Dict[str, Any]
    completion_history: List[Dict[str, Any]]
    focus_sessions: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list response (simplified)."""
    id: int
    title: str
    task_type: ADHDTaskType
    priority: TaskPriority
    status: TaskStatus
    impact_size: ADHDImpactSize
    estimated_duration: Optional[int]
    due_date: Optional[datetime]
    created_at: datetime
    project_id: Optional[str] = None
    
    # Key ADHD features for list view
    dopamine_reward: str = Field("🎉 Task completed!")
    energy_level_required: str = Field("medium")
    
    # Project information for organizing tasks
    project_name: Optional[str] = None
    project_type: Optional[str] = None  # "personal", "shared", "public"
    
    class Config:
        from_attributes = True


class TaskComplete(BaseModel):
    """Schema for task completion data."""
    actual_duration: Optional[int] = Field(None, ge=1, description="Actual time taken in minutes")
    completion_notes: Optional[str] = Field(None, description="Notes about task completion")


class TaskImpactClassification(BaseModel):
    """Schema for explaining the Rock/Pebbles/Sand system."""
    rock: Dict[str, str] = Field(default={
        "description": "Huge and super important tasks",
        "characteristics": "High impact, moves the needle, strategic importance",
        "examples": "Major project deliverables, important meetings, critical decisions",
        "adhd_tip": "🎯 Focus on 1-2 rocks per day maximum - they require your best energy"
    })
    pebbles: Dict[str, str] = Field(default={
        "description": "Small but still important tasks", 
        "characteristics": "Meaningful progress, builds momentum, supports bigger goals",
        "examples": "Follow-up emails, routine maintenance, skill development",
        "adhd_tip": "⚡ Perfect for filling gaps between rocks or when energy is medium"
    })
    sand: Dict[str, str] = Field(default={
        "description": "Nice to have, possibly delegatable tasks",
        "characteristics": "Low impact, optional, can be postponed without major consequences", 
        "examples": "Organizing files, reading optional articles, minor optimizations",
        "adhd_tip": "🌊 Let these fill in naturally - don't let sand crowd out your rocks!"
    })


class TaskSuggestion(BaseModel):
    """Schema for AI task suggestions based on impact classification."""
    suggested_task: str
    impact_size: ADHDImpactSize
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    adhd_benefits: List[str]
    estimated_duration: int
