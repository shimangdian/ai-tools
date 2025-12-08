#!/bin/bash

# AI Tools Docker Deployment Script

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
    if [ -f "message-sender/.env.example" ]; then
        print_info "Creating .env from message-sender/.env.example..."
        cp message-sender/.env.example .env
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

# Parse command line arguments
COMMAND=${1:-up}

case "$COMMAND" in
    up)
        print_info "Starting AI Tools services..."
        docker compose up -d
        print_info "Services started successfully!"
        print_info "Message Sender API: http://localhost:8000"
        print_info "Check logs: docker compose logs -f"
        ;;

    down)
        print_info "Stopping AI Tools services..."
        docker compose down
        print_info "Services stopped successfully!"
        ;;

    restart)
        print_info "Restarting AI Tools services..."
        docker compose restart
        print_info "Services restarted successfully!"
        ;;

    build)
        print_info "Building Docker images..."
        docker compose build --no-cache
        print_info "Images built successfully!"
        ;;

    logs)
        SERVICE=${2:-}
        if [ -z "$SERVICE" ]; then
            docker compose logs -f
        else
            docker compose logs -f "$SERVICE"
        fi
        ;;

    ps)
        docker compose ps
        ;;

    exec)
        SERVICE=${2:-daily-news}
        EXEC_CMD=${3:-bash}
        docker compose exec "$SERVICE" "$EXEC_CMD"
        ;;

    test)
        print_info "Running daily news task once..."
        docker compose exec daily-news python -m app.main --run-once
        ;;

    clean)
        print_warn "This will remove all containers, volumes, and images!"
        read -p "Are you sure? (yes/no): " CONFIRM
        if [ "$CONFIRM" = "yes" ]; then
            print_info "Cleaning up..."
            docker compose down -v
            docker compose down --rmi all
            print_info "Cleanup completed!"
        else
            print_info "Cleanup cancelled."
        fi
        ;;

    help|--help|-h)
        echo "AI Tools Docker Deployment Script"
        echo ""
        echo "Usage: $0 [COMMAND] [OPTIONS]"
        echo ""
        echo "Commands:"
        echo "  up          Start all services (default)"
        echo "  down        Stop all services"
        echo "  restart     Restart all services"
        echo "  build       Rebuild Docker images"
        echo "  logs [svc]  Show logs (optionally for specific service)"
        echo "  ps          Show running containers"
        echo "  exec [svc]  Execute command in container (default: daily-news bash)"
        echo "  test        Run daily news task once"
        echo "  clean       Remove all containers, volumes, and images"
        echo "  help        Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                    # Start services"
        echo "  $0 up                 # Start services"
        echo "  $0 down               # Stop services"
        echo "  $0 logs               # View all logs"
        echo "  $0 logs daily-news    # View daily-news logs"
        echo "  $0 test               # Test daily news"
        echo ""
        ;;

    *)
        print_error "Unknown command: $COMMAND"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
