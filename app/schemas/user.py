"""
Pydantic schemas for User entities.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime


class UserBase(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "adhd_champion",
                "email": "user@example.com",
                "full_name": "Alex Smith",
                "password": "securepassword123"
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    adhd_profile: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Alex Johnson",
                "adhd_profile": {
                    "energy_patterns": {
                        "morning": "high",
                        "afternoon": "low",
                        "evening": "medium"
                    },
                    "preferences": {
                        "break_reminders": True,
                        "dopamine_rewards": True
                    }
                }
            }
        }


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    adhd_profile: Dict[str, Any]
    stats: Dict[str, Any]
    google_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    provider: str = "local"
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list response (limited info)."""
    id: int
    username: str
    full_name: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class EnergyLogBase(BaseModel):
    energy_level: str = Field(..., description="Energy level: low, medium, high")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Duration in minutes")
    notes: Optional[str] = Field(None, description="Optional notes about energy level")


class EnergyLogCreate(EnergyLogBase):
    """Schema for creating an energy log entry."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "energy_level": "high",
                "duration_minutes": 90,
                "notes": "Great morning energy after good sleep"
            }
        }


class EnergyLogResponse(EnergyLogBase):
    """Schema for energy log response."""
    id: int
    user_id: int
    logged_at: datetime
    
    class Config:
        from_attributes = True
