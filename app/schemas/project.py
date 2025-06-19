"""
Pydantic schemas for Project entities.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectType(str, Enum):
    PERSONAL = "personal"
    SHARED = "shared"
    PUBLIC = "public"


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    project_type: ProjectType = Field(ProjectType.PERSONAL, description="Project visibility type")
    status: ProjectStatus = Field(ProjectStatus.PLANNING, description="Project status")
    is_public_joinable: bool = Field(False, description="Allow public users to join")
    max_collaborators: int = Field(10, ge=1, le=100, description="Maximum number of collaborators")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    due_date: Optional[datetime] = Field(None, description="Project due date")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    group_id: Optional[int] = Field(None, description="Optional group to associate with")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "ADHD-Friendly Home Organization",
                "description": "Organize living space using ADHD-friendly techniques and accountability",
                "project_type": "shared",
                "status": "planning", 
                "is_public_joinable": False,
                "max_collaborators": 5,
                "group_id": None
            }
        }


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    project_type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = None
    is_public_joinable: Optional[bool] = None
    max_collaborators: Optional[int] = Field(None, ge=1, le=100)
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    group_id: Optional[int] = Field(None, description="Optional group to associate with")


class ProjectCollaboratorInfo(BaseModel):
    """Schema for project collaborator information."""
    user_id: int
    username: str
    role: str
    joined_at: datetime
    is_active: bool
    contribution_stats: Dict[str, Any]


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    owner_id: int
    group_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # ADHD-specific features
    adhd_features: Dict[str, Any]
    metrics: Dict[str, Any]
    
    # Computed fields
    collaborator_count: int = Field(0, description="Number of active collaborators")
    task_count: int = Field(0, description="Number of tasks in project")
    completion_percentage: float = Field(0.0, description="Project completion percentage")
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for project list response."""
    id: int
    name: str
    description: Optional[str]
    project_type: ProjectType
    status: ProjectStatus
    owner_id: int
    collaborator_count: int
    task_count: int
    completion_percentage: float
    created_at: datetime
    due_date: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProjectInvitation(BaseModel):
    """Schema for project invitation."""
    project_id: int
    user_email: str = Field(..., description="Email of user to invite")
    role: str = Field("collaborator", description="Role for the invited user")
    message: Optional[str] = Field(None, description="Optional invitation message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "user_email": "friend@email.com",
                "role": "collaborator",
                "message": "Join me in organizing our ADHD-friendly workspace!"
            }
        }


class ProjectJoinRequest(BaseModel):
    """Schema for joining a public project."""
    project_id: int
    message: Optional[str] = Field(None, description="Optional message to project owner")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "message": "I'd love to help with this ADHD organization project!"
            }
        }
