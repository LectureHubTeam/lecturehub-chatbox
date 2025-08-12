#!/bin/bash

# Docker setup script for LectureHub Chatbot
# This script helps manage the PostgreSQL database with pgvector

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
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to start the database
start_db() {
    print_status "Starting PostgreSQL database with pgvector..."
    docker-compose -f docker/docker-compose.yml up -d postgres
    
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Wait for database to be healthy
    for i in {1..30}; do
        if docker-compose -f docker/docker-compose.yml exec postgres pg_isready -U root -d embedding > /dev/null 2>&1; then
            print_success "Database is ready!"
            return 0
        fi
        print_status "Waiting for database... ($i/30)"
        sleep 2
    done
    
    print_error "Database failed to start within 60 seconds"
    return 1
}

# Function to stop the database
stop_db() {
    print_status "Stopping PostgreSQL database..."
    docker-compose -f docker/docker-compose.yml down
    print_success "Database stopped"
}

# Function to restart the database
restart_db() {
    print_status "Restarting PostgreSQL database..."
    docker-compose -f docker/docker-compose.yml restart postgres
    print_success "Database restarted"
}

# Function to check database status
status_db() {
    print_status "Checking database status..."
    if docker-compose -f docker/docker-compose.yml ps postgres | grep -q "Up"; then
        print_success "Database is running"
        
        # Test connection
        if docker-compose -f docker/docker-compose.yml exec postgres pg_isready -U root -d embedding > /dev/null 2>&1; then
            print_success "Database connection is healthy"
        else
            print_warning "Database connection is not healthy"
        fi
    else
        print_warning "Database is not running"
    fi
}

# Function to view database logs
logs_db() {
    print_status "Showing database logs..."
    docker-compose -f docker/docker-compose.yml logs postgres
}

# Function to reset database (remove all data)
reset_db() {
    print_warning "This will remove all database data. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Removing database and all data..."
        docker-compose -f docker/docker-compose.yml down -v
        print_success "Database reset complete"
    else
        print_status "Database reset cancelled"
    fi
}

# Function to test database connection
test_db() {
    print_status "Testing database connection..."
    
    # Test using docker-compose
    if docker-compose -f docker/docker-compose.yml exec postgres psql -U root -d embedding -c "SELECT test_pgvector();" > /dev/null 2>&1; then
        print_success "Database connection test passed"
        print_success "pgvector extension is working"
    else
        print_error "Database connection test failed"
        return 1
    fi
}

# Function to show database info
info_db() {
    print_status "Database information:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: embedding"
    echo "  User: root"
    echo "  Password: root_password"
    echo "  Connection string: postgresql+psycopg://root:root_password@localhost:5432/embedding"
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the PostgreSQL database"
    echo "  stop      Stop the PostgreSQL database"
    echo "  restart   Restart the PostgreSQL database"
    echo "  status    Check database status"
    echo "  logs      View database logs"
    echo "  test      Test database connection"
    echo "  reset     Reset database (remove all data)"
    echo "  info      Show database information"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start the database"
    echo "  $0 test     # Test the connection"
    echo "  $0 status   # Check if database is running"
}

# Main script logic
case "${1:-help}" in
    start)
        check_docker
        start_db
        ;;
    stop)
        check_docker
        stop_db
        ;;
    restart)
        check_docker
        restart_db
        ;;
    status)
        check_docker
        status_db
        ;;
    logs)
        check_docker
        logs_db
        ;;
    test)
        check_docker
        test_db
        ;;
    reset)
        check_docker
        reset_db
        ;;
    info)
        info_db
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
