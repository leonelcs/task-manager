"""
Google OAuth service for ADHD Task Manager.
"""
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from fastapi import HTTPException, status
from app.config.settings import settings
import httpx
from typing import Dict, Any
from urllib.parse import urlencode
import os


class GoogleOAuthService:
    """Service for handling Google OAuth authentication."""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        
        # iOS OAuth settings
        self.ios_client_id = settings.GOOGLE_IOS_CLIENT_ID
        self.ios_bundle_id = settings.GOOGLE_IOS_BUNDLE_ID
        
        # OAuth 2.0 scopes for Google
        self.scopes = [
            'openid',
            'email',
            'profile'
        ]
        
        # Google OAuth endpoints
        self.google_auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_client_id(self, origin: str = "web") -> str:
        """Get the appropriate client ID based on origin."""
        if origin == "ios" and self.ios_client_id:
            return self.ios_client_id
        return self.client_id
    
    def get_auth_url(self, state: str = None, origin: str = "web") -> str:
        """Generate Google OAuth authorization URL."""
        client_id = self.get_client_id(origin)
        
        if not client_id or client_id == "your-google-client-id.apps.googleusercontent.com":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file"
            )
        
        params = {
            'client_id': client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        if state:
            params['state'] = state
        
        # Build URL manually with proper URL encoding
        return f"{self.google_auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        if not self.client_id or not self.client_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured"
            )
        
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.google_token_url, data=token_data)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google."""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.google_userinfo_url, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Google"
                )
            
            user_info = response.json()
            
            # Ensure required fields are present
            required_fields = ['id', 'email']
            for field in required_fields:
                if field not in user_info:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Missing required field: {field}"
                    )
            
            return user_info
    
    def verify_id_token(self, id_token_str: str, origin: str = "web") -> Dict[str, Any]:
        """Verify Google ID token."""
        try:
            client_id = self.get_client_id(origin)
            
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return idinfo
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ID token: {str(e)}"
            )


# Global instance
google_oauth_service = GoogleOAuthService()
