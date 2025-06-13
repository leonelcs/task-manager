"""
User model for ADHD Task Manager.
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # ADHD-specific profile
    adhd_profile = Column(JSON, default={
        "energy_patterns": {
            "morning": "high",
            "afternoon": "medium", 
            "evening": "low"
        },
        "focus_duration": {
            "optimal": 25,
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
            "overwhelm_threshold": 5,
            "complexity_limit": "medium",
            "notification_frequency": "gentle"
        }
    })
    
    # Statistics
    stats = Column(JSON, default={
        "tasks_completed_today": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "total_tasks_completed": 0
    })
    
    # Relationships
    owned_projects = relationship("Project", back_populates="owner")
    group_memberships = relationship("GroupMembership", back_populates="user")
    tasks = relationship("Task", back_populates="assigned_user")
    energy_logs = relationship("EnergyLog", back_populates="user")


class EnergyLog(Base):
    __tablename__ = "energy_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    energy_level = Column(String(10), nullable=False)  # low, medium, high
    logged_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_minutes = Column(Integer)  # How long this energy level lasted
    notes = Column(Text)
    
    # Relationship
    user = relationship("User", back_populates="energy_logs")
