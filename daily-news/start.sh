#!/bin/bash

# Daily News Service Start Script

echo "Starting Daily News Service..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed!"
    echo "Please install Node.js first:"
    echo "  macOS: brew install node"
    echo "  Ubuntu/Debian: sudo apt-get install nodejs npm"
    echo "  Or visit: https://nodejs.org/"
    exit 1
fi

echo "Node.js version: $(node --version)"

# Check if node_modules exists, if not, install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies (Tesseract.js)..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install Node.js dependencies!"
        exit 1
    fi
    echo "Node.js dependencies installed successfully."
else
    echo "Node.js dependencies already installed."
fi

# Load environment variables if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create logs directory if not exists
mkdir -p logs

# Start the service
echo "Starting Python service..."
python -m app.main "$@"
