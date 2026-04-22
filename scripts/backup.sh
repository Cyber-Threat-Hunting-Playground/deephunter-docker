#!/bin/bash
# Backup script for DeepHunter Docker deployment
# Creates compressed backups of database and critical data

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./data/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="deephunter_backup_${TIMESTAMP}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Container names
DB_CONTAINER="deephunter-mariadb"
APP_CONTAINER="deephunter-app"

echo -e "${BLUE}==================================="
echo "DeepHunter Backup Script"
echo -e "===================================${NC}"
echo ""
echo "Timestamp: ${TIMESTAMP}"
echo "Backup directory: ${BACKUP_DIR}"
echo "Retention: ${RETENTION_DAYS} days"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if containers are running
if ! docker ps | grep -q "${DB_CONTAINER}"; then
    echo -e "${RED}Error: Database container is not running${NC}"
    exit 1
fi

# Create temporary backup directory
TEMP_DIR="${BACKUP_DIR}/${BACKUP_NAME}"
mkdir -p "${TEMP_DIR}"

echo -e "${BLUE}Step 1/4: Backing up MariaDB database...${NC}"
# Backup database
if docker exec "${DB_CONTAINER}" mariadb-dump \
    -u root -p"${MARIADB_ROOT_PASSWORD:-password}" \
    --all-databases \
    --single-transaction \
    --quick \
    --lock-tables=false \
    > "${TEMP_DIR}/database.sql"; then
    echo -e "${GREEN}✓ Database backup completed${NC}"
else
    echo -e "${RED}✗ Database backup failed${NC}"
    rm -rf "${TEMP_DIR}"
    exit 1
fi

echo -e "${BLUE}Step 2/4: Backing up settings and configuration...${NC}"
# Backup settings
cp -r ./data/settings.py "${TEMP_DIR}/" 2>/dev/null || true
cp -r ./patch "${TEMP_DIR}/" 2>/dev/null || true
cp ./docker-compose.yml "${TEMP_DIR}/" 2>/dev/null || true
cp ./.env "${TEMP_DIR}/" 2>/dev/null || true
echo -e "${GREEN}✓ Configuration backup completed${NC}"

echo -e "${BLUE}Step 3/4: Compressing backup...${NC}"
# Create compressed archive
if tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" -C "${BACKUP_DIR}" "${BACKUP_NAME}"; then
    echo -e "${GREEN}✓ Compression completed${NC}"
    # Remove temporary directory
    rm -rf "${TEMP_DIR}"
else
    echo -e "${RED}✗ Compression failed${NC}"
    exit 1
fi

echo -e "${BLUE}Step 4/4: Cleaning old backups...${NC}"
# Remove backups older than retention period
find "${BACKUP_DIR}" -name "deephunter_backup_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete
echo -e "${GREEN}✓ Cleanup completed${NC}"

# Calculate backup size
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)

echo ""
echo -e "${GREEN}==================================="
echo "Backup completed successfully!"
echo -e "===================================${NC}"
echo ""
echo "Backup file: ${BACKUP_NAME}.tar.gz"
echo "Size: ${BACKUP_SIZE}"
echo "Location: ${BACKUP_DIR}"
echo ""
echo -e "${YELLOW}To restore this backup, run:${NC}"
echo "make restore BACKUP_FILE=${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo ""
