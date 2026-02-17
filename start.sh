#!/bin/bash
# Startup script for Render

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head || echo "Migrations skipped"

# Start the application
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
