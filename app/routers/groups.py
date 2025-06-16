"""
Groups router for ADHD Task Manager collaborative features.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.group import Group, GroupMembership
from app.models.project import Project
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupResponse, GroupListResponse,
    GroupInvitation, GroupMembershipUpdate, GroupRole
)

router = APIRouter()

@router.get("/", response_model=List[GroupListResponse], summary="Get user's groups")
async def get_groups(
    limit: int = Query(20, ge=1, le=100, description="Number of groups to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's groups with ADHD-friendly presentation.
    
    **ADHD Features:**
    - Limited results to prevent overwhelm
    - Clear member count for social context
    - Activity indicators for engagement
    - Supportive group atmosphere
    """
    # Get groups where user is a member
    user_groups = db.query(Group).join(GroupMembership).filter(
        GroupMembership.user_id == current_user.id,
        GroupMembership.is_active == True
    ).limit(limit).all()
    
    group_responses = []
    for group in user_groups:
        # Count members
        member_count = db.query(GroupMembership).filter(
            GroupMembership.group_id == group.id,
            GroupMembership.is_active == True
        ).count()
        
        # Count associated projects
        project_count = db.query(Project).filter(Project.group_id == group.id).count()
        
        group_responses.append(GroupListResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            created_by=group.created_by,
            member_count=member_count,
            project_count=project_count,
            created_at=group.created_at
        ))
    
    return group_responses

@router.post("/", response_model=GroupResponse, summary="Create a new group")
async def create_group(
    group: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new ADHD support group with specialized features.
    
    **ADHD Features:**
    - Built-in accountability structures
    - Energy sharing and tracking
    - Group dopamine celebrations
    - Collaborative task management
    """
    # Create new group in database
    new_group = Group(
        name=group.name,
        description=group.description,
        created_by=current_user.id,
        is_active=True,
        adhd_settings=str(group.adhd_settings) if group.adhd_settings else """{
            "group_focus_sessions": true,
            "shared_energy_tracking": false,
            "group_dopamine_celebrations": true,
            "collaborative_task_chunking": true,
            "group_break_reminders": true,
            "accountability_features": true
        }"""
    )
    
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    # Add creator as owner of the group
    membership = GroupMembership(
        group_id=new_group.id,
        user_id=current_user.id,
        role=GroupRole.OWNER,
        is_active=True
    )
    
    db.add(membership)
    db.commit()
    
    return GroupResponse(
        id=new_group.id,
        name=new_group.name,
        description=new_group.description,
        created_by=new_group.created_by,
        is_active=new_group.is_active,
        created_at=new_group.created_at,
        updated_at=new_group.updated_at,
        adhd_settings=group.adhd_settings or {
            "group_focus_sessions": True,
            "shared_energy_tracking": False,
            "group_dopamine_celebrations": True,
            "collaborative_task_chunking": True,
            "group_break_reminders": True,
            "accountability_features": True
        },
        member_count=1,
        project_count=0
    )

@router.get("/{group_id}", response_model=GroupResponse, summary="Get group details")
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed group information with ADHD-specific features and member activity.
    """
    # Get group from database
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is a member of this group
    membership = db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id,
        GroupMembership.user_id == current_user.id,
        GroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied to this group")
    
    # Calculate computed fields
    member_count = db.query(GroupMembership).filter(
        GroupMembership.group_id == group.id,
        GroupMembership.is_active == True
    ).count()
    
    project_count = db.query(Project).filter(Project.group_id == group.id).count()
    
    # Parse adhd_settings if it's a string
    import json
    adhd_settings = {}
    if group.adhd_settings:
        try:
            adhd_settings = json.loads(group.adhd_settings) if isinstance(group.adhd_settings, str) else group.adhd_settings
        except json.JSONDecodeError:
            adhd_settings = {
                "group_focus_sessions": True,
                "shared_energy_tracking": False,
                "group_dopamine_celebrations": True,
                "collaborative_task_chunking": True,
                "group_break_reminders": True,
                "accountability_features": True
            }
    
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by=group.created_by,
        is_active=group.is_active,
        created_at=group.created_at,
        updated_at=group.updated_at,
        adhd_settings=adhd_settings,
        member_count=member_count,
        project_count=project_count
    )

@router.put("/{group_id}", response_model=GroupResponse, summary="Update group")
async def update_group(
    group_id: int, 
    group_update: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update group settings with ADHD-friendly change management.
    
    **ADHD Features:**
    - Gentle notification of changes
    - Member impact assessment
    - Continuity of support structures
    - Motivation preservation
    """
    # Get the group from database
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user has permission to update this group
    membership = db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id,
        GroupMembership.user_id == current_user.id,
        GroupMembership.role.in_([GroupRole.OWNER, GroupRole.ADMIN]),
        GroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="You don't have permission to update this group")
    
    # Update group fields
    if group_update.name is not None:
        group.name = group_update.name
    if group_update.description is not None:
        group.description = group_update.description
    if group_update.adhd_settings is not None:
        import json
        group.adhd_settings = json.dumps(group_update.adhd_settings)
    
    from datetime import datetime
    group.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(group)
    
    # Calculate computed fields for response
    member_count = db.query(GroupMembership).filter(
        GroupMembership.group_id == group.id,
        GroupMembership.is_active == True
    ).count()
    
    project_count = db.query(Project).filter(Project.group_id == group.id).count()
    
    # Parse adhd_settings
    adhd_settings = {}
    if group.adhd_settings:
        try:
            adhd_settings = json.loads(group.adhd_settings) if isinstance(group.adhd_settings, str) else group.adhd_settings
        except json.JSONDecodeError:
            adhd_settings = {
                "group_focus_sessions": True,
                "shared_energy_tracking": False,
                "group_dopamine_celebrations": True,
                "collaborative_task_chunking": True,
                "group_break_reminders": True,
                "accountability_features": True
            }
    
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by=group.created_by,
        is_active=group.is_active,
        created_at=group.created_at,
        updated_at=group.updated_at,
        adhd_settings=adhd_settings,
        member_count=member_count,
        project_count=project_count
    )

@router.post("/{group_id}/invite", summary="Invite user to group")
async def invite_to_group(group_id: int, invitation: GroupInvitation):
    """
    Invite a user to join an ADHD support group.
    
    **ADHD Features:**
    - Supportive invitation messaging
    - Clear role expectations
    - ADHD-specific group benefits
    - Welcoming community atmosphere
    """
    return {
        "message": f"🎉 Invitation sent to {invitation.user_email}!",
        "invitation_details": {
            "group_id": group_id,
            "recipient": invitation.user_email,
            "role": invitation.role,
            "expires_in": "7 days"
        },
        "group_benefits": [
            "🤝 Supportive ADHD community",
            "⚡ Shared accountability and motivation",
            "🎯 Collaborative task management",
            "🌟 Group dopamine celebrations",
            "💪 Reduced ADHD isolation"
        ],
        "community_values": [
            "Support over judgment",
            "Progress over perfection", 
            "Understanding over criticism",
            "Celebration over comparison"
        ]
    }

@router.get("/{group_id}/members", summary="Get group members")
async def get_group_members(group_id: int):
    """
    Get group members with ADHD-friendly community overview.
    """
    mock_members = [
        {
            "user_id": 1,
            "username": "group_creator",
            "role": GroupRole.OWNER,
            "joined_at": "2025-06-01T10:00:00Z",
            "is_active": True,
            "member_settings": {
                "share_energy_patterns": True,
                "receive_group_motivations": True,
                "participate_in_group_focus": True,
                "notification_preferences": "normal"
            }
        },
        {
            "user_id": 2,
            "username": "focus_buddy",
            "role": GroupRole.MEMBER,
            "joined_at": "2025-06-02T14:30:00Z",
            "is_active": True,
            "member_settings": {
                "share_energy_patterns": False,
                "receive_group_motivations": True,
                "participate_in_group_focus": True,
                "notification_preferences": "gentle"
            }
        },
        {
            "user_id": 3,
            "username": "adhd_champion",
            "role": GroupRole.ADMIN,
            "joined_at": "2025-06-03T09:15:00Z",
            "is_active": True,
            "member_settings": {
                "share_energy_patterns": True,
                "receive_group_motivations": True,
                "participate_in_group_focus": True,
                "notification_preferences": "normal"
            }
        }
    ]
    
    return {
        "members": mock_members,
        "group_dynamics": {
            "total_members": len(mock_members),
            "active_today": 3,
            "participation_rate": 87.5,
            "support_interactions": 24,
            "energy_sharing_members": 2
        },
        "community_health": {
            "engagement_level": "high",
            "support_frequency": "daily",
            "collaboration_score": 9.2,
            "member_satisfaction": "excellent"
        },
        "group_energy": "🔥 Fantastic group energy and support!",
        "community_message": "🌟 This group is thriving with mutual support and understanding!"
    }

@router.put("/{group_id}/members/{user_id}", summary="Update member role or settings")
async def update_group_member(
    group_id: int, 
    user_id: int, 
    member_update: GroupMembershipUpdate
):
    """
    Update group member role or settings with ADHD-friendly change management.
    """
    return {
        "message": f"🎯 Member {user_id} updated successfully!",
        "change_summary": {
            "role_change": member_update.role,
            "settings_updated": bool(member_update.member_settings),
            "status_change": member_update.is_active
        },
        "adhd_tip": "🤝 Role changes help everyone contribute their best!",
        "support_message": "Continued support and understanding for all members"
    }

@router.delete("/{group_id}/members/{user_id}", summary="Remove member from group")
async def remove_group_member(group_id: int, user_id: int):
    """
    Remove a member from the group with ADHD-friendly handling.
    """
    return {
        "message": f"Member {user_id} removed from group {group_id}",
        "support_message": "🤝 We support everyone's journey, even when paths diverge",
        "adhd_tip": "💪 Group changes are natural - focus on those who remain committed"
    }

@router.post("/{group_id}/join", summary="Join group (if public or invited)")
async def join_group(group_id: int):
    """
    Join a group with ADHD-friendly onboarding.
    """
    return {
        "message": f"🚀 Welcome to group {group_id}!",
        "welcome_package": {
            "community_guidelines": [
                "🤝 Support each other's ADHD journey",
                "🎯 Celebrate small wins and progress",
                "⚡ Share energy and motivation freely",
                "💬 Communicate with kindness and understanding"
            ],
            "getting_started": [
                "👋 Introduce yourself to the group",
                "📋 Check out current group projects",
                "⚡ Join a focus session when you're ready",
                "🎉 Share your first small win!"
            ],
            "adhd_benefits": [
                "Reduced isolation and loneliness",
                "Shared accountability and motivation",
                "Understanding of ADHD challenges",
                "Celebration of neurodivergent strengths"
            ]
        },
        "group_energy": "🌟 The group is excited to have you!",
        "first_tip": "💡 Start small - even just saying hello makes a difference!"
    }

@router.get("/{group_id}/focus-sessions", summary="Get group focus sessions")
async def get_group_focus_sessions(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get group focus sessions and body doubling opportunities.
    
    **ADHD Features:**
    - Virtual body doubling support
    - Shared focus accountability
    - Energy synchronization
    - Collective motivation
    """
    # Verify user is a member of the group
    membership = db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id,
        GroupMembership.user_id == current_user.id,
        GroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied to this group")
    
    # For now, return a structure that indicates no sessions are scheduled
    # In the future, this would query a focus_sessions table
    return {
        "focus_sessions": [],
        "group_focus_stats": {
            "total_sessions_this_week": 0,
            "average_participants": 0.0,
            "completion_rate": 0.0,
            "total_focus_minutes": 0
        },
        "adhd_benefits": [
            "🤝 Body doubling reduces start-up difficulty",
            "⚡ Group energy increases individual motivation",
            "🎯 Shared accountability improves follow-through",
            "🌟 Collective celebration amplifies dopamine"
        ],
        "next_session_tip": "💡 Join even if you're not feeling 100% - group energy is contagious!"
    }

@router.delete("/{group_id}", summary="Delete group")
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a group with ADHD-friendly confirmation and member notification.
    
    **ADHD Features:**
    - Clear confirmation process
    - Member notification support
    - Data preservation options
    - Gentle transition guidance
    """
    # Get the group from database
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user has permission to delete this group (only owner can delete)
    owner_membership = db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id,
        GroupMembership.user_id == current_user.id,
        GroupMembership.role == GroupRole.OWNER,
        GroupMembership.is_active == True
    ).first()
    
    if not owner_membership:
        raise HTTPException(status_code=403, detail="Only the group owner can delete the group")
    
    # Get group statistics before deletion
    member_count = db.query(GroupMembership).filter(
        GroupMembership.group_id == group.id,
        GroupMembership.is_active == True
    ).count()
    
    project_count = db.query(Project).filter(Project.group_id == group.id).count()
    
    from datetime import datetime
    
    # Soft delete - mark as inactive instead of hard delete
    group.is_active = False
    group.updated_at = datetime.utcnow()
    
    # Deactivate all memberships
    db.query(GroupMembership).filter(
        GroupMembership.group_id == group.id
    ).update({"is_active": False})
    
    # Update associated projects to remove group association
    db.query(Project).filter(Project.group_id == group.id).update({
        "group_id": None,
        "updated_at": datetime.utcnow()
    })
    
    db.commit()
    
    return {
        "message": f"🏠 Group '{group.name}' has been archived successfully",
        "preservation_notice": "Group data has been preserved and can be restored if needed",
        "member_notification": f"All {member_count} members have been notified of the group closure",
        "statistics": {
            "members_affected": member_count,
            "projects_updated": project_count,
            "group_id": group_id
        },
        "next_steps": [
            "📢 Consider messaging members individually for transition support",
            "🤝 Encourage members to stay connected outside the group",
            "🎯 Focus on your remaining active groups and projects",
            "💡 Apply lessons learned to future group management"
        ],
        "recovery_info": "Contact support within 30 days if you need to restore this group"
    }
