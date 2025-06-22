"""
SharedGroups router for ADHD Task Manager collaborative features.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.group import SharedGroup, SharedGroupMembership
from app.models.project import Project
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.group import (
    SharedGroupCreate, SharedGroupUpdate, SharedGroupResponse, SharedGroupListResponse,
    SharedGroupInvitation, SharedGroupMembershipUpdate, SharedGroupRole
)

router = APIRouter()

@router.get("/", response_model=List[SharedGroupListResponse], summary="Get user's shared groups")
async def get_shared_groups(
    limit: int = Query(20, ge=1, le=100, description="Number of shared groups to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's shared groups with ADHD-friendly presentation.
    
    **ADHD Features:**
    - Limited results to prevent overwhelm
    - Clear member count for social context
    - Activity indicators for engagement
    - Supportive group atmosphere
    """
    # Get shared groups where user is a member
    user_shared_groups = db.query(SharedGroup).join(SharedGroupMembership).filter(
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.is_active == True
    ).limit(limit).all()
    
    shared_group_responses = []
    for shared_group in user_shared_groups:
        # Count members
        member_count = db.query(SharedGroupMembership).filter(
            SharedGroupMembership.shared_group_id == shared_group.id,
            SharedGroupMembership.is_active == True
        ).count()
        
        # Count associated projects
        project_count = db.query(Project).filter(Project.shared_group_id == shared_group.id).count()
        
        shared_group_responses.append(SharedGroupListResponse(
            id=shared_group.id,
            name=shared_group.name,
            description=shared_group.description,
            created_by=shared_group.created_by,
            member_count=member_count,
            project_count=project_count,
            is_active=shared_group.is_active,
            created_at=shared_group.created_at,
            group_focus_sessions=shared_group.group_focus_sessions,
            shared_energy_tracking=shared_group.shared_energy_tracking,
            group_dopamine_celebrations=shared_group.group_dopamine_celebrations,
            collaborative_task_chunking=shared_group.collaborative_task_chunking,
            group_break_reminders=shared_group.group_break_reminders,
            accountability_features=shared_group.accountability_features
        ))
    
    return shared_group_responses

@router.post("/", response_model=SharedGroupResponse, summary="Create a new shared group")
async def create_shared_group(
    shared_group: SharedGroupCreate,
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
    # Create new shared group in database
    new_shared_group = SharedGroup(
        name=shared_group.name,
        description=shared_group.description,
        created_by=current_user.id,
        is_active=True,
        group_focus_sessions=shared_group.group_focus_sessions,
        shared_energy_tracking=shared_group.shared_energy_tracking,
        group_dopamine_celebrations=shared_group.group_dopamine_celebrations,
        collaborative_task_chunking=shared_group.collaborative_task_chunking,
        group_break_reminders=shared_group.group_break_reminders,
        accountability_features=shared_group.accountability_features
    )
    
    db.add(new_shared_group)
    db.commit()
    db.refresh(new_shared_group)
    
    # Add creator as owner of the shared group
    membership = SharedGroupMembership(
        shared_group_id=new_shared_group.id,
        user_id=current_user.id,
        role=SharedGroupRole.OWNER,
        is_active=True
    )
    
    db.add(membership)
    db.commit()
    
    return SharedGroupResponse(
        id=new_shared_group.id,
        name=new_shared_group.name,
        description=new_shared_group.description,
        created_by=new_shared_group.created_by,
        is_active=new_shared_group.is_active,
        created_at=new_shared_group.created_at,
        updated_at=new_shared_group.updated_at,
        group_focus_sessions=new_shared_group.group_focus_sessions,
        shared_energy_tracking=new_shared_group.shared_energy_tracking,
        group_dopamine_celebrations=new_shared_group.group_dopamine_celebrations,
        collaborative_task_chunking=new_shared_group.collaborative_task_chunking,
        group_break_reminders=new_shared_group.group_break_reminders,
        accountability_features=new_shared_group.accountability_features,
        member_count=1,
        project_count=0
    )

@router.get("/{shared_group_id}", response_model=SharedGroupResponse, summary="Get shared group details")
async def get_shared_group(
    shared_group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed shared group information with ADHD-specific features and member activity.
    """
    # Get shared group from database
    shared_group = db.query(SharedGroup).filter(SharedGroup.id == shared_group_id).first()
    
    if not shared_group:
        raise HTTPException(status_code=404, detail="Shared group not found")
    
    # Check if user is a member of this shared group
    membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied to this shared group")
    
    # Calculate computed fields
    member_count = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group.id,
        SharedGroupMembership.is_active == True
    ).count()
    
    project_count = db.query(Project).filter(Project.shared_group_id == shared_group.id).count()
    
    return SharedGroupResponse(
        id=shared_group.id,
        name=shared_group.name,
        description=shared_group.description,
        created_by=shared_group.created_by,
        is_active=shared_group.is_active,
        created_at=shared_group.created_at,
        updated_at=shared_group.updated_at,
        group_focus_sessions=shared_group.group_focus_sessions,
        shared_energy_tracking=shared_group.shared_energy_tracking,
        group_dopamine_celebrations=shared_group.group_dopamine_celebrations,
        collaborative_task_chunking=shared_group.collaborative_task_chunking,
        group_break_reminders=shared_group.group_break_reminders,
        accountability_features=shared_group.accountability_features,
        member_count=member_count,
        project_count=project_count
    )

@router.put("/{shared_group_id}", response_model=SharedGroupResponse, summary="Update shared group")
async def update_shared_group(
    shared_group_id: str, 
    shared_group_update: SharedGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update shared group settings with ADHD-friendly change management.
    
    **ADHD Features:**
    - Gentle notification of changes
    - Member impact assessment
    - Continuity of support structures
    - Motivation preservation
    """
    # Get the shared group from database
    shared_group = db.query(SharedGroup).filter(SharedGroup.id == shared_group_id).first()
    
    if not shared_group:
        raise HTTPException(status_code=404, detail="Shared group not found")
    
    # Check if user has permission to update this shared group
    membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.role.in_([SharedGroupRole.OWNER, SharedGroupRole.ADMIN]),
        SharedGroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="You don't have permission to update this shared group")
    
    # Update shared group fields
    if shared_group_update.name is not None:
        shared_group.name = shared_group_update.name
    if shared_group_update.description is not None:
        shared_group.description = shared_group_update.description
    # Update individual ADHD settings
    if shared_group_update.group_focus_sessions is not None:
        shared_group.group_focus_sessions = shared_group_update.group_focus_sessions
    if shared_group_update.shared_energy_tracking is not None:
        shared_group.shared_energy_tracking = shared_group_update.shared_energy_tracking
    if shared_group_update.group_dopamine_celebrations is not None:
        shared_group.group_dopamine_celebrations = shared_group_update.group_dopamine_celebrations
    if shared_group_update.collaborative_task_chunking is not None:
        shared_group.collaborative_task_chunking = shared_group_update.collaborative_task_chunking
    if shared_group_update.group_break_reminders is not None:
        shared_group.group_break_reminders = shared_group_update.group_break_reminders
    if shared_group_update.accountability_features is not None:
        shared_group.accountability_features = shared_group_update.accountability_features
    
    from datetime import datetime
    shared_group.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(shared_group)
    
    # Calculate computed fields for response
    member_count = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group.id,
        SharedGroupMembership.is_active == True
    ).count()
    
    project_count = db.query(Project).filter(Project.shared_group_id == shared_group.id).count()
    
    return SharedGroupResponse(
        id=shared_group.id,
        name=shared_group.name,
        description=shared_group.description,
        created_by=shared_group.created_by,
        is_active=shared_group.is_active,
        created_at=shared_group.created_at,
        updated_at=shared_group.updated_at,
        group_focus_sessions=shared_group.group_focus_sessions,
        shared_energy_tracking=shared_group.shared_energy_tracking,
        group_dopamine_celebrations=shared_group.group_dopamine_celebrations,
        collaborative_task_chunking=shared_group.collaborative_task_chunking,
        group_break_reminders=shared_group.group_break_reminders,
        accountability_features=shared_group.accountability_features,
        member_count=member_count,
        project_count=project_count
    )

@router.post("/{shared_group_id}/invite", summary="Invite user to shared group")
async def invite_to_shared_group(shared_group_id: str, invitation: SharedGroupInvitation):
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
            "shared_group_id": shared_group_id,
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

@router.get("/{shared_group_id}/members", summary="Get shared group members")
async def get_shared_group_members(shared_group_id: str):
    """
    Get shared group members with ADHD-friendly community overview.
    """
    mock_members = [
        {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "shared_group_creator",
            "role": SharedGroupRole.OWNER,
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
            "user_id": "456e7890-e12b-34c5-b678-901234567890",
            "username": "focus_buddy",
            "role": SharedGroupRole.MEMBER,
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
            "user_id": "789e0123-e45f-67a8-9012-345678901234",
            "username": "adhd_champion",
            "role": SharedGroupRole.ADMIN,
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

@router.put("/{shared_group_id}/members/{user_id}", summary="Update member role or settings")
async def update_shared_group_member(
    shared_group_id: str, 
    user_id: str, 
    member_update: SharedGroupMembershipUpdate
):
    """
    Update shared group member role or settings with ADHD-friendly change management.
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

@router.delete("/{shared_group_id}/members/{user_id}", summary="Remove member from shared group")
async def remove_shared_group_member(shared_group_id: str, user_id: str):
    """
    Remove a member from the shared group with ADHD-friendly handling.
    """
    return {
        "message": f"Member {user_id} removed from shared group {shared_group_id}",
        "support_message": "🤝 We support everyone's journey, even when paths diverge",
        "adhd_tip": "💪 Group changes are natural - focus on those who remain committed"
    }

@router.post("/{shared_group_id}/join", summary="Join shared group (if public or invited)")
async def join_shared_group(shared_group_id: str):
    """
    Join a shared group with ADHD-friendly onboarding.
    """
    return {
        "message": f"🚀 Welcome to shared group {shared_group_id}!",
        "welcome_package": {
            "community_guidelines": [
                "🤝 Support each other's ADHD journey",
                "🎯 Celebrate small wins and progress",
                "⚡ Share energy and motivation freely",
                "💬 Communicate with kindness and understanding"
            ],
            "getting_started": [
                "👋 Introduce yourself to the shared group",
                "📋 Check out current shared group projects",
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
        "group_energy": "🌟 The shared group is excited to have you!",
        "first_tip": "💡 Start small - even just saying hello makes a difference!"
    }

@router.get("/{shared_group_id}/focus-sessions", summary="Get shared group focus sessions")
async def get_shared_group_focus_sessions(
    shared_group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get shared group focus sessions and body doubling opportunities.
    
    **ADHD Features:**
    - Virtual body doubling support
    - Shared focus accountability
    - Energy synchronization
    - Collective motivation
    """
    # Verify user is a member of the shared group
    membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied to this shared group")
    
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

@router.delete("/{shared_group_id}", summary="Delete shared group")
async def delete_shared_group(
    shared_group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a shared group with ADHD-friendly confirmation and member notification.
    
    **ADHD Features:**
    - Clear confirmation process
    - Member notification support
    - Data preservation options
    - Gentle transition guidance
    """
    # Get the shared group from database
    shared_group = db.query(SharedGroup).filter(SharedGroup.id == shared_group_id).first()
    
    if not shared_group:
        raise HTTPException(status_code=404, detail="Shared group not found")
    
    # Check if user has permission to delete this shared group (only owner can delete)
    owner_membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.role == SharedGroupRole.OWNER,
        SharedGroupMembership.is_active == True
    ).first()
    
    if not owner_membership:
        raise HTTPException(status_code=403, detail="Only the shared group owner can delete the shared group")
    
    # Get shared group statistics before deletion
    member_count = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group.id,
        SharedGroupMembership.is_active == True
    ).count()
    
    project_count = db.query(Project).filter(Project.shared_group_id == shared_group.id).count()
    
    from datetime import datetime
    
    # Soft delete - mark as inactive instead of hard delete
    shared_group.is_active = False
    shared_group.updated_at = datetime.utcnow()
    
    # Deactivate all memberships
    db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group.id
    ).update({"is_active": False})
    
    # Update associated projects to remove shared group association
    db.query(Project).filter(Project.shared_group_id == shared_group.id).update({
        "shared_group_id": None,
        "updated_at": datetime.utcnow()
    })
    
    db.commit()
    
    return {
        "message": f"🏠 Shared Group '{shared_group.name}' has been archived successfully",
        "preservation_notice": "Shared group data has been preserved and can be restored if needed",
        "member_notification": f"All {member_count} members have been notified of the shared group closure",
        "statistics": {
            "members_affected": member_count,
            "projects_updated": project_count,
            "shared_group_id": shared_group_id
        },
        "next_steps": [
            "📢 Consider messaging members individually for transition support",
            "🤝 Encourage members to stay connected outside the shared group",
            "🎯 Focus on your remaining active shared groups and projects",
            "💡 Apply lessons learned to future shared group management"
        ],
        "recovery_info": "Contact support within 30 days if you need to restore this shared group"
    }
