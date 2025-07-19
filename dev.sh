#!/bin/bash

# TreeLine Development Script
# This script sets up and runs the TreeLine AI customer support agent locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file and add your OpenAI API key before running again."
        print_warning "You can get an API key from: https://platform.openai.com/api-keys"
        exit 1
    fi
    
    # Check if OpenAI API key is set
    if grep -q "your_openai_api_key_here" .env; then
        print_warning "Please set your OpenAI API key in the .env file"
        print_warning "Edit .env and replace 'your_openai_api_key_here' with your actual API key"
        exit 1
    fi
    
    print_success ".env file configured"
}

# Function to stop services
stop_services() {
    print_status "Stopping TreeLine services..."
    docker-compose down
    print_success "Services stopped"
}

# Function to start services
start_services() {
    print_status "Starting TreeLine services..."
    
    # Build and start services
    docker-compose up --build -d
    
    print_status "Waiting for services to be ready..."
    
    # Wait for backend to be healthy
    print_status "Waiting for backend service..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Backend service failed to start within 60 seconds"
        docker-compose logs backend
        exit 1
    fi
    
    print_success "All services are running!"
    echo
    print_status "Service URLs:"
    echo "  🌐 Streamlit UI:    http://localhost:8501"
    echo "  🚀 FastAPI Backend: http://localhost:8000"
    echo "  📚 API Docs:        http://localhost:8000/docs"
    echo "  🗄️  PostgreSQL:      localhost:5432"
    echo
    print_status "To view logs: docker-compose logs -f [service_name]"
    print_status "To stop services: docker-compose down"
}

# Function to show logs
show_logs() {
    if [ -z "$1" ]; then
        print_status "Showing logs for all services..."
        docker-compose logs -f
    else
        print_status "Showing logs for $1..."
        docker-compose logs -f "$1"
    fi
}

# Function to show service status
show_status() {
    print_status "Checking service status..."
    echo
    docker-compose ps
    echo
    
    # Check individual service health
    print_status "Health checks:"
    
    # Backend health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "✓ Backend (http://localhost:8000) - Healthy"
    else
        print_warning "✗ Backend (http://localhost:8000) - Not responding"
    fi
    
    # AI Agent health
    if curl -f http://localhost:8001/health >/dev/null 2>&1; then
        print_success "✓ AI Agent (http://localhost:8001) - Healthy"
    else
        print_warning "✗ AI Agent (http://localhost:8001) - Not responding"
    fi
    
    # Streamlit UI
    if curl -f http://localhost:8501 >/dev/null 2>&1; then
        print_success "✓ Streamlit UI (http://localhost:8501) - Healthy"
    else
        print_warning "✗ Streamlit UI (http://localhost:8501) - Not responding"
    fi
    
    # Database
    if docker-compose exec -T postgres pg_isready -U treeline_user -d treeline >/dev/null 2>&1; then
        print_success "✓ PostgreSQL Database - Healthy"
    else
        print_warning "✗ PostgreSQL Database - Not responding"
    fi
}

# Function to open services in browser
open_services() {
    print_status "Opening TreeLine services in browser..."
    
    # Check if services are running first
    if ! curl -f http://localhost:8501 >/dev/null 2>&1; then
        print_warning "Services don't appear to be running. Starting them first..."
        start_services
        sleep 5
    fi
    
    # Open in browser (works on most Linux systems)
    if command_exists xdg-open; then
        xdg-open http://localhost:8501 >/dev/null 2>&1 &
        xdg-open http://localhost:8000/docs >/dev/null 2>&1 &
        print_success "Opened Streamlit UI and API docs in browser"
    elif command_exists open; then
        open http://localhost:8501 >/dev/null 2>&1 &
        open http://localhost:8000/docs >/dev/null 2>&1 &
        print_success "Opened Streamlit UI and API docs in browser"
    else
        print_status "Manual browser access:"
        echo "  🌐 Streamlit UI: http://localhost:8501"
        echo "  📚 API Docs: http://localhost:8000/docs"
    fi
}

# Function to clean up everything
clean_all() {
    print_warning "This will remove all containers, volumes, and images for TreeLine"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up TreeLine resources..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Install dev dependencies if not in container
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -e ".[dev]"
    else
        source venv/bin/activate
    fi
    
    # Run tests
    pytest -v
    
    print_success "Tests completed"
}

# Function to format code
format_code() {
    print_status "Formatting code..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -e ".[dev]"
    else
        source venv/bin/activate
    fi
    
    # Format with black
    black backend/ ai_agent/ ui/
    
    # Lint with ruff
    ruff check backend/ ai_agent/ ui/ --fix
    
    print_success "Code formatting completed"
}

# Main script logic
case "${1:-start}" in
    start)
        check_prerequisites
        check_env_file
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        check_prerequisites
        check_env_file
        start_services
        ;;
    logs)
        show_logs "$2"
        ;;
    test)
        run_tests
        ;;
    format)
        format_code
        ;;
    status)
        show_status
        ;;
    open)
        open_services
        ;;
    clean)
        clean_all
        ;;
    help|--help|-h)
        echo "TreeLine Development Script"
        echo
        echo "Usage: $0 [COMMAND]"
        echo
        echo "Commands:"
        echo "  start     Start all services (default)"
        echo "  stop      Stop all services"
        echo "  restart   Restart all services"
        echo "  status    Show service status and health checks"
        echo "  logs      Show logs for all services"
        echo "  logs [service]  Show logs for specific service"
        echo "  open      Open services in browser"
        echo "  test      Run tests"
        echo "  format    Format code with black and ruff"
        echo "  clean     Clean up all containers and volumes"
        echo "  help      Show this help message"
        echo
        echo "Services: postgres, backend, ai-agent, streamlit-ui"
        echo
        echo "Examples:"
        echo "  $0 start          # Start all services"
        echo "  $0 logs backend   # Show backend logs"
        echo "  $0 status         # Check service health"
        echo "  $0 open           # Open UI and docs in browser"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
