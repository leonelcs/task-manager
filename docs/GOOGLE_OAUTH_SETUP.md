# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for the ADHD Task Manager application.

## Prerequisites

- Google Cloud Platform account
- Google OAuth credentials (Client ID and Client Secret)

## Step 1: Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
   - Also enable "Google OAuth2 API"

4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized origins:
     - `http://localhost:8000`
     - `http://localhost:3000` (if you have a frontend)
   - Add authorized redirect URIs:
     - `http://localhost:8000/api/auth/google/callback`
   - Save and copy the Client ID and Client Secret

## Step 2: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your Google OAuth credentials:
   ```env
   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-actual-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   ```

## Step 3: Test the OAuth Flow

1. Start the FastAPI server:
   ```bash
   source bin/activate
   uvicorn app.main:app --reload
   ```

2. Open the test login page:
   ```
   http://localhost:8000/test_login.html
   ```

3. Click "Continue with Google" and complete the OAuth flow

## API Endpoints

### Authentication Endpoints

- `GET /api/auth/google/login` - Initiate Google OAuth login
- `GET /api/auth/google/callback` - Handle Google OAuth callback
- `POST /api/auth/login` - Traditional email/password login
- `GET /api/auth/me` - Get current user information
- `POST /api/auth/logout` - Logout (client-side token removal)

### Example Usage

#### Initiate Google OAuth
```javascript
// Get the Google OAuth URL
const response = await fetch('http://localhost:8000/api/auth/google/login');
const data = await response.json();

// Redirect user to Google OAuth
window.location.href = data.auth_url;
```

#### Traditional Login
```javascript
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
// Store token: localStorage.setItem('token', data.access_token);
```

#### Get Current User
```javascript
const response = await fetch('http://localhost:8000/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const user = await response.json();
```

## User Model Changes

The User model has been enhanced to support OAuth authentication:

- `google_id`: Unique Google user identifier
- `profile_picture_url`: User's Google profile picture
- `provider`: Authentication provider ("local" or "google")
- `username`: Made optional for OAuth users
- `hashed_password`: Made optional for OAuth users

## Database Migration

Run the following command to update your database schema:

```bash
source bin/activate
alembic upgrade head
```

## Security Considerations

1. **Environment Variables**: Never commit your actual Google OAuth credentials to version control
2. **HTTPS in Production**: Always use HTTPS in production environments
3. **Token Security**: Consider using httpOnly cookies instead of localStorage for production
4. **CORS**: Configure CORS properly for your frontend domains

## Troubleshooting

### Common Issues

1. **"OAuth error: invalid_client"**
   - Check that your Client ID and Client Secret are correct
   - Verify that the redirect URI matches exactly what's configured in Google Cloud Console

2. **"Authorization code not provided"**
   - User may have denied permissions
   - Check that the OAuth consent screen is properly configured

3. **"Failed to get access token"**
   - Verify that your Google OAuth credentials are correct
   - Check that the Google+ API is enabled

4. **CORS Errors**
   - Update `ALLOWED_ORIGINS` in your environment variables
   - Make sure your frontend domain is included

### Testing

You can test the OAuth flow using the provided HTML files:
- `test_login.html`: Login page with Google OAuth button
- `dashboard.html`: Simple dashboard to display user information

## Production Deployment

For production deployment:

1. Update redirect URIs in Google Cloud Console to match your production domain
2. Use HTTPS for all OAuth endpoints
3. Set secure environment variables
4. Consider implementing refresh tokens for long-lived sessions
5. Use secure, httpOnly cookies instead of localStorage for token storage

## ADHD-Specific Features

The authentication system integrates with ADHD-friendly features:
- Automatic ADHD profile creation for new users
- Energy tracking integration
- Group membership support
- Gamification statistics initialization

Users who sign up via Google OAuth automatically get:
- Default ADHD profile settings
- Energy pattern tracking setup
- Access to collaborative features
- Dopamine reward system activation
