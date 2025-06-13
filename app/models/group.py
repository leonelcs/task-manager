"""
Group model for collaborative features in ADHD Task Manager.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class GroupRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # ADHD-focused group settings
    adhd_settings = Column("adhd_settings", Text, default="""{
        "group_focus_sessions": true,
        "shared_energy_tracking": false,
        "group_dopamine_celebrations": true,
        "collaborative_task_chunking": true,
        "group_break_reminders": true,
        "accountability_features": true
    }""")
    
    # Creator/owner of the group
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User")
    memberships = relationship("GroupMembership", back_populates="group")
    projects = relationship("Project", back_populates="group")


class GroupMembership(Base):
    __tablename__ = "group_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(GroupRole), default=GroupRole.MEMBER)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # ADHD-specific member settings
    member_settings = Column("member_settings", Text, default="""{
        "share_energy_patterns": false,
        "receive_group_motivations": true,
        "participate_in_group_focus": true,
        "notification_preferences": "normal"
    }""")
    
    # Relationships
    group = relationship("Group", back_populates="memberships")
    user = relationship("User", back_populates="group_memberships")
