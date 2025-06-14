"""
Project model for ADHD Task Manager with collaborative features.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ProjectType(str, enum.Enum):
    PERSONAL = "personal"
    SHARED = "shared"  # Invite-only collaboration
    PUBLIC = "public"   # Open to any user


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    project_type = Column(Enum(ProjectType), default=ProjectType.PERSONAL)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    
    # Ownership and collaboration
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # Optional group association
    
    # Project settings
    is_active = Column(Boolean, default=True)
    is_public_joinable = Column(Boolean, default=False)  # For PUBLIC projects
    max_collaborators = Column(Integer, default=10)
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    start_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # ADHD-specific project features
    adhd_features = Column(JSON, default={
        "use_pomodoro_sessions": True,
        "enable_group_accountability": True,
        "shared_dopamine_rewards": True,
        "collective_break_reminders": True,
        "energy_sync_recommendations": False,
        "difficulty_balancing": True,
        "hyperfocus_protection": True,
        "progress_celebrations": {
            "milestone_rewards": True,
            "team_celebrations": True,
            "individual_recognition": True
        }
    })
    
    # Project metrics for ADHD insights
    metrics = Column(JSON, default={
        "total_tasks": 0,
        "completed_tasks": 0,
        "total_focus_sessions": 0,
        "total_break_time": 0,
        "average_task_duration": 0,
        "collaboration_score": 0,
        "dopamine_events": 0
    })
    
    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    group = relationship("Group", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    collaborations = relationship("ProjectCollaboration", back_populates="project")


class ProjectCollaboration(Base):
    __tablename__ = "project_collaborations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Collaboration details
    role = Column(String(20), default="collaborator")  # collaborator, reviewer, observer
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    invited_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    
    # ADHD-specific collaboration settings
    collaboration_settings = Column(JSON, default={
        "share_focus_sessions": False,
        "receive_progress_notifications": True,
        "participate_in_group_breaks": True,
        "share_energy_levels": False,
        "receive_dopamine_boosts": True,
        "task_assignment_notifications": True
    })
    
    # Collaboration stats
    contribution_stats = Column(JSON, default={
        "tasks_completed": 0,
        "focus_sessions_joined": 0,
        "helpful_comments": 0,
        "dopamine_given": 0,
        "last_active": None
    })
    
    # Relationships
    project = relationship("Project", back_populates="collaborations")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])
