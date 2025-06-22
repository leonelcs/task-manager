"""
SharedGroup model for collaborative features in ADHD Task Manager.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import CHAR
from app.database import Base
import enum
import uuid


class SharedGroupRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class SharedGroup(Base):
    __tablename__ = "shared_groups"
    
    id = Column(CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # ADHD-focused group settings as individual columns
    group_focus_sessions = Column(Boolean, default=True)
    shared_energy_tracking = Column(Boolean, default=False)
    group_dopamine_celebrations = Column(Boolean, default=True)
    collaborative_task_chunking = Column(Boolean, default=True)
    group_break_reminders = Column(Boolean, default=True)
    accountability_features = Column(Boolean, default=True)
    
    # Creator/owner of the group
    created_by = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User")
    memberships = relationship("SharedGroupMembership", back_populates="shared_group")
    projects = relationship("Project", back_populates="shared_group")


class SharedGroupMembership(Base):
    __tablename__ = "shared_group_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    shared_group_id = Column(CHAR(36), ForeignKey("shared_groups.id"), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(SharedGroupRole), default=SharedGroupRole.MEMBER)
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
    shared_group = relationship("SharedGroup", back_populates="memberships")
    user = relationship("User", back_populates="shared_group_memberships")
