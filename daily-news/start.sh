#!/bin/bash

# Daily News Service Start Script

echo "Starting Daily News Service..."

# Load environment variables if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create logs directory if not exists
mkdir -p logs

# Start the service
python -m app.main "$@"
