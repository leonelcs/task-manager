"""
SharedGroup invitation model for ADHD Task Manager.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import CHAR
from app.database import Base
import enum
import uuid


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class SharedGroupInvitation(Base):
    __tablename__ = "shared_group_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    
    # Invitation details
    shared_group_id = Column(CHAR(36), ForeignKey("shared_groups.id"), nullable=False)
    invited_email = Column(String(100), nullable=False, index=True)
    invited_user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)  # If user exists
    invited_by = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    
    # Invitation settings
    role = Column(String(20), default="member")  # member, admin
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING)
    message = Column(Text)  # Optional personal message
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # Invitation expiry
    responded_at = Column(DateTime(timezone=True))
    
    # ADHD-friendly invitation features
    adhd_welcome_settings = Column(Text, default="""{
        "include_group_guidelines": true,
        "highlight_adhd_features": true,
        "suggest_first_steps": true,
        "offer_onboarding_buddy": false
    }""")
    
    # Relationships
    shared_group = relationship("SharedGroup")
    invited_user = relationship("User", foreign_keys=[invited_user_id])
    inviter = relationship("User", foreign_keys=[invited_by])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.token:
            self.token = str(uuid.uuid4())
