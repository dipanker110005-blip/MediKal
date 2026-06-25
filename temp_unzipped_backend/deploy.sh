#!/bin/bash

# MediKal Backend - Quick Deployment Script
# Usage: ./deploy.sh [local|production]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Deployment environment
DEPLOY_ENV=${1:-local}

echo -e "${YELLOW}=== MediKal Backend Deployment ===${NC}"
echo "Environment: $DEPLOY_ENV"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check Docker
print_info "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker first."
    exit 1
fi
print_status "Docker installed: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi
print_status "Docker Compose installed: $(docker-compose --version)"

echo ""

# Navigate to backend directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the backend directory."
    exit 1
fi

print_status "Project directory confirmed"

# Select environment file
if [ "$DEPLOY_ENV" = "production" ]; then
    ENV_FILE=".env.production"
    print_info "Using production environment"
else
    ENV_FILE=".env"
    print_info "Using development environment"
fi

if [ ! -f "$ENV_FILE" ]; then
    print_error "$ENV_FILE not found"
    exit 1
fi

print_status "Environment file: $ENV_FILE"

echo ""
print_info "Building Docker images..."
docker-compose build

echo ""
print_info "Starting services..."
docker-compose up -d

echo ""
print_status "Services started!"

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 5

# Check service status
echo ""
docker-compose ps

# Run migrations
echo ""
print_info "Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
echo ""
print_info "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo ""
print_status "Deployment complete!"

echo ""
echo -e "${GREEN}================================${NC}"
echo "Deployment Summary:"
echo "================================"
echo "Environment: $DEPLOY_ENV"
echo "Backend URL: http://localhost:8000"
echo "Database: PostgreSQL (localhost:5432)"
echo ""
echo "Next steps:"
echo "1. Create admin user: docker-compose exec web python manage.py createsuperuser"
echo "2. Visit http://localhost:8000/api/"
echo "3. View logs: docker-compose logs -f web"
echo ""
echo "To stop services: docker-compose down"
echo -e "${GREEN}================================${NC}"
