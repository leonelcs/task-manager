# ADHD Task Manager API - Postman Testing Collection

This directory contains comprehensive Postman collections and environments to test the ADHD Task Manager API with all its collaborative and ADHD-specific features.

## Files Included

- `ADHD_Task_Manager_API.postman_collection.json` - Complete API collection with all endpoints
- `ADHD_Task_Manager_Local.postman_environment.json` - Local development environment variables

All files are located in the `postman/` directory to keep the project root organized.

## 🚀 Quick Setup

### 1. Import Collection and Environment

1. **Open Postman**
2. **Import Collection:**
   - Click "Import" button
   - Navigate to the `postman/` folder
   - Select `ADHD_Task_Manager_API.postman_collection.json`
   - Click "Import"

3. **Import Environment:**
   - Click "Import" button 
   - Navigate to the `postman/` folder
   - Select `ADHD_Task_Manager_Local.postman_environment.json`
   - Click "Import"

4. **Select Environment:**
   - In the top-right corner, select "ADHD Task Manager - Local" environment

### 2. Start the API Server

Make sure your API server is running:

```bash
# Activate virtual environment
source bin/activate

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📋 Collection Structure

### 🏠 Root & Health
- **Welcome Message** - Get API overview and feature list
- **Health Check** - Verify API is running properly

### 📋 Tasks (ADHD-Friendly Task Management)
- **Get All Tasks** - Retrieve tasks with ADHD-friendly filtering
- **Get Tasks - Filter by Status** - Filter by todo, in_progress, completed, paused
- **Get Tasks - Filter by Priority** - Filter by priority and ADHD task types
- **Get Specific Task** - Detailed task info with ADHD features
- **Create New Task** - Create tasks with dopamine rewards and chunking
- **Complete Task** - Mark complete with celebration and streak tracking
- **Get AI Task Suggestions** - AI-powered ADHD-specific recommendations

### 👥 Users (ADHD Profile Management)
- **Get User Profile** - Retrieve ADHD preferences and statistics
- **Update ADHD Preferences** - Customize energy patterns, focus duration, triggers
- **Log Energy Level** - Track energy for pattern analysis
- **Get Energy History** - Retrieve energy patterns over time

### 🚀 Projects (Collaborative Project Management)
- **Get All Projects** - List personal, shared, and public projects
- **Get Projects - Filter by Type** - Filter by project type and status
- **Get Specific Project** - Detailed project with collaboration features
- **Create New Project** - Create with ADHD-specific collaborative features
- **Update Project** - ADHD-friendly change management
- **Invite to Project** - Invite collaborators with supportive messaging
- **Join Project** - Join with ADHD-friendly onboarding
- **Get Project Collaborators** - View collaboration insights

### 👫 Groups (ADHD Support Communities)
- **Get All Groups** - List support groups with member counts
- **Get Specific Group** - Detailed group info with energy summaries
- **Create New Group** - Create ADHD support groups
- **Update Group** - Gentle change management for groups
- **Invite to Group** - Supportive invitation with community benefits
- **Join Group** - ADHD-friendly community onboarding
- **Get Group Members** - Community health and dynamics
- **Update Group Member** - Role and settings management
- **Get Group Focus Sessions** - Body doubling and focus opportunities

### 📊 Analytics (ADHD-Focused Insights)
- **Get Analytics Dashboard** - Comprehensive ADHD insights
- **Get Productivity Patterns** - Energy and productivity correlations
- **Get Energy Correlation** - Energy level impact analysis  
- **Get Focus Analytics** - Focus session patterns and effectiveness
- **Get Habit Formation** - Habit tracking and formation progress

## 🧠 ADHD-Specific Features Tested

### Task Management
- ✅ Dopamine reward systems
- ✅ Task chunking and breakdown
- ✅ Energy level matching
- ✅ Break reminders
- ✅ Hyperfocus protection
- ✅ Overwhelm prevention (limited results)

### Collaborative Features
- ✅ Group accountability
- ✅ Shared focus sessions (body doubling)
- ✅ Community celebrations
- ✅ Supportive messaging
- ✅ Energy sharing and tracking
- ✅ Collective break reminders

### Analytics & Insights
- ✅ Energy pattern analysis
- ✅ Productivity correlations
- ✅ Focus session effectiveness
- ✅ Habit formation tracking
- ✅ AI-powered suggestions
- ✅ Streak and motivation tracking

## 🔧 Environment Variables

The collection uses these environment variables (pre-configured):

- `baseUrl` - API base URL (http://localhost:8001)
- `apiPrefix` - API prefix (/api)
- `userId` - Sample user ID for testing (1)
- `projectId` - Sample project ID for testing (1)
- `groupId` - Sample group ID for testing (1)
- `taskId` - Sample task ID for testing (1)

## 🧪 Testing Scenarios

### Basic Workflow Test
1. **Health Check** - Verify API is running
2. **Get User Profile** - Check ADHD preferences
3. **Get All Tasks** - View current tasks with ADHD features
4. **Create New Task** - Test task creation with dopamine rewards
5. **Complete Task** - Test celebration and streak tracking

### Collaboration Test
1. **Create New Project** - Test project creation with ADHD features
2. **Invite to Project** - Test supportive collaboration invitation
3. **Create New Group** - Test ADHD support group creation
4. **Get Group Focus Sessions** - Test body doubling features

### Analytics Test
1. **Get Analytics Dashboard** - Test comprehensive ADHD insights
2. **Log Energy Level** - Test energy tracking
3. **Get Productivity Patterns** - Test pattern analysis
4. **Get AI Task Suggestions** - Test ADHD-specific AI recommendations

## 🎯 Success Indicators

Look for these ADHD-specific features in responses:

### Task Responses
- 🎉 Dopamine reward messages
- 🔥 Streak tracking and bonuses
- 💡 ADHD tips and encouragement
- ⚡ Energy level recommendations
- 🧠 Break and focus reminders

### Collaboration Responses
- 🤝 Supportive community messaging
- 🌟 Group energy and motivation
- 👥 Member engagement metrics
- 🎯 Collective accountability features
- 💪 Community values and guidelines

### Analytics Responses
- 📊 Energy pattern insights
- ⏰ Optimal timing recommendations
- 🎯 Focus session effectiveness
- 🔄 Habit formation progress
- 🤖 AI-powered ADHD suggestions

## 🆘 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure API server is running on port 8001
   - Check if port is already in use: `lsof -i :8001`

2. **404 Not Found**
   - Verify the endpoint path is correct
   - Check if the API prefix `/api` is included

3. **Environment Variables Not Working**
   - Ensure "ADHD Task Manager - Local" environment is selected
   - Check variable names match exactly

### API Server Commands

```bash
# Check if server is running
curl http://localhost:8001/health

# Start server with different port if needed
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Check server logs for errors
tail -f logs/api.log  # if logging is configured
```

## 🎨 Customization

### Adding New Endpoints
1. Add request to appropriate folder in collection
2. Use existing environment variables where possible
3. Include ADHD-specific features in request/response examples
4. Add relevant tests for ADHD functionality

### Creating Additional Environments
1. Duplicate the local environment
2. Update `baseUrl` for different environments (staging, production)
3. Adjust any environment-specific variables

## 📝 Notes

- All endpoints include ADHD-friendly response formatting
- Mock data responses demonstrate ADHD-specific features
- Collection includes comprehensive testing scenarios
- Environment variables make it easy to switch between environments
- Built-in tests check for successful responses and JSON format

Happy testing! 🧠✨ Remember: every small step in testing helps build a better ADHD support tool!
