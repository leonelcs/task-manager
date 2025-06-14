# Examples

This directory contains example files and utilities for testing and demonstrating the ADHD Task Manager functionality.

## Files

### `test_login.html`
A standalone HTML page for testing Google OAuth authentication flow.

**Usage:**
1. Make sure your FastAPI server is running on `http://localhost:8000`
2. Open `http://localhost:8000/examples/test_login.html` in your browser
3. Click "Continue with Google" to test OAuth flow
4. You can also test traditional email/password login

**Features:**
- Google OAuth login button
- Traditional email/password form
- ADHD-friendly UI design
- Error handling and feedback

### `dashboard.html`
A simple dashboard page that displays user information after successful login.

**Usage:**
- Automatically redirected here after successful OAuth login
- Can be accessed directly at `http://localhost:8000/examples/dashboard.html`
- Displays user profile information
- Shows authentication status

### `create_test_user.py`
A utility script to create test users for development and testing.

**Usage:**
```bash
# From the project root directory
source bin/activate
python examples/create_test_user.py
```

**What it does:**
- Creates a test user with email `test@adhdtasks.com`
- Sets password to `testpassword123`
- Initializes ADHD profile with default settings
- Can be used for testing traditional login

## Notes

- These files are for development and testing purposes only
- The HTML files use basic styling and JavaScript for simplicity
- In production, you would replace these with your actual frontend application
- Make sure to update API endpoints if you change the base URL

## Testing the OAuth Flow

1. Set up Google OAuth credentials (see `docs/GCP_OAUTH_DETAILED_SETUP.md`)
2. Start the FastAPI server: `uvicorn app.main:app --reload`
3. Open `http://localhost:8000/examples/test_login.html`
4. Click "Continue with Google"
5. Complete the OAuth flow
6. You should be redirected to the dashboard with your user information
