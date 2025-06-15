from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tasks, users, analytics, projects, groups, auth
from app.database import create_tables
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize database tables on startup
create_tables()

# Create FastAPI app with ADHD-focused metadata
app = FastAPI(
    title="ADHD Task Manager API",
    description="""
    A specialized task management API designed to support people with ADHD with collaborative features.
    
    ## Features
    
    * **Smart Task Management**: Create, update, and track tasks with ADHD-specific features
    * **🏔️ Rock/Pebbles/Sand Classification**: Prioritize by impact - Rocks (huge & important), Pebbles (meaningful progress), Sand (nice-to-have)
    * **Collaborative Projects**: Work together on shared goals with ADHD-friendly collaboration
    * **Support Groups**: Join communities for accountability and mutual support
    * **Periodic Tasks**: Support for recurring tasks and habit building
    * **AI-Powered Insights**: Get personalized suggestions based on your patterns and impact classification
    * **Executive Function Support**: Break down complex tasks and manage priorities with impact awareness
    * **Dopamine-Friendly Rewards**: Gamified experience with impact-based celebrations
    * **Energy Tracking**: Monitor and optimize your energy patterns with group insights
    
    ## ADHD-Specific Endpoints
    
    The API includes specialized endpoints for:
    - Individual and collaborative task management with Rock/Pebbles/Sand classification
    - Project creation and collaboration (Personal, Shared, Public)
    - Support group management and community features
    - Task breakdown and impact-aware chunking
    - Energy level tracking and sharing
    - Focus session management and body doubling
    - Reward system integration with impact-based celebrations
    - Group accountability and motivation systems
    
    ## 🏔️ Rock/Pebbles/Sand System
    
    **Rocks**: Your biggest, most impactful tasks (1-2 per day max)
    - Schedule during peak energy hours
    - Major career/life impact
    - Deserve your best focus
    
    **Pebbles**: Important tasks that build momentum (3-5 per day)
    - Support your bigger goals  
    - Great for building consistency
    - Perfect between rocks
    
    **Sand**: Nice-to-have, possibly delegatable tasks
    - Fill gaps naturally
    - Don't let these crowd out rocks
    - Good for low-energy periods
    """,
    version="1.0.0",
    contact={
        "name": "ADHD Task Manager Team",
        "email": "support@adhdtaskmanager.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS middleware configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])

@app.get("/", tags=["root"])
async def read_root():
    """
    Welcome endpoint with ADHD-friendly messaging.
    """
    return {
        "message": "Welcome to the ADHD Task Manager API! 🧠✨",
        "status": "running",
        "features": [
            "Smart task management with Rock/Pebbles/Sand classification",
            "Collaborative projects",
            "Support groups", 
            "ADHD-specific support",
            "AI-powered insights with impact awareness",
            "Habit tracking",
            "Dopamine rewards",
            "Community accountability"
        ],
        "new_feature": "🏔️ Rock/Pebbles/Sand Classification - Prioritize by impact for maximum ADHD effectiveness!",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "service": "adhd-task-manager-api"}

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    """
    print("🚀 ADHD Task Manager API is starting up...")
    print("💡 Remember: Every small step counts!")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    """
    print("👋 ADHD Task Manager API is shutting down...")
    print("✨ Great job on all the tasks completed today!")
