"""
Test for the updated projects endpoint that follows the comprehensive access rules.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.project import Project, ProjectType, ProjectStatus, ProjectCollaboration
from app.models.group import SharedGroup, SharedGroupMembership, SharedGroupRole
from app.routers.auth import get_current_user
import uuid

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_projects.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Create test user for dependency override
test_user = None

def override_get_current_user():
    return test_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def sample_user(db_session):
    global test_user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    test_user = user
    return user

def test_projects_endpoint_comprehensive_access(setup_database, db_session, sample_user):
    """
    Test the /projects/ endpoint to ensure it returns projects according to the comprehensive access rules:
    1. All active projects from shared groups where user is a member
    2. All active projects created by the user (owned)
    3. All active public projects where the user participates (as collaborator)
    """
    
    # Create a shared group and add user as member
    shared_group = SharedGroup(
        id=str(uuid.uuid4()),
        name="Test Group",
        description="Test group for projects",
        created_by=sample_user.id,
        is_active=True
    )
    db_session.add(shared_group)
    
    # Add user to the shared group
    group_membership = SharedGroupMembership(
        shared_group_id=shared_group.id,
        user_id=sample_user.id,
        role=SharedGroupRole.MEMBER,
        is_active=True
    )
    db_session.add(group_membership)
    
    # Create different types of projects
    
    # 1. User's own project (should be returned)
    owned_project = Project(
        id=str(uuid.uuid4()),
        name="My Personal Project",
        description="A project I own",
        project_type=ProjectType.PERSONAL,
        status=ProjectStatus.ACTIVE,
        owner_id=sample_user.id,
        is_active=True
    )
    db_session.add(owned_project)
    
    # 2. Project in the shared group (should be returned)
    group_project = Project(
        id=str(uuid.uuid4()),
        name="Group Project",
        description="A project in my group",
        project_type=ProjectType.SHARED,
        status=ProjectStatus.ACTIVE,
        owner_id=str(uuid.uuid4()),  # Different owner
        shared_group_id=shared_group.id,
        is_active=True
    )
    db_session.add(group_project)
    
    # 3. Public project where user is a collaborator (should be returned)
    public_project = Project(
        id=str(uuid.uuid4()),
        name="Public Collaboration Project",
        description="A public project I collaborate on",
        project_type=ProjectType.PUBLIC,
        status=ProjectStatus.ACTIVE,
        owner_id=str(uuid.uuid4()),  # Different owner
        is_active=True
    )
    db_session.add(public_project)
    
    # Add user as collaborator to the public project
    collaboration = ProjectCollaboration(
        project_id=public_project.id,
        user_id=sample_user.id,
        role="collaborator",
        is_active=True
    )
    db_session.add(collaboration)
    
    # 4. Project user should NOT see (not owned, not in group, not collaborating)
    inaccessible_project = Project(
        id=str(uuid.uuid4()),
        name="Inaccessible Project",
        description="A project I should not see",
        project_type=ProjectType.PERSONAL,
        status=ProjectStatus.ACTIVE,
        owner_id=str(uuid.uuid4()),  # Different owner
        is_active=True
    )
    db_session.add(inaccessible_project)
    
    db_session.commit()
    
    # Test the endpoint
    response = client.get("/projects/")
    assert response.status_code == 200
    
    projects = response.json()
    project_names = [p["name"] for p in projects]
    
    # Verify the correct projects are returned
    assert "My Personal Project" in project_names
    assert "Group Project" in project_names
    assert "Public Collaboration Project" in project_names
    assert "Inaccessible Project" not in project_names
    
    # Verify the response structure includes new fields
    for project in projects:
        assert "access_source" in project
        assert "user_role_in_project" in project
        assert "shared_group_name" in project or project["shared_group_name"] is None
        assert "user_role_in_group" in project or project["user_role_in_group"] is None
    
    # Verify access sources are correct
    access_sources = {p["name"]: p["access_source"] for p in projects}
    assert access_sources["My Personal Project"] == "owned"
    assert access_sources["Group Project"] == "shared_group"
    assert access_sources["Public Collaboration Project"] == "public_collaboration"

def test_projects_endpoint_filters(setup_database, db_session, sample_user):
    """
    Test that the endpoint respects project_type and status filters.
    """
    
    # Create projects of different types and statuses
    personal_active = Project(
        id=str(uuid.uuid4()),
        name="Personal Active",
        project_type=ProjectType.PERSONAL,
        status=ProjectStatus.ACTIVE,
        owner_id=sample_user.id,
        is_active=True
    )
    
    personal_completed = Project(
        id=str(uuid.uuid4()),
        name="Personal Completed",
        project_type=ProjectType.PERSONAL,
        status=ProjectStatus.COMPLETED,
        owner_id=sample_user.id,
        is_active=True
    )
    
    db_session.add_all([personal_active, personal_completed])
    db_session.commit()
    
    # Test status filter
    response = client.get("/projects/?status=active")
    assert response.status_code == 200
    projects = response.json()
    statuses = [p["status"] for p in projects]
    assert all(status == "active" for status in statuses)
    
    # Test project_type filter
    response = client.get("/projects/?project_type=personal")
    assert response.status_code == 200
    projects = response.json()
    types = [p["project_type"] for p in projects]
    assert all(ptype == "personal" for ptype in types)

if __name__ == "__main__":
    pytest.main([__file__])
