"""
Task model for ADHD Task Manager with project and collaboration support.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    BLOCKED = "blocked"


class ADHDTaskType(str, enum.Enum):
    ROUTINE = "routine"      # Daily habits
    PROJECT = "project"      # Larger goals
    MAINTENANCE = "maintenance"  # Regular upkeep
    EMERGENCY = "emergency"   # Urgent items
    HYPERFOCUS = "hyperfocus"  # Deep work sessions
    COLLABORATIVE = "collaborative"  # Team tasks


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    
    # Task categorization
    task_type = Column(Enum(ADHDTaskType), default=ADHDTaskType.ROUTINE)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    complexity = Column(String(10), default="medium")  # low, medium, high
    
    # Ownership and assignment
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Time management
    estimated_duration = Column(Integer)  # minutes
    actual_duration = Column(Integer)     # minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # ADHD-specific features
    adhd_features = Column(JSON, default={
        "dopamine_reward": "🎉 Task completed!",
        "break_reminder": True,
        "chunked": False,
        "subtasks": [],
        "energy_level_required": "medium",
        "best_time_of_day": "flexible",
        "focus_duration": 25,
        "hyperfocus_risk": False,
        "collaboration_boost": False
    })
    
    # Task analytics
    completion_history = Column(JSON, default=[])
    focus_sessions = Column(JSON, default=[])
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id], back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task")


class TaskComment(Base):
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    comment_type = Column(String(20), default="comment")  # comment, support, celebration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ADHD-specific comment features
    is_motivational = Column(Boolean, default=False)
    dopamine_boost = Column(Boolean, default=False)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User")
