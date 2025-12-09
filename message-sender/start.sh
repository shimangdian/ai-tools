#!/bin/bash

# Message Sender Service Start Script

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
MODE=${1:-dev}

case "$MODE" in
    dev|local)
        print_info "Starting Message Sender Service in development mode..."

        # Load environment variables if .env file exists
        if [ -f .env ]; then
            print_info "Loading environment variables from .env..."
            export $(cat .env | grep -v '^#' | xargs)
        fi

        # Start the service with hot-reload
        uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload
        ;;

    docker)
        print_info "Starting Message Sender Service with Docker..."

        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            print_error "Docker is not installed!"
            echo "Please install Docker first: https://docs.docker.com/get-docker/"
            exit 1
        fi

        # Check if Docker Compose is installed
        if ! docker compose version &> /dev/null; then
            print_error "Docker Compose is not installed!"
            echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
            exit 1
        fi

        # Check for .env file
        if [ ! -f ".env" ]; then
            print_warn ".env file not found"
            if [ -f ".env.example" ]; then
                print_info "Creating .env from .env.example..."
                cp .env.example .env
                print_warn "Please update .env with your configuration!"
            else
                print_error "No .env.example found. Please create .env manually."
                exit 1
            fi
        fi

        # Load environment variables
        if [ -f ".env" ]; then
            print_info "Loading environment variables from .env..."
            export $(cat .env | grep -v '^#' | xargs)
        fi

        print_info "Building and starting Docker container..."
        docker compose up -d

        print_info "Service started successfully!"
        print_info "API: http://localhost:8000"
        print_info "API Docs: http://localhost:8000/docs"
        print_info "Health Check: http://localhost:8000/health"
        print_info ""
        print_info "View logs: docker compose logs -f"
        ;;

    stop)
        print_info "Stopping Docker container..."
        docker compose down
        print_info "Service stopped successfully!"
        ;;

    restart)
        print_info "Restarting Docker container..."
        docker compose restart
        print_info "Service restarted successfully!"
        ;;

    build)
        print_info "Building Docker image..."
        docker compose build --no-cache
        print_info "Image built successfully!"
        ;;

    logs)
        docker compose logs -f
        ;;

    ps)
        docker compose ps
        ;;

    test)
        print_info "Testing Message Sender Service..."

        # Wait for service to be ready
        print_info "Waiting for service to be ready..."
        sleep 2

        # Test health endpoint
        print_info "Testing health endpoint..."
        curl -f http://localhost:8000/health || {
            print_error "Health check failed!"
            exit 1
        }

        print_info ""
        print_info "✅ Service is healthy!"
        print_info "Visit http://localhost:8000/docs to view the API documentation"
        ;;

    help|--help|-h)
        echo "Message Sender Service Start Script"
        echo ""
        echo "Usage: $0 [MODE]"
        echo ""
        echo "Modes:"
        echo "  dev, local  Start in development mode with hot-reload (default)"
        echo "  docker      Start with Docker Compose"
        echo "  stop        Stop Docker container"
        echo "  restart     Restart Docker container"
        echo "  build       Rebuild Docker image"
        echo "  logs        View Docker logs"
        echo "  ps          Show Docker container status"
        echo "  test        Test the service (Docker mode)"
        echo "  help        Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              # Start in development mode"
        echo "  $0 dev          # Start in development mode"
        echo "  $0 docker       # Start with Docker"
        echo "  $0 stop         # Stop Docker container"
        echo "  $0 logs         # View logs"
        echo ""
        ;;

    *)
        print_error "Unknown mode: $MODE"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
