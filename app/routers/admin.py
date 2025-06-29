"""
Admin router for ADHD Task Manager.
Provides administrative endpoints for managing the application.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.utils.whitelist import get_whitelist_emails, is_email_whitelisted
from pydantic import BaseModel
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class WhitelistStatusResponse(BaseModel):
    """Response model for whitelist status."""
    enabled: bool
    emails: List[str]
    count: int

class EmailCheckRequest(BaseModel):
    """Request model for checking email whitelist status."""
    email: str

class EmailCheckResponse(BaseModel):
    """Response model for email whitelist check."""
    email: str
    is_whitelisted: bool
    message: str

@router.get("/whitelist/status", response_model=WhitelistStatusResponse)
async def get_whitelist_status(current_user: User = Depends(get_current_user)):
    """
    Get the current whitelist status.
    Note: This is for admin/debugging purposes only.
    """
    from app.config.settings import settings
    
    emails = get_whitelist_emails()
    
    return WhitelistStatusResponse(
        enabled=settings.ALPHA_WHITELIST_ENABLED,
        emails=emails,
        count=len(emails)
    )

@router.post("/whitelist/check", response_model=EmailCheckResponse)
async def check_email_whitelist(
    request: EmailCheckRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Check if an email is whitelisted.
    Note: This is for admin/debugging purposes only.
    """
    is_whitelisted = is_email_whitelisted(request.email)
    
    message = (
        f"Email '{request.email}' is whitelisted for alpha access" 
        if is_whitelisted 
        else f"Email '{request.email}' is NOT whitelisted for alpha access"
    )
    
    return EmailCheckResponse(
        email=request.email,
        is_whitelisted=is_whitelisted,
        message=message
    )
