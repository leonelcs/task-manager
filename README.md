# ADHD Task Manager API

A FastAPI-based backend for a task management system specifically designed to support people with ADHD in maintaining their periodic tasks and routines.

## Features

- 🧠 **ADHD-Focused Design**: Built with ADHD-specific challenges in mind
- 🤖 **Agentic Behavior**: AI-powered task suggestions based on historical data
- 📊 **Historical Analysis**: Smart insights from past task completion patterns
- ⚡ **FastAPI**: High-performance, modern Python web framework
- 🔄 **Periodic Tasks**: Support for recurring tasks and routines
- 📈 **Progress Tracking**: Monitor task completion and habit formation

## Project Structure

```
task-manager-api/
├── app/
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
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

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
