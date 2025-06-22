"""
Pydantic schemas for SharedGroup entities.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SharedGroupRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class SharedGroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="SharedGroup name")
    description: Optional[str] = Field(None, description="SharedGroup description")


class SharedGroupCreate(SharedGroupBase):
    """Schema for creating a new shared group."""
    # ADHD-specific group settings as individual fields
    group_focus_sessions: bool = Field(True, description="Enable group focus sessions")
    shared_energy_tracking: bool = Field(False, description="Enable shared energy tracking")
    group_dopamine_celebrations: bool = Field(True, description="Enable group dopamine celebrations")
    collaborative_task_chunking: bool = Field(True, description="Enable collaborative task chunking")
    group_break_reminders: bool = Field(True, description="Enable group break reminders")
    accountability_features: bool = Field(True, description="Enable accountability features")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "ADHD Support Squad",
                "description": "A supportive group for people with ADHD to collaborate on tasks and projects",
                "group_focus_sessions": True,
                "group_dopamine_celebrations": True,
                "accountability_features": True,
                "shared_energy_tracking": False,
                "collaborative_task_chunking": True,
                "group_break_reminders": True
            }
        }


class SharedGroupUpdate(BaseModel):
    """Schema for updating a shared group."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    # ADHD-specific group settings as individual fields
    group_focus_sessions: Optional[bool] = None
    shared_energy_tracking: Optional[bool] = None
    group_dopamine_celebrations: Optional[bool] = None
    collaborative_task_chunking: Optional[bool] = None
    group_break_reminders: Optional[bool] = None
    accountability_features: Optional[bool] = None


class SharedGroupMemberInfo(BaseModel):
    """Schema for shared group member information."""
    user_id: str
    username: str
    role: SharedGroupRole
    joined_at: datetime
    is_active: bool
    member_settings: Dict[str, Any]


class SharedGroupResponse(SharedGroupBase):
    """Schema for shared group response."""
    id: str
    created_by: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # ADHD-specific group settings as individual fields
    group_focus_sessions: bool
    shared_energy_tracking: bool
    group_dopamine_celebrations: bool
    collaborative_task_chunking: bool
    group_break_reminders: bool
    accountability_features: bool
    
    # Computed fields
    member_count: int = Field(0, description="Number of active members")
    project_count: int = Field(0, description="Number of associated projects")
    
    class Config:
        from_attributes = True


class SharedGroupListResponse(BaseModel):
    """Schema for shared group list response."""
    id: str
    name: str
    description: Optional[str]
    created_by: str
    member_count: int
    project_count: int
    is_active: bool
    created_at: datetime
    
    # ADHD-specific group settings as individual fields
    group_focus_sessions: bool
    shared_energy_tracking: bool
    group_dopamine_celebrations: bool
    collaborative_task_chunking: bool
    group_break_reminders: bool
    accountability_features: bool
    
    class Config:
        from_attributes = True


class SharedGroupInvitation(BaseModel):
    """Schema for shared group invitation."""
    shared_group_id: str
    user_email: str = Field(..., description="Email of user to invite")
    role: SharedGroupRole = Field(SharedGroupRole.MEMBER, description="Role for the invited user")
    message: Optional[str] = Field(None, description="Optional invitation message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "shared_group_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_email": "friend@email.com", 
                "role": "member",
                "message": "Join our ADHD support group!"
            }
        }


class SharedGroupMembershipUpdate(BaseModel):
    """Schema for updating shared group membership."""
    role: Optional[SharedGroupRole] = None
    is_active: Optional[bool] = None
    member_settings: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "admin",
                "member_settings": {
                    "share_energy_patterns": True,
                    "receive_group_motivations": True,
                    "participate_in_group_focus": True
                }
            }
        }
