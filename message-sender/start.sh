#!/bin/bash

# Message Sender Service Start Script

echo "Starting Message Sender Service..."

# Load environment variables if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload
