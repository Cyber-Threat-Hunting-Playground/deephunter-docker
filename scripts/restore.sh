#!/bin/bash
# Restore script for DeepHunter Docker deployment

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BACKUP_FILE="${1}"
RESTORE_DIR="/tmp/deephunter_restore_$$"

# Container names
DB_CONTAINER="deephunter-mariadb"
APP_CONTAINER="deephunter-app"

echo -e "${BLUE}==================================="
echo "DeepHunter Restore Script"
echo -e "===================================${NC}"
echo ""

# Check if backup file is provided
if [ -z "${BACKUP_FILE}" ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo "Usage: $0 <backup_file.tar.gz>"
    echo "   or: make restore BACKUP_FILE=path/to/backup.tar.gz"
    exit 1
fi

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}Error: Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

echo "Backup file: ${BACKUP_FILE}"
echo ""

# Warning
echo -e "${YELLOW}WARNING: This will overwrite existing data!${NC}"
read -p "Are you sure you want to continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Restore cancelled.${NC}"
    exit 0
fi

# Check if containers are running
if ! docker ps | grep -q "${DB_CONTAINER}"; then
    echo -e "${RED}Error: Database container is not running${NC}"
    echo "Please start the containers first: make up"
    exit 1
fi

# Create restore directory
mkdir -p "${RESTORE_DIR}"

echo -e "${BLUE}Step 1/4: Extracting backup...${NC}"
tar -xzf "${BACKUP_FILE}" -C "${RESTORE_DIR}"
BACKUP_NAME=$(ls "${RESTORE_DIR}")
echo -e "${GREEN}✓ Extraction completed${NC}"

echo -e "${BLUE}Step 2/4: Stopping application...${NC}"
docker-compose stop deephunter
echo -e "${GREEN}✓ Application stopped${NC}"

echo -e "${BLUE}Step 3/4: Restoring database...${NC}"
# Restore database
if docker exec -i "${DB_CONTAINER}" mariadb \
    -u root -p"${MARIADB_ROOT_PASSWORD:-password}" \
    < "${RESTORE_DIR}/${BACKUP_NAME}/database.sql"; then
    echo -e "${GREEN}✓ Database restore completed${NC}"
else
    echo -e "${RED}✗ Database restore failed${NC}"
    docker-compose start deephunter
    rm -rf "${RESTORE_DIR}"
    exit 1
fi

echo -e "${BLUE}Step 4/4: Restoring configuration...${NC}"
# Restore settings (optional - backup first)
if [ -f "${RESTORE_DIR}/${BACKUP_NAME}/settings.py" ]; then
    cp ./data/settings.py ./data/settings.py.bak 2>/dev/null || true
    cp "${RESTORE_DIR}/${BACKUP_NAME}/settings.py" ./data/settings.py
    echo -e "${GREEN}✓ Settings restored (backup saved as settings.py.bak)${NC}"
fi

# Cleanup
rm -rf "${RESTORE_DIR}"

# Restart application
echo -e "${BLUE}Restarting application...${NC}"
docker-compose start deephunter

echo ""
echo -e "${GREEN}==================================="
echo "Restore completed successfully!"
echo -e "===================================${NC}"
echo ""
echo -e "${YELLOW}Please verify the application is working correctly.${NC}"
echo "Access DeepHunter at: https://localhost:9000"
echo ""#!/bin/bash
# Restore script for DeepHunter Docker deployment

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BACKUP_FILE="${1}"
RESTORE_DIR="/tmp/deephunter_restore_$$"

# Container names
DB_CONTAINER="deephunter-mariadb"
APP_CONTAINER="deephunter-app"

echo -e "${BLUE}==================================="
echo "DeepHunter Restore Script"
echo -e "===================================${NC}"
echo ""

# Check if backup file is provided
if [ -z "${BACKUP_FILE}" ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo "Usage: $0 <backup_file.tar.gz>"
    echo "   or: make restore BACKUP_FILE=path/to/backup.tar.gz"
    exit 1
fi

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}Error: Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

echo "Backup file: ${BACKUP_FILE}"
echo ""

# Warning
echo -e "${YELLOW}WARNING: This will overwrite existing data!${NC}"
read -p "Are you sure you want to continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Restore cancelled.${NC}"
    exit 0
fi

# Check if containers are running
if ! docker ps | grep -q "${DB_CONTAINER}"; then
    echo -e "${RED}Error: Database container is not running${NC}"
    echo "Please start the containers first: make up"
    exit 1
fi

# Create restore directory
mkdir -p "${RESTORE_DIR}"

echo -e "${BLUE}Step 1/4: Extracting backup...${NC}"
tar -xzf "${BACKUP_FILE}" -C "${RESTORE_DIR}"
BACKUP_NAME=$(ls "${RESTORE_DIR}")
echo -e "${GREEN}✓ Extraction completed${NC}"

echo -e "${BLUE}Step 2/4: Stopping application...${NC}"
docker-compose stop deephunter
echo -e "${GREEN}✓ Application stopped${NC}"

echo -e "${BLUE}Step 3/4: Restoring database...${NC}"
# Restore database
docker exec -i "${DB_CONTAINER}" mariadb \
    -u root -p"${MARIADB_ROOT_PASSWORD:-password}" \
    < "${RESTORE_DIR}/${BACKUP_NAME}/database.sql"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database restore completed${NC}"
else
    echo -e "${RED}✗ Database restore failed${NC}"
    docker-compose start deephunter
    rm -rf "${RESTORE_DIR}"
    exit 1
fi

echo -e "${BLUE}Step 4/4: Restoring configuration...${NC}"
# Restore settings (optional - backup first)
if [ -f "${RESTORE_DIR}/${BACKUP_NAME}/settings.py" ]; then
    cp ./data/settings.py ./data/settings.py.bak 2>/dev/null || true
    cp "${RESTORE_DIR}/${BACKUP_NAME}/settings.py" ./data/settings.py
    echo -e "${GREEN}✓ Settings restored (backup saved as settings.py.bak)${NC}"
fi

# Cleanup
rm -rf "${RESTORE_DIR}"

# Restart application
echo -e "${BLUE}Restarting application...${NC}"
docker-compose start deephunter

echo ""
echo -e "${GREEN}==================================="
echo "Restore completed successfully!"
echo -e "===================================${NC}"
echo ""
echo -e "${YELLOW}Please verify the application is working correctly.${NC}"
echo "Access DeepHunter at: https://localhost:9000"
echo ""
