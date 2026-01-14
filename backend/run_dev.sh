#!/bin/bash

# Run the FastAPI backend in development mode with auto-reload

cd "$(dirname "$0")/.."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY"
    exit 1
fi

echo "Starting FastAPI server in development mode..."
echo "API will be available at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""

# Run with auto-reload using uv
uv run uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
