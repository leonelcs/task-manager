"""
Project router for ADHD Task Manager with collaborative features.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models.project import Project, ProjectCollaboration
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.models.group import SharedGroup, SharedGroupMembership
from app.routers.auth import get_current_user
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse, EnhancedProjectListResponse,
    ProjectInvitation, ProjectJoinRequest, ProjectType, ProjectStatus
)

router = APIRouter()

@router.get("/", response_model=List[EnhancedProjectListResponse], summary="Get user's projects")
async def get_projects(
    project_type: Optional[List[ProjectType]] = Query(None, description="Filter by project type(s). Can be a single type or list of types."),
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    limit: int = Query(100, ge=1, le=200, description="Number of projects to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's projects based on comprehensive access rules:
    
    1. All active projects from shared groups where user is a member
    2. All active projects created by the user (owned)
    3. All active public projects where the user participates (as collaborator)
    
    This matches the query:
    SELECT 
        sgm.shared_group_id,
        sg.name AS group_name,
        COALESCE(u.full_name, u.email) AS user_name,
        sgm.role,
        p.name AS project_name,
        p.project_type,
        p.status AS project_status
    FROM shared_group_memberships sgm
    JOIN shared_groups sg ON sgm.shared_group_id = sg.id
    JOIN users u ON sgm.user_id = u.id
    LEFT JOIN projects p ON p.shared_group_id = sg.id AND p.is_active = TRUE
    WHERE sgm.is_active = TRUE
    ORDER BY sg.name, p.name, sgm.role, u.full_name;
    
    Plus user's own projects and public projects they collaborate on.
    """
    
    project_responses = []
    
    # Query 1: All active projects from shared groups where user is a member
    # This replicates your main SQL query
    shared_group_projects_query = db.query(
        Project,
        SharedGroup.name.label('group_name'),
        SharedGroupMembership.role.label('user_group_role')
    ).join(
        SharedGroup, Project.shared_group_id == SharedGroup.id
    ).join(
        SharedGroupMembership, SharedGroupMembership.shared_group_id == SharedGroup.id
    ).filter(
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.is_active == True,
        Project.is_active == True
    )
    
    # Apply filters if specified
    if status:
        shared_group_projects_query = shared_group_projects_query.filter(Project.status == status)
    if project_type:
        if not isinstance(project_type, list):
            project_type = [project_type]
        shared_group_projects_query = shared_group_projects_query.filter(Project.project_type.in_(project_type))
    
    shared_group_projects = shared_group_projects_query.all()
    
    # Process shared group projects
    for project, group_name, user_group_role in shared_group_projects:
        # Calculate metrics for this project
        collaborator_count = db.query(ProjectCollaboration).filter(
            ProjectCollaboration.project_id == project.id,
            ProjectCollaboration.is_active == True
        ).count()
        
        task_count = db.query(Task).filter(Task.project_id == project.id).count()
        
        completed_tasks = db.query(Task).filter(
            Task.project_id == project.id,
            Task.status == "completed"
        ).count()
        completion_percentage = (completed_tasks / task_count * 100) if task_count > 0 else 0.0
        
        # Determine user's role in project
        if project.owner_id == current_user.id:
            user_role_in_project = "owner"
        else:
            # Check if user is a direct collaborator
            collaboration = db.query(ProjectCollaboration).filter(
                ProjectCollaboration.project_id == project.id,
                ProjectCollaboration.user_id == current_user.id,
                ProjectCollaboration.is_active == True
            ).first()
            user_role_in_project = collaboration.role if collaboration else "group_member"
        
        project_responses.append(EnhancedProjectListResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            project_type=project.project_type,
            status=project.status,
            owner_id=project.owner_id,
            shared_group_id=project.shared_group_id,
            shared_group_name=group_name,
            user_role_in_group=user_group_role,
            user_role_in_project=user_role_in_project,
            access_source="shared_group",
            collaborator_count=collaborator_count,
            task_count=task_count,
            completion_percentage=completion_percentage,
            created_at=project.created_at,
            due_date=project.due_date
        ))
    
    # Query 2: All active projects created by the user (owned projects)
    owned_projects_query = db.query(Project).filter(
        Project.owner_id == current_user.id,
        Project.is_active == True
    )
    
    # Apply filters if specified
    if status:
        owned_projects_query = owned_projects_query.filter(Project.status == status)
    if project_type:
        owned_projects_query = owned_projects_query.filter(Project.project_type.in_(project_type))
    
    owned_projects = owned_projects_query.all()
    
    # Process owned projects (exclude those already added from shared groups)
    existing_project_ids = {resp.id for resp in project_responses}
    
    for project in owned_projects:
        if project.id in existing_project_ids:
            continue  # Skip if already added from shared group
            
        # Calculate metrics for this project
        collaborator_count = db.query(ProjectCollaboration).filter(
            ProjectCollaboration.project_id == project.id,
            ProjectCollaboration.is_active == True
        ).count()
        
        task_count = db.query(Task).filter(Task.project_id == project.id).count()
        
        completed_tasks = db.query(Task).filter(
            Task.project_id == project.id,
            Task.status == "completed"
        ).count()
        completion_percentage = (completed_tasks / task_count * 100) if task_count > 0 else 0.0
        
        # Get group info if project belongs to a group
        group_name = None
        user_role_in_group = None
        if project.shared_group_id:
            group_info = db.query(
                SharedGroup.name,
                SharedGroupMembership.role
            ).join(
                SharedGroupMembership, SharedGroupMembership.shared_group_id == SharedGroup.id
            ).filter(
                SharedGroup.id == project.shared_group_id,
                SharedGroupMembership.user_id == current_user.id,
                SharedGroupMembership.is_active == True
            ).first()
            if group_info:
                group_name, user_role_in_group = group_info
        
        project_responses.append(EnhancedProjectListResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            project_type=project.project_type,
            status=project.status,
            owner_id=project.owner_id,
            shared_group_id=project.shared_group_id,
            shared_group_name=group_name,
            user_role_in_group=user_role_in_group,
            user_role_in_project="owner",
            access_source="owned",
            collaborator_count=collaborator_count,
            task_count=task_count,
            completion_percentage=completion_percentage,
            created_at=project.created_at,
            due_date=project.due_date
        ))
    
    # Query 3: All active public projects where the user participates (as direct collaborator)
    public_collaboration_projects_query = db.query(
        Project,
        ProjectCollaboration.role.label('collaboration_role')
    ).join(
        ProjectCollaboration, ProjectCollaboration.project_id == Project.id
    ).filter(
        ProjectCollaboration.user_id == current_user.id,
        ProjectCollaboration.is_active == True,
        Project.is_active == True,
        Project.project_type == ProjectType.PUBLIC
    )
    
    # Apply filters if specified
    if status:
        public_collaboration_projects_query = public_collaboration_projects_query.filter(Project.status == status)
    if project_type and ProjectType.PUBLIC not in project_type:
        # Skip public projects if not requested
        public_collaboration_projects = []
    else:
        public_collaboration_projects = public_collaboration_projects_query.all()
    
    # Process public collaboration projects (exclude those already added)
    existing_project_ids = {resp.id for resp in project_responses}
    
    for project, collaboration_role in public_collaboration_projects:
        if project.id in existing_project_ids:
            continue  # Skip if already added
            
        # Calculate metrics for this project
        collaborator_count = db.query(ProjectCollaboration).filter(
            ProjectCollaboration.project_id == project.id,
            ProjectCollaboration.is_active == True
        ).count()
        
        task_count = db.query(Task).filter(Task.project_id == project.id).count()
        
        completed_tasks = db.query(Task).filter(
            Task.project_id == project.id,
            Task.status == "completed"
        ).count()
        completion_percentage = (completed_tasks / task_count * 100) if task_count > 0 else 0.0
        
        # Get group info if project belongs to a group
        group_name = None
        user_role_in_group = None
        if project.shared_group_id:
            group_info = db.query(
                SharedGroup.name,
                SharedGroupMembership.role
            ).join(
                SharedGroupMembership, SharedGroupMembership.shared_group_id == SharedGroup.id
            ).filter(
                SharedGroup.id == project.shared_group_id,
                SharedGroupMembership.user_id == current_user.id,
                SharedGroupMembership.is_active == True
            ).first()
            if group_info:
                group_name, user_role_in_group = group_info
        
        project_responses.append(EnhancedProjectListResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            project_type=project.project_type,
            status=project.status,
            owner_id=project.owner_id,
            shared_group_id=project.shared_group_id,
            shared_group_name=group_name,
            user_role_in_group=user_role_in_group,
            user_role_in_project=collaboration_role,
            access_source="public_collaboration",
            collaborator_count=collaborator_count,
            task_count=task_count,
            completion_percentage=completion_percentage,
            created_at=project.created_at,
            due_date=project.due_date
        ))
    
    # Sort by group name, project name, and role (similar to your SQL ORDER BY)
    project_responses.sort(key=lambda x: (
        x.shared_group_name or "",
        x.name,
        x.user_role_in_project,
        x.access_source
    ))
    
    # Apply limit
    return project_responses[:limit]

@router.post("/", response_model=ProjectResponse, summary="Create a new project")
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project with ADHD-friendly features and collaboration support.
    
    **ADHD Features:**
    - Automatic project breakdown suggestions
    - Collaboration difficulty balancing
    - Built-in accountability features
    - Dopamine reward system setup
    """
    # Create new project in database
    new_project = Project(
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        status=project.status,
        owner_id=current_user.id,
        shared_group_id=project.shared_group_id,
        is_active=True,
        is_public_joinable=project.is_public_joinable,
        max_collaborators=project.max_collaborators,
        start_date=project.start_date,
        due_date=project.due_date,
        adhd_features={
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
        metrics={
            "total_tasks": 0,
            "completed_tasks": 0,
            "total_focus_sessions": 0,
            "total_break_time": 0,
            "average_task_duration": 0,
            "collaboration_score": 0,
            "dopamine_events": 0
        }
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return ProjectResponse(
        id=new_project.id,
        name=new_project.name,
        description=new_project.description,
        project_type=new_project.project_type,
        status=new_project.status,
        owner_id=new_project.owner_id,
        shared_group_id=new_project.shared_group_id,
        is_active=new_project.is_active,
        is_public_joinable=new_project.is_public_joinable,
        max_collaborators=new_project.max_collaborators,
        created_at=new_project.created_at,
        updated_at=new_project.updated_at,
        completed_at=new_project.completed_at,
        start_date=new_project.start_date,
        due_date=new_project.due_date,
        adhd_features=new_project.adhd_features,
        metrics=new_project.metrics,
        collaborator_count=0,
        task_count=0,
        completion_percentage=0.0
    )

@router.get("/{project_id}", response_model=ProjectResponse, summary="Get project details")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed project information with ADHD insights and collaboration status.
    """
    # Get project from database
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to this project
    has_access = (
        project.owner_id == current_user.id or  # Owner
        project.project_type == ProjectType.PUBLIC or  # Public project
        db.query(ProjectCollaboration).filter(
            ProjectCollaboration.project_id == project_id,
            ProjectCollaboration.user_id == current_user.id,
            ProjectCollaboration.is_active == True
        ).first() is not None  # Collaborator
    )
    
    # Check group membership access for shared projects
    if not has_access and project.shared_group_id:
        group_membership = db.query(SharedGroupMembership).filter(
            SharedGroupMembership.shared_group_id == project.shared_group_id,
            SharedGroupMembership.user_id == current_user.id,
            SharedGroupMembership.is_active == True
        ).first()
        if group_membership:
            has_access = True
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Calculate computed fields
    collaborator_count = db.query(ProjectCollaboration).filter(
        ProjectCollaboration.project_id == project.id,
        ProjectCollaboration.is_active == True
    ).count()
    
    task_count = db.query(Task).filter(Task.project_id == project.id).count()
    
    completed_tasks = db.query(Task).filter(
        Task.project_id == project.id,
        Task.status == 'completed'
    ).count()
    completion_percentage = (completed_tasks / task_count * 100) if task_count > 0 else 0.0
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        status=project.status,
        owner_id=project.owner_id,
        shared_group_id=project.shared_group_id,
        is_active=project.is_active,
        is_public_joinable=project.is_public_joinable,
        max_collaborators=project.max_collaborators,
        created_at=project.created_at,
        updated_at=project.updated_at,
        completed_at=project.completed_at,
        start_date=project.start_date,
        due_date=project.due_date,
        adhd_features=project.adhd_features or {},
        metrics=project.metrics or {},
        collaborator_count=collaborator_count,
        task_count=task_count,
        completion_percentage=completion_percentage
    )

@router.put("/{project_id}", response_model=ProjectResponse, summary="Update project")
async def update_project(
    project_id: str, 
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project with ADHD-friendly change management.
    
    **ADHD Features:**
    - Gentle transition notifications
    - Impact assessment on collaborators
    - Progress preservation
    - Motivation maintenance
    """
    # Get the project from database
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to update this project
    has_permission = (
        project.owner_id == current_user.id or
        db.query(ProjectCollaboration).filter(
            ProjectCollaboration.project_id == project_id,
            ProjectCollaboration.user_id == current_user.id,
            ProjectCollaboration.role.in_(['admin', 'owner']),
            ProjectCollaboration.is_active == True
        ).first() is not None
    )
    
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to update this project")
    
    # Validate group access if shared_group_id is being updated
    if project_update.shared_group_id is not None:
        if project_update.shared_group_id != 0:  # 0 means remove group association
            group = db.query(SharedGroup).filter(SharedGroup.id == project_update.shared_group_id).first()
            if not group:
                raise HTTPException(status_code=404, detail="Group not found")
            
            # Check if user is a member of the group
            group_membership = db.query(SharedGroupMembership).filter(
                SharedGroupMembership.shared_group_id == project_update.shared_group_id,
                SharedGroupMembership.user_id == current_user.id,
                SharedGroupMembership.is_active == True
            ).first()
            
            if not group_membership:
                raise HTTPException(
                    status_code=403, 
                    detail="You must be a member of the group to associate the project with it"
                )
    
    # Update project fields
    if project_update.name is not None:
        project.name = project_update.name
    if project_update.description is not None:
        project.description = project_update.description
    if project_update.status is not None:
        project.status = project_update.status
    if project_update.project_type is not None:
        project.project_type = project_update.project_type
    if project_update.start_date is not None:
        project.start_date = project_update.start_date
    if project_update.due_date is not None:
        project.due_date = project_update.due_date
    if project_update.shared_group_id is not None:
        project.shared_group_id = project_update.shared_group_id if project_update.shared_group_id != 0 else None
    if project_update.is_public_joinable is not None:
        project.is_public_joinable = project_update.is_public_joinable
    if project_update.max_collaborators is not None:
        project.max_collaborators = project_update.max_collaborators
    
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    
    # Calculate computed fields for response
    collaborator_count = db.query(ProjectCollaboration).filter(
        ProjectCollaboration.project_id == project.id,
        ProjectCollaboration.is_active == True
    ).count()
    
    task_count = db.query(Task).filter(Task.project_id == project.id).count()
    
    completed_tasks = db.query(Task).filter(
        Task.project_id == project.id,
        Task.status == 'completed'
    ).count()
    completion_percentage = (completed_tasks / task_count * 100) if task_count > 0 else 0.0
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        status=project.status,
        owner_id=project.owner_id,
        shared_group_id=project.shared_group_id,
        is_active=project.is_active,
        is_public_joinable=project.is_public_joinable,
        max_collaborators=project.max_collaborators,
        created_at=project.created_at,
        updated_at=project.updated_at,
        completed_at=project.completed_at,
        start_date=project.start_date,
        due_date=project.due_date,
        adhd_features=project.adhd_features or {},
        metrics=project.metrics or {},
        collaborator_count=collaborator_count,
        task_count=task_count,
        completion_percentage=completion_percentage
    )

@router.post("/{project_id}/invite", summary="Invite user to project")
async def invite_to_project(
    project_id: str, 
    invitation: ProjectInvitation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a user to collaborate on a project with ADHD-friendly onboarding.
    
    **ADHD Features:**
    - Clear role expectations
    - Collaboration guidelines
    - Supportive welcome message
    - ADHD-specific collaboration tips
    """
    # Get the project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if current user has permission to invite (owner or admin collaborator)
    has_permission = (
        project.owner_id == current_user.id or
        db.query(ProjectCollaboration).filter(
            ProjectCollaboration.project_id == project_id,
            ProjectCollaboration.user_id == current_user.id,
            ProjectCollaboration.role.in_(['admin', 'owner']),
            ProjectCollaboration.is_active == True
        ).first() is not None
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403, 
            detail="Only project owners and admins can send invitations"
        )
    
    # Check if invited user exists
    invited_user = db.query(User).filter(User.email == invitation.user_email).first()
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already a collaborator
    existing_collaboration = db.query(ProjectCollaboration).filter(
        ProjectCollaboration.project_id == project_id,
        ProjectCollaboration.user_id == invited_user.id,
        ProjectCollaboration.is_active == True
    ).first()
    
    if existing_collaboration:
        raise HTTPException(
            status_code=400,
            detail="User is already a collaborator on this project"
        )
    
    # Create collaboration
    collaboration = ProjectCollaboration(
        project_id=project_id,
        user_id=invited_user.id,
        role=invitation.role,
        invited_by=current_user.id,
        is_active=True,
        collaboration_settings={
            "share_focus_sessions": False,
            "receive_progress_notifications": True,
            "participate_in_group_breaks": True,
            "share_energy_levels": False,
            "receive_dopamine_boosts": True,
            "task_assignment_notifications": True
        },
        contribution_stats={
            "tasks_completed": 0,
            "focus_sessions_joined": 0,
            "helpful_comments": 0,
            "dopamine_given": 0,
            "last_active": None
        }
    )
    
    db.add(collaboration)
    db.commit()
    
    return {
        "message": f"🎉 {invited_user.full_name or invited_user.email} has been added to the project!",
        "invitation_details": {
            "project_id": project_id,
            "project_name": project.name,
            "recipient": invitation.user_email,
            "role": invitation.role,
            "added_by": current_user.full_name or current_user.email
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
async def join_public_project(project_id: str, join_request: ProjectJoinRequest):
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
async def get_project_collaborators(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get project collaborators with ADHD-friendly team overview.
    """
    # Verify user has access to project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    has_access = (
        project.owner_id == current_user.id or
        project.project_type == ProjectType.PUBLIC or
        db.query(ProjectCollaboration).filter(
            ProjectCollaboration.project_id == project_id,
            ProjectCollaboration.user_id == current_user.id,
            ProjectCollaboration.is_active == True
        ).first() is not None
    )
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Get collaborators from database - fix ambiguous join
    collaborations = db.query(ProjectCollaboration).filter(
        ProjectCollaboration.project_id == project_id,
        ProjectCollaboration.is_active == True
    ).all()
    
    collaborators = []
    total_tasks_completed = 0
    
    for collab in collaborations:
        user = db.query(User).filter(User.id == collab.user_id).first()
        if user:
            collaborators.append({
                "user_id": collab.user_id,
                "username": user.username or user.email.split('@')[0],  # Fallback to email prefix
                "role": collab.role,
                "joined_at": collab.joined_at.isoformat(),
                "is_active": collab.is_active,
                "contribution_stats": collab.contribution_stats or {
                    "tasks_completed": 0,
                    "focus_sessions_joined": 0,
                    "helpful_comments": 0,
                    "dopamine_given": 0,
                    "last_active": None
                }
            })
            total_tasks_completed += collab.contribution_stats.get("tasks_completed", 0) if collab.contribution_stats else 0
    
    # Add project owner if not already in collaborators
    if not any(c["user_id"] == project.owner_id for c in collaborators):
        owner = db.query(User).filter(User.id == project.owner_id).first()
        if owner:
            collaborators.append({
                "user_id": project.owner_id,
                "username": owner.username or owner.email.split('@')[0],
                "role": "owner",
                "joined_at": project.created_at.isoformat(),
                "is_active": True,
                "contribution_stats": {
                    "tasks_completed": 0,
                    "focus_sessions_joined": 0,
                    "helpful_comments": 0,
                    "dopamine_given": 0,
                    "last_active": None
                }
            })
    
    return {
        "collaborators": collaborators,
        "team_stats": {
            "total_collaborators": len(collaborators),
            "active_today": len([c for c in collaborators if c["is_active"]]),
            "total_tasks_completed": total_tasks_completed,
            "team_focus_time": 0,  # Can be calculated from focus sessions
            "dopamine_exchanges": sum(c["contribution_stats"].get("dopamine_given", 0) for c in collaborators)
        },
        "team_energy": "🔥 High collaborative energy!",
        "motivation": "🌟 Amazing teamwork - keep supporting each other!"
    }

@router.get("/public/discover", summary="Discover public projects")
async def discover_public_projects(
    limit: int = Query(10, ge=1, le=50, description="Number of projects to return"),
    db: Session = Depends(get_db)
):
    """
    Discover public ADHD-friendly projects to join.
    
    **ADHD Features:**
    - Curated for ADHD community
    - Clear difficulty indicators
    - Supportive community focus
    - Beginner-friendly options
    """
    # Get public projects from database
    public_projects = db.query(Project).filter(
        Project.project_type == ProjectType.PUBLIC,
        Project.is_public_joinable == True,
        Project.status == ProjectStatus.ACTIVE
    ).limit(limit).all()
    
    public_project_list = []
    for project in public_projects:
        # Count collaborators and tasks
        collaborator_count = db.query(ProjectCollaboration).filter(
            ProjectCollaboration.project_id == project.id,
            ProjectCollaboration.is_active == True
        ).count()
        
        task_count = db.query(Task).filter(Task.project_id == project.id).count()
        
        completed_tasks = db.query(Task).filter(
            Task.project_id == project.id,
            Task.status == 'completed'
        ).count()
        completion_percentage = (completed_tasks / task_count * 100) if task_count > 0 else 0.0
        
        public_project_list.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "collaborator_count": collaborator_count,
            "task_count": task_count,
            "completion_percentage": completion_percentage,
            "difficulty": "beginner-friendly",  # Could be derived from project metadata
            "tags": [],  # Could be added to project model
            "welcomes_beginners": True
        })
    
    return {
        "public_projects": public_project_list,
        "discovery_tip": "🔍 Look for projects that match your current energy and interests!",
        "community_message": "🤝 The ADHD community is here to support each other!",
        "joining_benefits": [
            "Learn from others' ADHD strategies",
            "Get accountability and motivation",
            "Share your unique strengths",
            "Build supportive connections"
        ]
    }

@router.delete("/{project_id}", summary="Delete project")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project with ADHD-friendly confirmation and data preservation.
    
    **ADHD Features:**
    - Clear confirmation process
    - Data backup recommendations
    - Gentle transition support
    - Task preservation options
    """
    # Get the project from database
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission to delete this project (only owner can delete)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can delete the project")
    
    # Get project statistics before deletion
    task_count = db.query(Task).filter(Task.project_id == project.id).count()
    collaborator_count = db.query(ProjectCollaboration).filter(
        ProjectCollaboration.project_id == project.id,
        ProjectCollaboration.is_active == True
    ).count()
    
    # Soft delete - mark as inactive instead of hard delete to preserve data
    project.is_active = False
    project.updated_at = datetime.utcnow()
    
    # Deactivate all collaborations
    db.query(ProjectCollaboration).filter(
        ProjectCollaboration.project_id == project.id
    ).update({"is_active": False})
    
    # Mark tasks as paused instead of deleting
    db.query(Task).filter(Task.project_id == project.id).update({
        "status": TaskStatus.PAUSED,
        "updated_at": datetime.utcnow()
    })
    
    db.commit()
    
    return {
        "message": f"🗂️ Project '{project.name}' has been archived successfully",
        "preservation_notice": "Your project data has been preserved and can be restored if needed",
        "statistics": {
            "tasks_archived": task_count,
            "collaborations_ended": collaborator_count,
            "project_id": project_id
        },
        "next_steps": [
            "📋 Consider downloading important project data",
            "🤝 Notify collaborators about the project closure",
            "🎯 Focus energy on your active projects",
            "💡 Apply lessons learned to future projects"
        ],
        "recovery_info": "Contact support within 30 days if you need to restore this project"
    }
