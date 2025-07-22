# Mobile Authentication Integration Guide

## Overview

This document explains how to integrate the ADHD Task Manager backend with iOS and Android mobile applications.

## iOS Integration

### Google OAuth Configuration

The iOS app uses the following configuration from `config.plist`:

```xml
<key>GoogleOAuth</key>
<dict>
    <key>ClientID</key>
    <string>813648694576-i7ajuil729ci26n7q40fds1ffus1moo0.apps.googleusercontent.com</string>
    <key>ReversedClientID</key>
    <string>com.googleusercontent.apps.813648694576-i7ajuil729ci26n7q40fds1ffus1moo0</string>
    <key>BundleID</key>
    <string>com.engandmore.AdhdTaskManager</string>
</dict>
```

### Backend Configuration

Add these environment variables to your `.env` file:

```bash
# iOS Google OAuth Client ID
GOOGLE_IOS_CLIENT_ID=813648694576-i7ajuil729ci26n7q40fds1ffus1moo0.apps.googleusercontent.com

# iOS Bundle ID
GOOGLE_IOS_BUNDLE_ID=com.engandmore.AdhdTaskManager
```

### Authentication Endpoints

#### 1. Web Authentication (existing)
- **Endpoint**: `GET /api/auth/google/login?origin=web`
- **Usage**: Web applications using OAuth2 flow
- **Response**: Returns authorization URL for redirect

#### 2. Mobile Authentication (new)
- **Endpoint**: `POST /api/auth/mobile/google`
- **Usage**: iOS/Android apps using Google Sign-In SDK
- **Request Body**:
```json
{
    "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "origin": "ios"
}
```
- **Response**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": "123",
        "email": "user@example.com",
        "full_name": "John Doe",
        "profile_picture_url": "https://...",
        "is_active": true
    }
}
```

### iOS Implementation Example

```swift
import GoogleSignIn

// Configure Google Sign-In
guard let path = Bundle.main.path(forResource: "GoogleService-Info", ofType: "plist"),
      let plist = NSDictionary(contentsOfFile: path),
      let clientId = plist["CLIENT_ID"] as? String else {
    // Handle error
    return
}

GIDSignIn.sharedInstance.configuration = GIDConfiguration(clientID: clientId)

// Sign in and get ID token
GIDSignIn.sharedInstance.signIn(withPresenting: viewController) { result, error in
    guard let user = result?.user,
          let idToken = user.idToken?.tokenString else {
        // Handle error
        return
    }
    
    // Send to backend
    let authRequest = [
        "id_token": idToken,
        "origin": "ios"
    ]
    
    // Make API call to /api/auth/mobile/google
    // Handle response and store access_token
}
```

### Security Considerations

1. **Client ID**: The iOS client ID is public and included in the app bundle. This is normal for OAuth2 mobile flows.

2. **ID Token Validation**: The backend validates ID tokens using Google's verification service, ensuring tokens are legitimate and issued by Google.

3. **Bundle ID Verification**: The backend can optionally verify that the token was issued for the correct bundle ID.

4. **Whitelist Check**: All authentication (web and mobile) goes through the same email whitelist for alpha release.

### Error Handling

Common error responses:

- `403 Forbidden`: Email not whitelisted
- `400 Bad Request`: Invalid ID token
- `500 Internal Server Error`: OAuth configuration issues

### Testing

Use the Google Sign-In SDK in your development environment with the provided client ID. The backend will validate tokens against Google's servers.

## Future Enhancements

- Support for additional OAuth providers (Apple Sign-In, Facebook, etc.)
- Device registration for push notifications
- Offline token refresh capabilities
