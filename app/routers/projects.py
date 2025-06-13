"""
Project router for ADHD Task Manager with collaborative features.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectInvitation, ProjectJoinRequest, ProjectType, ProjectStatus
)

router = APIRouter()

@router.get("/", response_model=List[ProjectListResponse], summary="Get user's projects")
async def get_projects(
    project_type: Optional[ProjectType] = Query(None, description="Filter by project type"),
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    limit: int = Query(20, ge=1, le=100, description="Number of projects to return")
):
    """
    Get user's projects with ADHD-friendly filtering and presentation.
    
    **ADHD Features:**
    - Limited results to prevent overwhelm
    - Clear status-based organization
    - Project type categorization for focus
    - Progress indicators for motivation
    """
    # Mock data for now - replace with database queries
    mock_projects = [
        {
            "id": 1,
            "name": "ADHD-Friendly Home Organization",
            "description": "Organize living space using ADHD techniques and group accountability",
            "project_type": ProjectType.SHARED,
            "status": ProjectStatus.ACTIVE,
            "owner_id": 1,
            "collaborator_count": 3,
            "task_count": 12,
            "completion_percentage": 45.5,
            "created_at": "2025-06-10T10:00:00Z",
            "due_date": "2025-07-15T17:00:00Z"
        },
        {
            "id": 2, 
            "name": "Personal Morning Routine",
            "description": "Build a consistent ADHD-friendly morning routine",
            "project_type": ProjectType.PERSONAL,
            "status": ProjectStatus.ACTIVE,
            "owner_id": 1,
            "collaborator_count": 0,
            "task_count": 8,
            "completion_percentage": 75.0,
            "created_at": "2025-06-08T08:00:00Z",
            "due_date": None
        },
        {
            "id": 3,
            "name": "ADHD Study Techniques Sharing",
            "description": "Open community project for sharing effective ADHD study methods",
            "project_type": ProjectType.PUBLIC,
            "status": ProjectStatus.ACTIVE,
            "owner_id": 2,
            "collaborator_count": 15,
            "task_count": 25,
            "completion_percentage": 30.2,
            "created_at": "2025-06-05T14:00:00Z",
            "due_date": None
        }
    ]
    
    # Apply filters
    filtered_projects = mock_projects
    if project_type:
        filtered_projects = [p for p in filtered_projects if p["project_type"] == project_type]
    if status:
        filtered_projects = [p for p in filtered_projects if p["status"] == status]
    
    limited_projects = filtered_projects[:limit]
    
    return limited_projects

@router.post("/", response_model=ProjectResponse, summary="Create a new project")
async def create_project(project: ProjectCreate):
    """
    Create a new project with ADHD-friendly features and collaboration support.
    
    **ADHD Features:**
    - Automatic project breakdown suggestions
    - Collaboration difficulty balancing
    - Built-in accountability features
    - Dopamine reward system setup
    """
    # Mock creation - replace with database logic
    new_project = {
        "id": 4,
        "name": project.name,
        "description": project.description,
        "project_type": project.project_type,
        "status": project.status,
        "owner_id": 1,  # Current user
        "group_id": project.group_id,
        "is_active": True,
        "is_public_joinable": project.is_public_joinable,
        "max_collaborators": project.max_collaborators,
        "created_at": "2025-06-13T12:00:00Z",
        "updated_at": None,
        "completed_at": None,
        "start_date": project.start_date,
        "due_date": project.due_date,
        "adhd_features": {
            "use_pomodoro_sessions": True,
            "enable_group_accountability": project.project_type != ProjectType.PERSONAL,
            "shared_dopamine_rewards": True,
            "collective_break_reminders": True,
            "energy_sync_recommendations": False,
            "difficulty_balancing": True,
            "hyperfocus_protection": True,
            "progress_celebrations": {
                "milestone_rewards": True,
                "team_celebrations": project.project_type != ProjectType.PERSONAL,
                "individual_recognition": True
            }
        },
        "metrics": {
            "total_tasks": 0,
            "completed_tasks": 0,
            "total_focus_sessions": 0,
            "total_break_time": 0,
            "average_task_duration": 0,
            "collaboration_score": 0,
            "dopamine_events": 0
        },
        "collaborator_count": 0,
        "task_count": 0,
        "completion_percentage": 0.0
    }
    
    return new_project

@router.get("/{project_id}", response_model=ProjectResponse, summary="Get project details")
async def get_project(project_id: int):
    """
    Get detailed project information with ADHD insights and collaboration status.
    """
    if project_id == 1:
        return {
            "id": 1,
            "name": "ADHD-Friendly Home Organization",
            "description": "Organize living space using ADHD techniques and group accountability",
            "project_type": ProjectType.SHARED,
            "status": ProjectStatus.ACTIVE,
            "owner_id": 1,
            "group_id": None,
            "is_active": True,
            "is_public_joinable": False,
            "max_collaborators": 5,
            "created_at": "2025-06-10T10:00:00Z",
            "updated_at": "2025-06-12T14:30:00Z",
            "completed_at": None,
            "start_date": "2025-06-10T10:00:00Z",
            "due_date": "2025-07-15T17:00:00Z",
            "adhd_features": {
                "use_pomodoro_sessions": True,
                "enable_group_accountability": True,
                "shared_dopamine_rewards": True,
                "collective_break_reminders": True,
                "energy_sync_recommendations": True,
                "difficulty_balancing": True,
                "hyperfocus_protection": True,
                "progress_celebrations": {
                    "milestone_rewards": True,
                    "team_celebrations": True,
                    "individual_recognition": True
                }
            },
            "metrics": {
                "total_tasks": 12,
                "completed_tasks": 5,
                "total_focus_sessions": 18,
                "total_break_time": 135,
                "average_task_duration": 28,
                "collaboration_score": 8.5,
                "dopamine_events": 23
            },
            "collaborator_count": 3,
            "task_count": 12,
            "completion_percentage": 41.7
        }
    
    raise HTTPException(status_code=404, detail="Project not found")

@router.put("/{project_id}", response_model=ProjectResponse, summary="Update project")
async def update_project(project_id: int, project_update: ProjectUpdate):
    """
    Update project with ADHD-friendly change management.
    
    **ADHD Features:**
    - Gentle transition notifications
    - Impact assessment on collaborators
    - Progress preservation
    - Motivation maintenance
    """
    return {
        "message": f"🎯 Project {project_id} updated successfully!",
        "adhd_tip": "🔄 Changes are part of the ADHD journey - adapt and keep going!",
        "impact_summary": "Updated settings will apply to future tasks and sessions"
    }

@router.post("/{project_id}/invite", summary="Invite user to project")
async def invite_to_project(project_id: int, invitation: ProjectInvitation):
    """
    Invite a user to collaborate on a project with ADHD-friendly onboarding.
    
    **ADHD Features:**
    - Clear role expectations
    - Collaboration guidelines
    - Supportive welcome message
    - ADHD-specific collaboration tips
    """
    return {
        "message": f"🎉 Invitation sent to {invitation.user_email}!",
        "invitation_details": {
            "project_id": project_id,
            "recipient": invitation.user_email,
            "role": invitation.role,
            "expires_in": "7 days"
        },
        "adhd_benefits": [
            "Shared accountability and support",
            "Different perspectives and energy",
            "Reduced isolation in task management",
            "Collaborative dopamine boosts"
        ],
        "collaboration_tips": [
            "🤝 Set clear expectations about availability",
            "⏰ Respect different energy patterns",
            "🎯 Celebrate small wins together",
            "💬 Use encouraging communication"
        ]
    }

@router.post("/{project_id}/join", summary="Join a public project")
async def join_public_project(project_id: int, join_request: ProjectJoinRequest):
    """
    Join a public project with ADHD-friendly onboarding.
    """
    return {
        "message": f"🚀 Successfully joined project {project_id}!",
        "welcome_message": "Welcome to the ADHD community project!",
        "onboarding_tips": [
            "📋 Check out existing tasks to find your fit",
            "💪 Start with small contributions to build confidence", 
            "🤝 Introduce yourself to other collaborators",
            "⚡ Share your ADHD superpowers with the team"
        ],
        "project_guidelines": {
            "be_supportive": "We lift each other up",
            "respect_differences": "Every ADHD brain is unique",
            "celebrate_progress": "Small wins are big wins",
            "communicate_openly": "Share struggles and successes"
        }
    }

@router.get("/{project_id}/collaborators", summary="Get project collaborators")
async def get_project_collaborators(project_id: int):
    """
    Get project collaborators with ADHD-friendly team overview.
    """
    mock_collaborators = [
        {
            "user_id": 1,
            "username": "project_owner",
            "role": "owner",
            "joined_at": "2025-06-10T10:00:00Z",
            "is_active": True,
            "contribution_stats": {
                "tasks_completed": 5,
                "focus_sessions_joined": 8,
                "helpful_comments": 12,
                "dopamine_given": 15,
                "last_active": "2025-06-13T09:30:00Z"
            }
        },
        {
            "user_id": 2,
            "username": "adhd_helper",
            "role": "collaborator", 
            "joined_at": "2025-06-11T14:00:00Z",
            "is_active": True,
            "contribution_stats": {
                "tasks_completed": 3,
                "focus_sessions_joined": 5,
                "helpful_comments": 8,
                "dopamine_given": 10,
                "last_active": "2025-06-12T16:45:00Z"
            }
        }
    ]
    
    return {
        "collaborators": mock_collaborators,
        "team_stats": {
            "total_collaborators": len(mock_collaborators),
            "active_today": 2,
            "total_tasks_completed": 8,
            "team_focus_time": 325,  # minutes
            "dopamine_exchanges": 25
        },
        "team_energy": "🔥 High collaborative energy!",
        "motivation": "🌟 Amazing teamwork - keep supporting each other!"
    }

@router.get("/public/discover", summary="Discover public projects")
async def discover_public_projects(
    limit: int = Query(10, ge=1, le=50, description="Number of projects to return")
):
    """
    Discover public ADHD-friendly projects to join.
    
    **ADHD Features:**
    - Curated for ADHD community
    - Clear difficulty indicators
    - Supportive community focus
    - Beginner-friendly options
    """
    mock_public_projects = [
        {
            "id": 3,
            "name": "ADHD Study Techniques Sharing",
            "description": "Share and learn effective study methods for ADHD brains",
            "collaborator_count": 15,
            "task_count": 25,
            "completion_percentage": 30.2,
            "difficulty": "beginner-friendly",
            "tags": ["study", "techniques", "community"],
            "welcomes_beginners": True
        },
        {
            "id": 5,
            "name": "ADHD Meal Prep Challenge", 
            "description": "Weekly meal prep challenges designed for ADHD executive function",
            "collaborator_count": 8,
            "task_count": 15,
            "completion_percentage": 60.0,
            "difficulty": "moderate",
            "tags": ["meal-prep", "routine", "health"],
            "welcomes_beginners": True
        }
    ]
    
    return {
        "public_projects": mock_public_projects[:limit],
        "discovery_tip": "🔍 Look for projects that match your current energy and interests!",
        "community_message": "🤝 The ADHD community is here to support each other!",
        "joining_benefits": [
            "Learn from others' ADHD strategies",
            "Get accountability and motivation",
            "Share your unique strengths",
            "Build supportive connections"
        ]
    }
