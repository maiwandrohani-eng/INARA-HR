#!/bin/bash

# Database Backup Script for INARA HRIS
# This script creates automated backups of the PostgreSQL database

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/inara-hris}"
DB_NAME="${POSTGRES_DB:-inara_hris}"
DB_USER="${POSTGRES_USER:-inara_user}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Date format for backup filenames
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/inara_hris_backup_${DATE}.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "Starting database backup at $(date)"
echo "Database: ${DB_NAME}"
echo "Backup file: ${BACKUP_FILE}"

# Create backup
export PGPASSWORD="${POSTGRES_PASSWORD}"
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
    --verbose \
    --clean \
    --if-exists \
    --create \
    --format=custom \
    | gzip > "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "✅ Backup completed successfully: ${BACKUP_FILE}"
    
    # Get backup size
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "Backup size: ${BACKUP_SIZE}"
    
    # Clean up old backups (keep only last N days)
    echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
    find "${BACKUP_DIR}" -name "inara_hris_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
    echo "✅ Old backups cleaned up"
    
    # Optional: Upload to S3 or remote storage
    if [ -n "${BACKUP_S3_BUCKET}" ] && [ -n "${AWS_ACCESS_KEY_ID}" ]; then
        echo "Uploading backup to S3..."
        aws s3 cp "${BACKUP_FILE}" "s3://${BACKUP_S3_BUCKET}/database-backups/inara_hris_backup_${DATE}.sql.gz"
        echo "✅ Backup uploaded to S3"
    fi
else
    echo "❌ Backup failed!"
    exit 1
fi

echo "Backup process completed at $(date)"

