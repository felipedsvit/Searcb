#!/bin/bash

# Startup script for SEARCB Backend
# This script handles application startup, migrations, and health checks

set -e

# Configuration
APP_DIR="/app"
VENV_DIR="$APP_DIR/venv"
TIMEOUT=300  # 5 minutes timeout for startup
HEALTH_CHECK_INTERVAL=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Function to check if a service is ready
wait_for_service() {
    local service_name=$1
    local check_command=$2
    local timeout=$3
    
    log "Waiting for $service_name to be ready..."
    
    local count=0
    while [ $count -lt $timeout ]; do
        if eval "$check_command" > /dev/null 2>&1; then
            log "$service_name is ready!"
            return 0
        fi
        
        sleep 1
        count=$((count + 1))
        
        if [ $((count % 10)) -eq 0 ]; then
            info "Still waiting for $service_name... (${count}s)"
        fi
    done
    
    error "Timeout waiting for $service_name"
    return 1
}

# Function to check database connection
check_database() {
    python -c "
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    connection = engine.connect()
    connection.close()
    print('Database connection successful')
except OperationalError as e:
    print(f'Database connection failed: {e}')
    exit(1)
except Exception as e:
    print(f'Database check failed: {e}')
    exit(1)
"
}

# Function to check Redis connection
check_redis() {
    python -c "
import os
import redis
try:
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    r = redis.from_url(redis_url)
    r.ping()
    print('Redis connection successful')
except Exception as e:
    print(f'Redis connection failed: {e}')
    exit(1)
"
}

# Function to run database migrations
run_migrations() {
    log "Running database migrations..."
    
    if alembic upgrade head; then
        log "Database migrations completed successfully"
    else
        error "Database migrations failed"
        return 1
    fi
}

# Function to create admin user if not exists
create_admin_user() {
    log "Checking for admin user..."
    
    python -c "
import os
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.usuario import Usuario
from app.services.usuario_service import UsuarioService
from app.schemas.usuario import UsuarioCreate
from app.core.database import SessionLocal

async def create_admin_if_not_exists():
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(Usuario).filter(Usuario.username == 'admin').first()
        if admin:
            print('Admin user already exists')
            return
        
        # Create admin user
        usuario_service = UsuarioService(db)
        admin_data = UsuarioCreate(
            username='admin',
            email='admin@searcb.gov.br',
            nome_completo='Administrador do Sistema',
            senha='AdminSEARCB123!',
            confirmar_senha='AdminSEARCB123!',
            is_admin=True
        )
        
        await usuario_service.create_usuario(admin_data)
        print('Admin user created successfully')
        
    except Exception as e:
        print(f'Error creating admin user: {e}')
    finally:
        db.close()

# Run the function
asyncio.run(create_admin_if_not_exists())
"
}

# Function to warm up the application
warm_up_application() {
    log "Warming up application..."
    
    # Import heavy modules to pre-load them
    python -c "
import asyncio
from app.main import app
from app.core.database import SessionLocal
from app.core.cache import redis_client
from app.services.pncp_service import pncp_service

# Test basic functionality
print('Application modules loaded successfully')
"
}

# Function to start the application
start_application() {
    log "Starting SEARCB Backend application..."
    
    # Determine the command based on environment
    if [ "${ENVIRONMENT:-}" = "production" ]; then
        # Production mode with Gunicorn
        exec gunicorn app.main:app \
            --bind 0.0.0.0:8000 \
            --workers 4 \
            --worker-class uvicorn.workers.UvicornWorker \
            --worker-connections 1000 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --timeout 30 \
            --keepalive 2 \
            --preload \
            --access-logfile /app/logs/access.log \
            --error-logfile /app/logs/error.log \
            --log-level info
    else
        # Development mode with Uvicorn
        exec uvicorn app.main:app \
            --host 0.0.0.0 \
            --port 8000 \
            --log-level info
    fi
}

# Main startup sequence
main() {
    log "Starting SEARCB Backend startup sequence..."
    
    # Change to application directory
    cd "$APP_DIR"
    
    # Wait for external services
    wait_for_service "Database" "check_database" 60
    wait_for_service "Redis" "check_redis" 30
    
    # Run database migrations
    run_migrations
    
    # Create admin user if needed
    create_admin_user
    
    # Warm up application
    warm_up_application
    
    # Start application
    start_application
}

# Handle script arguments
case "${1:-}" in
    "migrate")
        log "Running migrations only..."
        cd "$APP_DIR"
        run_migrations
        ;;
    "admin")
        log "Creating admin user only..."
        cd "$APP_DIR"
        create_admin_user
        ;;
    "check")
        log "Running health checks only..."
        cd "$APP_DIR"
        check_database
        check_redis
        log "All health checks passed!"
        ;;
    *)
        # Default: full startup
        main
        ;;
esac
