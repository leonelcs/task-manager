"""
Authentication utilities for ADHD Task Manager.
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.models.user import User
from app.config.settings import settings
import secrets
import string

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔐 Verifying JWT token: {token[:20]}...")
        logger.info(f"🔐 Using SECRET_KEY: {settings.SECRET_KEY[:10]}...")
        logger.info(f"🔐 Using algorithm: {settings.ALGORITHM}")
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.info(f"✅ JWT decoded successfully: {payload}")
        return payload
    except JWTError as e:
        logger.error(f"❌ JWT verification failed: {str(e)}")
        logger.error(f"❌ Token that failed: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error during JWT verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Get user by Google ID."""
    return db.query(User).filter(User.google_id == google_id).first()

def create_user_from_google(db: Session, google_user_info: dict) -> User:
    """Create a new user from Google OAuth data."""
    # Generate a unique username from email
    base_username = google_user_info["email"].split("@")[0]
    username = base_username
    counter = 1
    
    # Ensure username is unique
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}_{counter}"
        counter += 1
    
    # Create new user
    user = User(
        username=username,
        email=google_user_info["email"],
        full_name=google_user_info.get("name", ""),
        google_id=google_user_info["id"],
        profile_picture_url=google_user_info.get("picture", ""),
        provider="google",
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Union[User, bool]:
    """Authenticate user with email and password."""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not user.hashed_password:  # OAuth user trying to login with password
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def generate_random_username(base: str = "user") -> str:
    """Generate a random username."""
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{base}_{random_suffix}"
