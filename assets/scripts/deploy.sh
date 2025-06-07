#!/bin/bash
# Deployment script for Yōsai Intel Dashboard

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        log_warning ".env file not found. Creating from template..."
        if [ -f .env.template ]; then
            cp .env.template .env
            log_info "Please edit .env file with your configuration before continuing."
            log_info "Press any key to continue when ready..."
            read -n 1 -s
        else
            log_error ".env.template file not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Check Docker installation
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    log_success "Docker and Docker Compose are installed."
}

# Build and start services
deploy_production() {
    log_info "Starting production deployment..."
    
    # Build the application
    log_info "Building application image..."
    docker-compose build --no-cache yosai-app
    
    # Start all services
    log_info "Starting all services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_health
    
    log_success "Production deployment completed!"
    log_info "Application available at: http://localhost:8050"
}

# Deploy development environment
deploy_development() {
    log_info "Starting development deployment..."
    
    # Build and start development services
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
    
    log_success "Development deployment completed!"
    log_info "Application available at: http://localhost:8050"
    log_info "Use 'docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f yosai-app' to follow logs"
}

# Deploy with monitoring
deploy_with_monitoring() {
    log_info "Starting deployment with monitoring..."
    
    # Start all services including monitoring
    docker-compose --profile monitoring up -d --build
    
    log_success "Deployment with monitoring completed!"
    log_info "Application: http://localhost:8050"
    log_info "Grafana: http://localhost:3000 (admin/admin)"
    log_info "Prometheus: http://localhost:9090"
}

# Check service health
check_health() {
    log_info "Checking service health..."
    
    # Check if main app is responding
    for i in {1..30}; do
        if curl -f http://localhost:8050/ >/dev/null 2>&1; then
            log_success "Application is healthy and responding"
            return 0
        fi
        log_info "Waiting for application to start... ($i/30)"
        sleep 2
    done
    
    log_error "Application failed to start properly"
    log_info "Checking logs..."
    docker-compose logs yosai-app
    return 1
}

# Stop all services
stop_services() {
    log_info "Stopping all services..."
    docker-compose down
    log_success "All services stopped."
}

# Clean up everything
cleanup() {
    log_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up..."
        docker-compose down -v --rmi all
        docker system prune -f
        log_success "Cleanup completed."
    else
        log_info "Cleanup cancelled."
    fi
}

# Show logs
show_logs() {
    service=${1:-yosai-app}
    log_info "Showing logs for $service..."
    docker-compose logs -f "$service"
}

# Show status
show_status() {
    log_info "Service status:"
    docker-compose ps
    
    log_info "\nContainer health:"
    docker-compose exec yosai-app curl -f http://localhost:8050/ >/dev/null 2>&1 && \
        log_success "Application: Healthy" || log_error "Application: Unhealthy"
}

# Main menu
show_help() {
    echo "Yōsai Intel Dashboard Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  prod, production     Deploy production environment"
    echo "  dev, development     Deploy development environment"
    echo "  monitor, monitoring  Deploy with monitoring stack"
    echo "  stop                 Stop all services"
    echo "  status               Show service status"
    echo "  logs [service]       Show logs (default: yosai-app)"
    echo "  cleanup              Remove all containers and images"
    echo "  help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 prod              # Deploy production"
    echo "  $0 dev               # Deploy development"
    echo "  $0 logs yosai-db     # Show database logs"
}

# Main script logic
main() {
    case ${1:-help} in
        "prod"|"production")
            check_docker
            check_env_file
            deploy_production
            ;;
        "dev"|"development")
            check_docker
            check_env_file
            deploy_development
            ;;
        "monitor"|"monitoring")
            check_docker
            check_env_file
            deploy_with_monitoring
            ;;
        "stop")
            stop_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"