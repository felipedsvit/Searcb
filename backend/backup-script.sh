#!/bin/bash

# Backup script for SEARCB Production Environment
# This script creates backups of the PostgreSQL database and important files

set -e

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7
DB_HOST="db"
DB_NAME="${DB_NAME:-searcb_db}"
DB_USER="${DB_USER:-searcb}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

log "Starting backup process..."

# Database backup
log "Creating database backup..."
DB_BACKUP_FILE="$BACKUP_DIR/searcb_db_backup_$DATE.sql"

if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$DB_BACKUP_FILE"; then
    log "Database backup completed: $DB_BACKUP_FILE"
    
    # Compress the database backup
    if gzip "$DB_BACKUP_FILE"; then
        log "Database backup compressed: ${DB_BACKUP_FILE}.gz"
        DB_BACKUP_FILE="${DB_BACKUP_FILE}.gz"
    else
        warning "Failed to compress database backup"
    fi
else
    error "Database backup failed"
    exit 1
fi

# Application logs backup
log "Creating application logs backup..."
LOGS_BACKUP_FILE="$BACKUP_DIR/searcb_logs_backup_$DATE.tar.gz"

if [ -d "/app/logs" ]; then
    if tar -czf "$LOGS_BACKUP_FILE" -C /app logs/; then
        log "Application logs backup completed: $LOGS_BACKUP_FILE"
    else
        warning "Failed to backup application logs"
    fi
else
    warning "Application logs directory not found"
fi

# Create backup manifest
log "Creating backup manifest..."
MANIFEST_FILE="$BACKUP_DIR/backup_manifest_$DATE.json"

cat > "$MANIFEST_FILE" << EOF
{
    "backup_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_type": "full",
    "database": {
        "host": "$DB_HOST",
        "database": "$DB_NAME",
        "user": "$DB_USER",
        "backup_file": "$(basename "$DB_BACKUP_FILE")",
        "size_bytes": $(stat -c%s "$DB_BACKUP_FILE" 2>/dev/null || echo 0)
    },
    "logs": {
        "backup_file": "$(basename "$LOGS_BACKUP_FILE")",
        "size_bytes": $(stat -c%s "$LOGS_BACKUP_FILE" 2>/dev/null || echo 0)
    },
    "retention_days": $RETENTION_DAYS
}
EOF

log "Backup manifest created: $MANIFEST_FILE"

# Clean up old backups
log "Cleaning up old backups (older than $RETENTION_DAYS days)..."

find "$BACKUP_DIR" -name "searcb_db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "searcb_logs_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "backup_manifest_*.json" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

log "Old backups cleaned up"

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Total backup directory size: $TOTAL_SIZE"

# List current backups
log "Current backups:"
ls -la "$BACKUP_DIR"/*_$DATE* 2>/dev/null || true

# Verify backup integrity
log "Verifying backup integrity..."

# Verify database backup
if [ -f "$DB_BACKUP_FILE" ]; then
    if file "$DB_BACKUP_FILE" | grep -q "gzip compressed"; then
        log "Database backup integrity verified (gzip compressed)"
    else
        error "Database backup integrity check failed"
        exit 1
    fi
else
    error "Database backup file not found"
    exit 1
fi

# Send backup notification (if configured)
if [ -n "${WEBHOOK_URL:-}" ]; then
    log "Sending backup notification..."
    
    NOTIFICATION_PAYLOAD=$(cat << EOF
{
    "text": "✅ SEARCB Backup Completed",
    "attachments": [
        {
            "color": "good",
            "fields": [
                {
                    "title": "Date",
                    "value": "$(date)",
                    "short": true
                },
                {
                    "title": "Database Size",
                    "value": "$(stat -c%s "$DB_BACKUP_FILE" 2>/dev/null | numfmt --to=iec || echo 'Unknown')",
                    "short": true
                },
                {
                    "title": "Total Backup Size",
                    "value": "$TOTAL_SIZE",
                    "short": true
                }
            ]
        }
    ]
}
EOF
)

    if curl -X POST -H 'Content-type: application/json' \
        --data "$NOTIFICATION_PAYLOAD" \
        "$WEBHOOK_URL" > /dev/null 2>&1; then
        log "Backup notification sent"
    else
        warning "Failed to send backup notification"
    fi
fi

log "Backup process completed successfully!"

# Exit with success
exit 0
