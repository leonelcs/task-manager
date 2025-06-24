"""
SharedGroup invitation router for ADHD Task Manager.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models.invitation import SharedGroupInvitation, InvitationStatus
from app.models.group import SharedGroup, SharedGroupMembership, SharedGroupRole
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.invitation import (
    SharedGroupInvitationCreate, SharedGroupInvitationResponse, SharedGroupInvitationAccept,
    SharedGroupInvitationList, InvitationEmailData
)
from app.services.email_service import send_invitation_email
import json

router = APIRouter()


@router.post("/groups/{shared_group_id}/invite", response_model=SharedGroupInvitationResponse)
async def invite_to_shared_group(
    shared_group_id: str,
    invitation_data: SharedGroupInvitationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a user to join an ADHD support group.
    
    **ADHD Features:**
    - Supportive invitation messaging
    - Clear role expectations
    - ADHD-specific group benefits highlighted
    - Welcoming community atmosphere
    """
    # Get the group
    group = db.query(SharedGroup).filter(SharedGroup.id == shared_group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if current user has permission to invite (owner or admin)
    membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.role.in_([SharedGroupRole.OWNER, SharedGroupRole.ADMIN]),
        SharedGroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403, 
            detail="Only group owners and admins can send invitations"
        )
    
    # Check if user is already a member
    existing_membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.is_active == True
    ).join(User).filter(User.email == invitation_data.invited_email).first()
    
    if existing_membership:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this group"
        )
    
    # Check for existing pending invitation
    existing_invitation = db.query(SharedGroupInvitation).filter(
        SharedGroupInvitation.shared_group_id == shared_group_id,
        SharedGroupInvitation.invited_email == invitation_data.invited_email,
        SharedGroupInvitation.status == InvitationStatus.PENDING
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=400,
            detail="A pending invitation already exists for this email"
        )
    
    # Check if invited user exists
    invited_user = db.query(User).filter(User.email == invitation_data.invited_email).first()
    
    # Create invitation
    invitation = SharedGroupInvitation(
        shared_group_id=shared_group_id,
        invited_email=invitation_data.invited_email,
        invited_user_id=invited_user.id if invited_user else None,
        invited_by=current_user.id,
        role=invitation_data.role,
        message=invitation_data.message,
        expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days to accept
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # Prepare email data
    email_data = InvitationEmailData(
        recipient_email=invitation_data.invited_email,
        recipient_name=invited_user.full_name if invited_user else None,
        group_name=group.name,
        group_description=group.description,
        inviter_name=current_user.full_name or current_user.email,
        invitation_token=invitation.token,
        invitation_message=invitation_data.message,
        invitation_url=f"http://localhost:3000/invitations/{invitation.token}",
        expires_at=invitation.expires_at
    )
    
    # Build group features from individual ADHD settings
    group_features = {
        "group_focus_sessions": group.group_focus_sessions,
        "shared_energy_tracking": group.shared_energy_tracking,
        "group_dopamine_celebrations": group.group_dopamine_celebrations,
        "collaborative_task_chunking": group.collaborative_task_chunking,
        "group_break_reminders": group.group_break_reminders,
        "accountability_features": group.accountability_features
    }
    email_data.group_features = group_features
    
    # Send invitation email in background
    background_tasks.add_task(send_invitation_email, email_data)
    
    return SharedGroupInvitationResponse(
        id=invitation.id,
        token=invitation.token,
        shared_group_id=invitation.shared_group_id,
        invited_email=invitation.invited_email,
        invited_user_id=invitation.invited_user_id,
        invited_by=invitation.invited_by,
        role=invitation.role,
        status=invitation.status,
        message=invitation.message,
        created_at=invitation.created_at,
        expires_at=invitation.expires_at,
        responded_at=invitation.responded_at,
        group_name=group.name,
        group_description=group.description,
        inviter_name=current_user.full_name or current_user.email
    )


@router.get("/groups/{shared_group_id}", response_model=List[SharedGroupInvitationResponse])
async def get_group_invitations(
    shared_group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all invitations for a shared group (for group admins/owners).
    """
    # Check if current user has permission to view invitations (owner or admin)
    membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.role.in_([SharedGroupRole.OWNER, SharedGroupRole.ADMIN]),
        SharedGroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403, 
            detail="Only group owners and admins can view invitations"
        )
    
    # Get the group
    group = db.query(SharedGroup).filter(SharedGroup.id == shared_group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get all invitations for this group
    invitations = db.query(SharedGroupInvitation).filter(
        SharedGroupInvitation.shared_group_id == shared_group_id
    ).order_by(SharedGroupInvitation.created_at.desc()).all()
    
    invitation_responses = []
    for invitation in invitations:
        # Get inviter details
        inviter = db.query(User).filter(User.id == invitation.invited_by).first()
        
        invitation_responses.append(SharedGroupInvitationResponse(
            id=invitation.id,
            token=invitation.token,
            shared_group_id=invitation.shared_group_id,
            invited_email=invitation.invited_email,
            invited_user_id=invitation.invited_user_id,
            invited_by=invitation.invited_by,
            role=invitation.role,
            status=invitation.status,
            message=invitation.message,
            created_at=invitation.created_at,
            expires_at=invitation.expires_at,
            responded_at=invitation.responded_at,
            group_name=group.name,
            group_description=group.description,
            inviter_name=inviter.full_name if inviter and inviter.full_name else inviter.email if inviter else None
        ))
    
    return invitation_responses


@router.post("/groups/{shared_group_id}/{invitation_id}/resend")
async def resend_invitation(
    shared_group_id: str,
    invitation_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resend a pending invitation.
    """
    # Check if current user has permission (owner or admin)
    membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.role.in_([SharedGroupRole.OWNER, SharedGroupRole.ADMIN]),
        SharedGroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403, 
            detail="Only group owners and admins can resend invitations"
        )
    
    # Get the invitation
    invitation = db.query(SharedGroupInvitation).filter(
        SharedGroupInvitation.id == invitation_id,
        SharedGroupInvitation.shared_group_id == shared_group_id,
        SharedGroupInvitation.status == InvitationStatus.PENDING
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=404, 
            detail="Invitation not found or not pending"
        )
    
    # Get the group
    group = db.query(SharedGroup).filter(SharedGroup.id == shared_group_id).first()
    
    # Check if invited user exists
    invited_user = db.query(User).filter(User.email == invitation.invited_email).first()
    
    # Prepare email data
    email_data = InvitationEmailData(
        recipient_email=invitation.invited_email,
        recipient_name=invited_user.full_name if invited_user else None,
        group_name=group.name,
        group_description=group.description,
        inviter_name=current_user.full_name or current_user.email,
        invitation_token=invitation.token,
        invitation_message=invitation.message,
        invitation_url=f"http://localhost:3000/invitations/{invitation.token}",
        expires_at=invitation.expires_at
    )
    
    # Build group features from individual ADHD settings
    group_features = {
        "group_focus_sessions": group.group_focus_sessions,
        "shared_energy_tracking": group.shared_energy_tracking,
        "group_dopamine_celebrations": group.group_dopamine_celebrations,
        "collaborative_task_chunking": group.collaborative_task_chunking,
        "group_break_reminders": group.group_break_reminders,
        "accountability_features": group.accountability_features
    }
    email_data.group_features = group_features
    
    # Send invitation email in background
    background_tasks.add_task(send_invitation_email, email_data)
    
    return {
        "message": "Invitation resent successfully",
        "invitation_id": invitation_id,
        "invited_email": invitation.invited_email,
        "note": "📧 The invitation email has been sent again. Please check your email (including spam folder)."
    }


@router.delete("/groups/{shared_group_id}/{invitation_id}")
async def cancel_invitation(
    shared_group_id: str,
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a pending invitation.
    """
    # Check if current user has permission (owner or admin)
    membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.role.in_([SharedGroupRole.OWNER, SharedGroupRole.ADMIN]),
        SharedGroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403, 
            detail="Only group owners and admins can cancel invitations"
        )
    
    # Get the invitation
    invitation = db.query(SharedGroupInvitation).filter(
        SharedGroupInvitation.id == invitation_id,
        SharedGroupInvitation.shared_group_id == shared_group_id,
        SharedGroupInvitation.status == InvitationStatus.PENDING
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=404, 
            detail="Invitation not found or not pending"
        )
    
    # Update invitation status to expired/cancelled
    invitation.status = InvitationStatus.EXPIRED
    invitation.responded_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Invitation cancelled successfully",
        "invitation_id": invitation_id,
        "invited_email": invitation.invited_email,
        "note": "The invitation has been cancelled and can no longer be used."
    }


@router.get("/me", response_model=SharedGroupInvitationList)
async def get_my_invitations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all invitations for the current user.
    """
    invitations = db.query(SharedGroupInvitation).filter(
        SharedGroupInvitation.invited_email == current_user.email
    ).order_by(SharedGroupInvitation.created_at.desc()).all()
    
    invitation_responses = []
    pending_count = 0
    
    for invitation in invitations:
        # Get group and inviter details
        group = db.query(SharedGroup).filter(SharedGroup.id == invitation.shared_group_id).first()
        inviter = db.query(User).filter(User.id == invitation.invited_by).first()
        
        if invitation.status == InvitationStatus.PENDING:
            pending_count += 1
        
        invitation_responses.append(SharedGroupInvitationResponse(
            id=invitation.id,
            token=invitation.token,
            shared_group_id=invitation.shared_group_id,
            invited_email=invitation.invited_email,
            invited_user_id=invitation.invited_user_id,
            invited_by=invitation.invited_by,
            role=invitation.role,
            status=invitation.status,
            message=invitation.message,
            created_at=invitation.created_at,
            expires_at=invitation.expires_at,
            responded_at=invitation.responded_at,
            group_name=group.name if group else None,
            group_description=group.description if group else None,
            inviter_name=inviter.full_name if inviter and inviter.full_name else inviter.email if inviter else None
        ))
    
    return SharedGroupInvitationList(
        invitations=invitation_responses,
        total=len(invitation_responses),
        pending_count=pending_count
    )


@router.get("/{token}", response_model=SharedGroupInvitationResponse)
async def get_invitation(token: str, db: Session = Depends(get_db)):
    """
    Get invitation details by token.
    """
    invitation = db.query(SharedGroupInvitation).filter(
        SharedGroupInvitation.token == token
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Check if invitation is expired
    if invitation.expires_at and invitation.expires_at < datetime.utcnow():
        invitation.status = InvitationStatus.EXPIRED
        db.commit()
        
    # Get group and inviter details
    group = db.query(SharedGroup).filter(SharedGroup.id == invitation.shared_group_id).first()
    inviter = db.query(User).filter(User.id == invitation.invited_by).first()
    
    return SharedGroupInvitationResponse(
        id=invitation.id,
        token=invitation.token,
        shared_group_id=invitation.shared_group_id,
        invited_email=invitation.invited_email,
        invited_user_id=invitation.invited_user_id,
        invited_by=invitation.invited_by,
        role=invitation.role,
        status=invitation.status,
        message=invitation.message,
        created_at=invitation.created_at,
        expires_at=invitation.expires_at,
        responded_at=invitation.responded_at,
        group_name=group.name if group else None,
        group_description=group.description if group else None,
        inviter_name=inviter.full_name if inviter and inviter.full_name else inviter.email if inviter else None
    )


@router.post("/{token}/accept")
async def accept_invitation(
    token: str,
    accept_data: SharedGroupInvitationAccept,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept a group invitation with ADHD-friendly onboarding.
    """
    invitation = db.query(SharedGroupInvitation).filter(
        SharedGroupInvitation.token == token,
        SharedGroupInvitation.status == InvitationStatus.PENDING
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or already processed")
    
    # Check if invitation is expired
    if invitation.expires_at and invitation.expires_at < datetime.utcnow():
        invitation.status = InvitationStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=400, detail="Invitation has expired")
    
    # Check if current user is the invited user
    if invitation.invited_email != current_user.email:
        raise HTTPException(
            status_code=403,
            detail="You can only accept invitations sent to your email"
        )
    
    # Check if user is already a member
    existing_membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == invitation.shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.is_active == True
    ).first()
    
    if existing_membership:
        raise HTTPException(status_code=400, detail="You are already a member of this group")
    
    # Create group membership
    membership = SharedGroupMembership(
        shared_group_id=invitation.shared_group_id,
        user_id=current_user.id,
        role=SharedGroupRole.MEMBER if invitation.role == "member" else SharedGroupRole.ADMIN,
        is_active=True
    )
    
    # Update member settings based on welcome preferences
    if accept_data.welcome_preferences:
        member_settings = {
            "share_energy_patterns": accept_data.welcome_preferences.get("share_energy_patterns", False),
            "receive_group_motivations": True,
            "participate_in_group_focus": accept_data.welcome_preferences.get("join_group_focus_session", True),
            "notification_preferences": "normal"
        }
        membership.member_settings = json.dumps(member_settings)
    
    db.add(membership)
    
    # Update invitation status
    invitation.status = InvitationStatus.ACCEPTED
    invitation.responded_at = datetime.utcnow()
    invitation.invited_user_id = current_user.id
    
    db.commit()
    
    # Get group details for response
    group = db.query(SharedGroup).filter(SharedGroup.id == invitation.shared_group_id).first()
    
    return {
        "message": f"🎉 Welcome to {group.name}!",
        "group_id": invitation.shared_group_id,
        "group_name": group.name,
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
        "next_steps": [
            f"Visit the group page to see active projects",
            "Update your member preferences if needed",
            "Consider joining the next group focus session"
        ]
    }


@router.post("/{token}/decline")
async def decline_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Decline a group invitation.
    """
    invitation = db.query(SharedGroupInvitation).filter(
        SharedGroupInvitation.token == token,
        SharedGroupInvitation.status == InvitationStatus.PENDING
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or already processed")
    
    # Check if current user is the invited user
    if invitation.invited_email != current_user.email:
        raise HTTPException(
            status_code=403,
            detail="You can only decline invitations sent to your email"
        )
    
    # Update invitation status
    invitation.status = InvitationStatus.DECLINED
    invitation.responded_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Invitation declined",
        "note": "You can always ask for another invitation later if you change your mind!"
    }


@router.delete("/groups/{shared_group_id}/clear-pending")
async def clear_pending_invitations(
    shared_group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all pending invitations for a group (development/admin endpoint).
    """
    # Check if current user has permission (owner only for this operation)
    membership = db.query(SharedGroupMembership).filter(
        SharedGroupMembership.shared_group_id == shared_group_id,
        SharedGroupMembership.user_id == current_user.id,
        SharedGroupMembership.role == SharedGroupRole.OWNER,
        SharedGroupMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403, 
            detail="Only group owners can clear pending invitations"
        )
    
    # Get all pending invitations for this group
    pending_invitations = db.query(SharedGroupInvitation).filter(
        SharedGroupInvitation.shared_group_id == shared_group_id,
        SharedGroupInvitation.status == InvitationStatus.PENDING
    ).all()
    
    # Mark them as expired
    cleared_count = 0
    for invitation in pending_invitations:
        invitation.status = InvitationStatus.EXPIRED
        invitation.responded_at = datetime.utcnow()
        cleared_count += 1
    
    db.commit()
    
    return {
        "message": f"Cleared {cleared_count} pending invitations",
        "cleared_count": cleared_count,
        "note": "All pending invitations have been marked as expired. You can now send new invitations."
    }
