from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import time
from app.routers import tasks, users, analytics, projects, groups, auth, invitations
from app.database import create_tables
import os
import logging
from dotenv import load_dotenv

# Configure logging
import os
# Get the project root directory (where the log file should be)
current_dir = os.path.dirname(__file__)  # /path/to/task-manager/app
project_root = os.path.dirname(current_dir)  # /path/to/task-manager
log_file_path = os.path.join(project_root, 'adhd_task_manager.log')

print(f"🔍 Log file path: {log_file_path}")
print(f"🔍 Log file exists: {os.path.exists(log_file_path)}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

logger.info("🚀 ADHD Task Manager API Starting Up...")
logger.info("🌍 Loading environment variables...")

# Initialize database tables on startup
logger.info("🗄️ Creating database tables...")
try:
    create_tables()
    logger.info("✅ Database tables created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create database tables: {str(e)}")
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 ADHD Task Manager API startup complete!")
    logger.info("💡 Remember: Every small step counts!")
    
    yield
    
    # Shutdown
    logger.info("👋 ADHD Task Manager API shutting down...")
    logger.info("✨ Great job on all the tasks completed today!")

# Create FastAPI app with ADHD-focused metadata
app = FastAPI(
    title="ADHD Task Manager API",
    lifespan=lifespan,
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

# Timeout middleware disabled - causing issues with task creation
# Will rely on uvicorn timeouts and SQLAlchemy connection timeouts instead
# @app.middleware("http")
# async def timeout_middleware(request: Request, call_next):
#     """Add request timeout middleware to prevent hanging requests."""
#     start_time = time.time()
#     
#     try:
#         # Set timeout based on request type
#         if request.method == "POST":
#             timeout_seconds = 30  # Longer timeout for POST requests (task creation, etc.)
#         elif request.method == "PUT":
#             timeout_seconds = 20  # Medium timeout for updates
#         else:
#             timeout_seconds = 15  # Shorter timeout for GET requests
#         
#         logger.info(f"🕐 Request {request.method} {request.url.path} - timeout set to {timeout_seconds}s")
#         
#         # Execute the request with timeout
#         response = await asyncio.wait_for(
#             call_next(request), 
#             timeout=timeout_seconds
#         )
#         
#         process_time = time.time() - start_time
#         logger.info(f"⏱️ Request {request.method} {request.url.path} completed in {process_time:.2f}s")
#         
#         return response
#         
#     except asyncio.TimeoutError:
#         process_time = time.time() - start_time
#         logger.error(f"⏰ Request {request.method} {request.url.path} timed out after {process_time:.2f}s")
#         raise HTTPException(
#             status_code=504, 
#             detail=f"Request timed out after {timeout_seconds} seconds. Please try again or contact support if this persists."
#         )
#     except Exception as e:
#         process_time = time.time() - start_time
#         logger.error(f"❌ Request {request.method} {request.url.path} failed after {process_time:.2f}s: {str(e)}")
#         raise

# Simple request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log HTTP requests for monitoring"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(groups.router, prefix="/api/shared-groups", tags=["shared-groups"])
app.include_router(invitations.router, prefix="/api/invitations", tags=["invitations"])

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
