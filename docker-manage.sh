#!/bin/bash
# Docker management script for ADHD Task Manager

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to start services
start_services() {
    print_status "Starting ADHD Task Manager services..."
    docker-compose up -d
    print_success "Services started successfully!"
    
    print_status "Waiting for MySQL to be ready..."
    sleep 10
    
    print_status "Checking MySQL health..."
    docker-compose exec mysql mysqladmin ping -h localhost -u root -prootpassword
    print_success "MySQL is ready!"
}

# Function to stop services
stop_services() {
    print_status "Stopping ADHD Task Manager services..."
    docker-compose down
    print_success "Services stopped successfully!"
}

# Function to restart services
restart_services() {
    print_status "Restarting ADHD Task Manager services..."
    docker-compose down
    docker-compose up -d
    print_success "Services restarted successfully!"
}

# Function to show logs
show_logs() {
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$1"
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Check if MySQL is ready
    if ! docker-compose exec mysql mysqladmin ping -h localhost -u root -prootpassword > /dev/null 2>&1; then
        print_error "MySQL is not ready. Please start services first."
        exit 1
    fi
    
    # Run migrations
    ENVIRONMENT=local alembic upgrade head
    print_success "Database migrations completed!"
}

# Function to connect to MySQL
connect_mysql() {
    print_status "Connecting to MySQL..."
    docker-compose exec mysql mysql -u adhd_tasksmanager -p"TaskManager2024!" adhd_tasks_dev
}

# Function to test database connection
test_connection() {
    print_status "Testing database connection..."
    python test_mysql.py
}

# Function to show status
show_status() {
    print_status "ADHD Task Manager Services Status:"
    docker-compose ps
}

# Function to clean up
cleanup() {
    print_warning "This will remove ALL Docker containers, networks, and volumes for this project."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker-compose rm -f
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to show help
show_help() {
    echo "ADHD Task Manager - Docker Management Script"
    echo
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  start         Start all services"
    echo "  stop          Stop all services"
    echo "  restart       Restart all services"
    echo "  status        Show services status"
    echo "  logs [service] Show logs (optionally for specific service)"
    echo "  migrate       Run database migrations"
    echo "  mysql         Connect to MySQL database"
    echo "  test          Test database connection"
    echo "  cleanup       Remove all containers and volumes"
    echo "  help          Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs mysql"
    echo "  $0 migrate"
}

# Main script logic
check_docker

case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    migrate)
        run_migrations
        ;;
    mysql)
        connect_mysql
        ;;
    test)
        test_connection
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
