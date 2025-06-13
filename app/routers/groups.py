"""
Groups router for ADHD Task Manager collaborative features.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupResponse, GroupListResponse,
    GroupInvitation, GroupMembershipUpdate, GroupRole
)

router = APIRouter()

@router.get("/", response_model=List[GroupListResponse], summary="Get user's groups")
async def get_groups(
    limit: int = Query(20, ge=1, le=100, description="Number of groups to return")
):
    """
    Get user's groups with ADHD-friendly presentation.
    
    **ADHD Features:**
    - Limited results to prevent overwhelm
    - Clear member count for social context
    - Activity indicators for engagement
    - Supportive group atmosphere
    """
    # Mock data for now - replace with database queries
    mock_groups = [
        {
            "id": 1,
            "name": "ADHD Support Squad",
            "description": "A supportive group for ADHD task management and accountability",
            "created_by": 1,
            "member_count": 8,
            "project_count": 3,
            "created_at": "2025-06-01T10:00:00Z"
        },
        {
            "id": 2,
            "name": "Focus Buddies",
            "description": "Virtual body doubling and focus sessions for ADHD productivity",
            "created_by": 2,
            "member_count": 12,
            "project_count": 1,
            "created_at": "2025-05-28T14:30:00Z"
        },
        {
            "id": 3,
            "name": "ADHD Workplace Warriors",
            "description": "Professional support group for ADHD individuals in the workplace",
            "created_by": 3,
            "member_count": 15,
            "project_count": 5,
            "created_at": "2025-05-25T09:00:00Z"
        }
    ]
    
    limited_groups = mock_groups[:limit]
    
    return limited_groups

@router.post("/", response_model=GroupResponse, summary="Create a new group")
async def create_group(group: GroupCreate):
    """
    Create a new ADHD support group with specialized features.
    
    **ADHD Features:**
    - Built-in accountability structures
    - Energy sharing and tracking
    - Group dopamine celebrations
    - Collaborative task management
    """
    # Mock creation - replace with database logic
    new_group = {
        "id": 4,
        "name": group.name,
        "description": group.description,
        "created_by": 1,  # Current user
        "is_active": True,
        "created_at": "2025-06-13T12:00:00Z",
        "updated_at": None,
        "adhd_settings": group.adhd_settings or {
            "group_focus_sessions": True,
            "shared_energy_tracking": False,
            "group_dopamine_celebrations": True,
            "collaborative_task_chunking": True,
            "group_break_reminders": True,
            "accountability_features": True
        },
        "member_count": 1,  # Creator is first member
        "project_count": 0
    }
    
    return new_group

@router.get("/{group_id}", response_model=GroupResponse, summary="Get group details")
async def get_group(group_id: int):
    """
    Get detailed group information with ADHD-specific features and member activity.
    """
    if group_id == 1:
        return {
            "id": 1,
            "name": "ADHD Support Squad",
            "description": "A supportive group for ADHD task management and accountability",
            "created_by": 1,
            "is_active": True,
            "created_at": "2025-06-01T10:00:00Z",
            "updated_at": "2025-06-12T15:20:00Z",
            "adhd_settings": {
                "group_focus_sessions": True,
                "shared_energy_tracking": True,
                "group_dopamine_celebrations": True,
                "collaborative_task_chunking": True,
                "group_break_reminders": True,
                "accountability_features": True
            },
            "member_count": 8,
            "project_count": 3,
            "group_activity": {
                "active_members_today": 5,
                "total_focus_sessions": 42,
                "dopamine_celebrations": 28,
                "collaborative_tasks": 15,
                "support_messages": 67
            },
            "energy_summary": {
                "group_energy_trend": "increasing",
                "peak_focus_times": ["9:00-11:00", "14:00-16:00"],
                "group_motivation_level": "high"
            }
        }
    
    raise HTTPException(status_code=404, detail="Group not found")

@router.put("/{group_id}", response_model=GroupResponse, summary="Update group")
async def update_group(group_id: int, group_update: GroupUpdate):
    """
    Update group settings with ADHD-friendly change management.
    
    **ADHD Features:**
    - Gentle notification of changes
    - Member impact assessment
    - Continuity of support structures
    - Motivation preservation
    """
    return {
        "message": f"🎯 Group {group_id} updated successfully!",
        "adhd_tip": "🔄 Adapting group settings helps everyone thrive!",
        "change_notification": "All members will be gently notified of the updates",
        "support_continuity": "Your accountability and support structures remain intact"
    }

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
async def get_group_focus_sessions(group_id: int):
    """
    Get group focus sessions and body doubling opportunities.
    
    **ADHD Features:**
    - Virtual body doubling support
    - Shared focus accountability
    - Energy synchronization
    - Collective motivation
    """
    mock_sessions = [
        {
            "id": 1,
            "title": "Morning Focus Session",
            "description": "Start the day with group accountability",
            "scheduled_time": "2025-06-14T09:00:00Z",
            "duration_minutes": 50,
            "participants": 5,
            "session_type": "body_doubling",
            "energy_level": "high",
            "status": "scheduled"
        },
        {
            "id": 2,
            "title": "Afternoon Project Work",
            "description": "Collaborative project focus time",
            "scheduled_time": "2025-06-14T14:00:00Z", 
            "duration_minutes": 25,
            "participants": 8,
            "session_type": "collaborative",
            "energy_level": "medium",
            "status": "scheduled"
        }
    ]
    
    return {
        "focus_sessions": mock_sessions,
        "group_focus_stats": {
            "total_sessions_this_week": 12,
            "average_participants": 6.5,
            "completion_rate": 89.2,
            "total_focus_minutes": 1440
        },
        "adhd_benefits": [
            "🤝 Body doubling reduces start-up difficulty",
            "⚡ Group energy increases individual motivation",
            "🎯 Shared accountability improves follow-through",
            "🌟 Collective celebration amplifies dopamine"
        ],
        "next_session_tip": "💡 Join even if you're not feeling 100% - group energy is contagious!"
    }
