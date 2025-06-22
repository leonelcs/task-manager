"""
Pydantic schemas for Shared Group Invitation entities.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class SharedGroupInvitationCreate(BaseModel):
    """Schema for creating a shared group invitation."""
    invited_email: EmailStr = Field(..., description="Email of the person to invite")
    role: str = Field("member", description="Role for the invited user")
    message: Optional[str] = Field(None, description="Optional personal message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "invited_email": "friend@example.com",
                "role": "member",
                "message": "Hey! I'd love for you to join our ADHD support group. We help each other stay focused and motivated!"
            }
        }


class SharedGroupInvitationResponse(BaseModel):
    """Schema for shared group invitation response."""
    id: str
    token: str
    shared_group_id: str
    invited_email: str
    invited_user_id: Optional[str]
    invited_by: str
    role: str
    status: InvitationStatus
    message: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    responded_at: Optional[datetime]
    
    # Group details for display
    group_name: Optional[str] = None
    group_description: Optional[str] = None
    inviter_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SharedGroupInvitationAccept(BaseModel):
    """Schema for accepting an invitation."""
    welcome_preferences: Optional[Dict[str, Any]] = Field(
        default={
            "receive_welcome_email": True,
            "join_group_focus_session": False,
            "share_energy_patterns": False
        },
        description="User preferences for joining the group"
    )


class SharedGroupInvitationList(BaseModel):
    """Schema for listing invitations."""
    invitations: list[SharedGroupInvitationResponse]
    total: int
    pending_count: int
    
    
class InvitationEmailData(BaseModel):
    """Schema for invitation email data."""
    recipient_email: str
    recipient_name: Optional[str]
    group_name: str
    group_description: Optional[str]
    inviter_name: str
    invitation_token: str
    invitation_message: Optional[str]
    invitation_url: str
    expires_at: Optional[datetime]
    
    # ADHD-specific email content
    adhd_benefits: list[str] = [
        "🤝 Supportive ADHD community",
        "⚡ Shared accountability and motivation", 
        "🎯 Collaborative task management",
        "🌟 Group dopamine celebrations",
        "💪 Reduced ADHD isolation"
    ]
    
    group_features: Optional[Dict[str, bool]] = None
