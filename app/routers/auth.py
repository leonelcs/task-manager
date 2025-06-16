"""
Authentication router for ADHD Task Manager.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.google_oauth import google_oauth_service
from app.utils.auth import (
    create_access_token, 
    verify_token, 
    get_user_by_email, 
    get_user_by_google_id,
    create_user_from_google
)
from app.schemas.user import UserResponse, UserCreate
from pydantic import BaseModel
from typing import Optional
import secrets
import string

router = APIRouter()
security = HTTPBearer()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class LoginRequest(BaseModel):
    email: str
    password: str

@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth login.
    Redirects to Google's OAuth consent screen.
    """
    try:
        # Generate state parameter for security
        state = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        auth_url = google_oauth_service.get_auth_url(state=state)
        
        return {
            "auth_url": auth_url,
            "message": "Visit the auth_url to complete Google OAuth login",
            "state": state
        }
    except HTTPException as e:
        # Re-raise HTTPException as-is
        raise e
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Google OAuth: {str(e)}"
        )

@router.get("/google/callback")
async def google_callback(
    code: str = None,
    error: str = None,
    state: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    Exchange authorization code for user information and create/login user.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    try:
        # Exchange code for token
        token_data = await google_oauth_service.exchange_code_for_token(code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token"
            )
        
        # Get user info from Google
        google_user_info = await google_oauth_service.get_user_info(access_token)
        
        # Check if user already exists
        existing_user = get_user_by_google_id(db, google_user_info['id'])
        
        if not existing_user:
            # Check if user exists with same email but different provider
            existing_email_user = get_user_by_email(db, google_user_info['email'])
            if existing_email_user:
                # Link Google account to existing user
                existing_email_user.google_id = google_user_info['id']
                existing_email_user.profile_picture_url = google_user_info.get('picture', '')
                if not existing_email_user.full_name:
                    existing_email_user.full_name = google_user_info.get('name', '')
                db.commit()
                db.refresh(existing_email_user)
                user = existing_email_user
            else:
                # Create new user
                user = create_user_from_google(db, google_user_info)
        else:
            # User exists, update their info
            existing_user.profile_picture_url = google_user_info.get('picture', '')
            existing_user.full_name = google_user_info.get('name', existing_user.full_name)
            db.commit()
            db.refresh(existing_user)
            user = existing_user
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        
        # Redirect to frontend with token
        frontend_url = f"http://localhost:3000/auth/callback?token={access_token}&user_id={user.id}"
        
        return RedirectResponse(url=frontend_url, status_code=302)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Traditional email/password login.
    """
    from app.utils.auth import authenticate_user
    
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔐 Authentication check started")
        logger.info(f"🔐 Token received: {credentials.credentials[:20]}..." if credentials.credentials else "No token")
        
        payload = verify_token(credentials.credentials)
        logger.info(f"🔐 JWT payload decoded successfully: {payload}")
        
        user_id: int = payload.get("user_id")
        logger.info(f"🔐 User ID from token: {user_id}")
        
        if user_id is None:
            logger.error("❌ No user_id found in JWT payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"🔍 Looking up user in database with ID: {user_id}")
        user = db.query(User).filter(User.id == user_id).first()
        
        if user is None:
            logger.error(f"❌ User not found in database with ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"✅ Authentication successful for user: {user.email} (ID: {user.id})")
        return user
        
    except HTTPException as he:
        logger.error(f"❌ HTTP Exception during authentication: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"❌ Unexpected error during authentication: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Stack trace: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return UserResponse.from_orm(current_user)

@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    Since we're using stateless JWT tokens, logout is handled client-side by discarding the token.
    """
    return {
        "message": "Successfully logged out! 👋",
        "tip": "Great job on staying focused today! Don't forget to celebrate your wins! 🎉"
    }
