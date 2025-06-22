"""
User model for ADHD Task Manager.
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import CHAR
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    
    id = Column(CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=True)  # Made nullable for Google OAuth
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=True)  # Made nullable for Google OAuth
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # OAuth fields
    google_id = Column(String(100), unique=True, index=True, nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    provider = Column(String(50), default="local")  # 'local', 'google'
    
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
    shared_group_memberships = relationship("SharedGroupMembership", back_populates="user")
    tasks = relationship("Task", foreign_keys="Task.assigned_user_id", back_populates="assigned_user")
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    energy_logs = relationship("EnergyLog", back_populates="user")


class EnergyLog(Base):
    __tablename__ = "energy_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False, index=True)
    energy_level = Column(String(10), nullable=False)  # low, medium, high
    logged_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_minutes = Column(Integer)  # How long this energy level lasted
    notes = Column(Text)
    
    # Relationship
    user = relationship("User", back_populates="energy_logs")
