# Google OAuth Setup Guide

This guide will walk you through setting up Google OAuth authentication for your ADHD Task Manager application.

## Prerequisites

- Google Cloud Platform account
- Python virtual environment activated
- FastAPI server running

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "ADHD Task Manager")
5. Click "Create"

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for and enable the following APIs:
   - **Google+ API** (for user profile information)
   - **Google OAuth2 API** (for authentication)

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Select **External** user type (unless you have a Google Workspace)
3. Click **Create**
4. Fill in the required information:
   - **App name**: ADHD Task Manager
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click **Save and Continue**
6. Skip the "Scopes" section for now (click **Save and Continue**)
7. Add test users (your email and any other emails you want to test with)
8. Click **Save and Continue**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Select **Web application** as the application type
4. Give it a name (e.g., "ADHD Task Manager Web Client")
5. Add **Authorized JavaScript origins**:
   ```
   http://localhost:8000
   http://127.0.0.1:8000
   ```
6. Add **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/auth/google/callback
   ```
7. Click **Create**
8. **IMPORTANT**: Copy the Client ID and Client Secret

## Step 5: Configure Your Application

1. Update your `.env` file in the project root:
   ```env
   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-actual-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   ```

## Step 6: Test the Setup

1. Restart your FastAPI server:
   ```bash
   source bin/activate
   uvicorn app.main:app --reload
   ```

2. Test the OAuth endpoint:
   ```bash
   curl -X GET "http://localhost:8000/api/auth/google/login"
   ```

3. Open the test login page:
   ```
   http://localhost:8000/examples/test_login.html
   ```

## Troubleshooting

### Common Issues:

1. **"OAuth not configured" error**:
   - Check that your `.env` file has the correct values
   - Restart your server after updating the `.env` file

2. **"redirect_uri_mismatch" error**:
   - Make sure the redirect URI in Google Cloud Console exactly matches: `http://localhost:8000/api/auth/google/callback`

3. **"This app isn't verified" warning**:
   - This is normal for development. Click "Advanced" then "Go to [Your App Name] (unsafe)"

## Production Deployment

When deploying to production:

1. Update the **Authorized JavaScript origins** to include your production domain
2. Update the **Authorized redirect URIs** to use HTTPS and your production domain
3. Update the `GOOGLE_REDIRECT_URI` in your production environment variables

## Security Notes

- Never commit your actual OAuth credentials to version control
- The `.env` file should be in your `.gitignore`
- In production, consider using a more secure method for storing secrets
