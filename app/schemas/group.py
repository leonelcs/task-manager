"""
Pydantic schemas for Group entities.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class GroupRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Group name")
    description: Optional[str] = Field(None, description="Group description")


class GroupCreate(GroupBase):
    """Schema for creating a new group."""
    adhd_settings: Optional[Dict[str, Any]] = Field(
        default={
            "group_focus_sessions": True,
            "shared_energy_tracking": False,
            "group_dopamine_celebrations": True,
            "collaborative_task_chunking": True,
            "group_break_reminders": True,
            "accountability_features": True
        },
        description="ADHD-specific group settings"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "ADHD Support Squad",
                "description": "A supportive group for people with ADHD to collaborate on tasks and projects",
                "adhd_settings": {
                    "group_focus_sessions": True,
                    "group_dopamine_celebrations": True,
                    "accountability_features": True
                }
            }
        }


class GroupUpdate(BaseModel):
    """Schema for updating a group."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    adhd_settings: Optional[Dict[str, Any]] = None


class GroupMemberInfo(BaseModel):
    """Schema for group member information."""
    user_id: int
    username: str
    role: GroupRole
    joined_at: datetime
    is_active: bool
    member_settings: Dict[str, Any]


class GroupResponse(GroupBase):
    """Schema for group response."""
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    adhd_settings: Dict[str, Any]
    
    # Computed fields
    member_count: int = Field(0, description="Number of active members")
    project_count: int = Field(0, description="Number of associated projects")
    
    class Config:
        from_attributes = True


class GroupListResponse(BaseModel):
    """Schema for group list response."""
    id: int
    name: str
    description: Optional[str]
    created_by: int
    member_count: int
    project_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class GroupInvitation(BaseModel):
    """Schema for group invitation."""
    group_id: int
    user_email: str = Field(..., description="Email of user to invite")
    role: GroupRole = Field(GroupRole.MEMBER, description="Role for the invited user")
    message: Optional[str] = Field(None, description="Optional invitation message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "group_id": 1,
                "user_email": "friend@email.com", 
                "role": "member",
                "message": "Join our ADHD support group!"
            }
        }


class GroupMembershipUpdate(BaseModel):
    """Schema for updating group membership."""
    role: Optional[GroupRole] = None
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
