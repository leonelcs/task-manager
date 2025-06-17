#!/bin/bash
# Script to start the FastAPI server with improved timeout settings

echo "🚀 Starting ADHD Task Manager API with enhanced timeout settings..."

# Navigate to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source bin/activate

# Start uvicorn with timeout settings
echo "⚡ Starting uvicorn with enhanced settings..."
uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --timeout-keep-alive 60 \
    --timeout-graceful-shutdown 10 \
    --access-log \
    --log-level info

echo "✅ Server started with timeout settings!"
