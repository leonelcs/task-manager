# ADHD Task Manager - Backend API

FastAPI backend for the ADHD Task Manager application.

## Quick Start

```bash
# Setup environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and OAuth settings

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables
```bash
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/adhd_tasks_dev
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000
```

## Database Operations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Testing
```bash
pytest -v
```

For complete documentation, see the [docs-site](../docs-site/).
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── user.py
│   │   └── analytics.py
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   ├── users.py
│   │   └── analytics.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── task.py
│   │   └── user.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── task_service.py
│   │   └── ai_service.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip or poetry for dependency management

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd task-manager-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration (especially Google OAuth credentials)
```

5. Set up Google OAuth (see [OAuth Setup Guide](docs/GCP_OAUTH_DETAILED_SETUP.md))

6. Run database migrations:
```bash
alembic upgrade head
```

7. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`
- Test login page: `http://localhost:8000/examples/test_login.html`

## Authentication

The application supports both traditional email/password authentication and Google OAuth.

### Google OAuth Setup
For Google OAuth configuration, see the detailed guide: [OAuth Setup Guide](docs/GCP_OAUTH_DETAILED_SETUP.md)

### API Endpoints
- `GET /api/auth/google/login` - Initiate Google OAuth login
- `POST /api/auth/login` - Traditional email/password login
- `GET /api/auth/me` - Get current user information
- `POST /api/auth/logout` - Logout

## ADHD-Specific Features

### Task Types
- **Routine Tasks**: Daily habits and recurring activities
- **Project Tasks**: Larger goals broken into manageable chunks
- **Maintenance Tasks**: Regular upkeep activities
- **Emergency Tasks**: Urgent items that need immediate attention

### ADHD Support Features
- **Dopamine Rewards**: Gamified task completion
- **Time Blocking**: Built-in time management suggestions
- **Break Reminders**: Automatic break scheduling
- **Hyperfocus Protection**: Alerts for extended work sessions
- **Executive Function Support**: Task breakdown and prioritization

### AI-Powered Insights
- **Pattern Recognition**: Identifies optimal work times and conditions
- **Task Suggestion**: Recommends tasks based on energy levels and context
- **Difficulty Adjustment**: Adapts task complexity based on performance
- **Motivation Boost**: Provides encouragement and celebrates progress

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support with ADHD-related features or general questions, please open an issue or contact the maintainers.
