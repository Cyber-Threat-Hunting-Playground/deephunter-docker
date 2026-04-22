#!/bin/bash
# Upgrade script for DeepHunter Docker deployment

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DeepHunter Upgrade Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Pre-upgrade checks
echo -e "${BLUE}Step 1/6: Pre-upgrade checks...${NC}"

if ! docker ps | grep -q "deephunter"; then
    echo -e "${RED}No DeepHunter containers running${NC}"
    exit 1
fi

# Check for uncommitted changes
if [ -d ".git" ]; then
    if ! git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}⚠ You have uncommitted changes${NC}"
        read -p "Continue anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Upgrade cancelled${NC}"
            exit 0
        fi
    fi
fi

echo -e "${GREEN}✓ Pre-checks passed${NC}"
echo ""

# Create backup
echo -e "${BLUE}Step 2/6: Creating backup...${NC}"
chmod +x scripts/backup.sh
./scripts/backup.sh
echo -e "${GREEN}✓ Backup created${NC}"
echo ""

# Pull latest changes
echo -e "${BLUE}Step 3/6: Pulling latest changes...${NC}"
if [ -d ".git" ]; then
    git pull origin main 2>/dev/null || git pull 2>/dev/null || echo "Not a git repository"
else
    echo -e "${YELLOW}Not a git repository, skipping...${NC}"
fi
echo -e "${GREEN}✓ Changes pulled${NC}"
echo ""

# Pull latest images
echo -e "${BLUE}Step 4/6: Pulling latest images...${NC}"
docker-compose pull
echo -e "${GREEN}✓ Images updated${NC}"
echo ""

# Rebuild application
echo -e "${BLUE}Step 5/6: Rebuilding application...${NC}"
./build.sh
echo -e "${GREEN}✓ Application rebuilt${NC}"
echo ""

# Restart services
echo -e "${BLUE}Step 6/6: Restarting services...${NC}"
docker-compose down
docker-compose up -d

# Wait for services to be healthy
echo ""
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check health
MAX_RETRIES=12
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if docker ps --filter "name=deephunter" --filter "health=healthy" | grep -q "deephunter-app"; then
        echo -e "${GREEN}✓ Services are healthy${NC}"
        break
    fi
    RETRY=$((RETRY + 1))
    echo -e "${YELLOW}Waiting... ($RETRY/$MAX_RETRIES)${NC}"
    sleep 5
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Services did not become healthy${NC}"
    echo -e "${YELLOW}Check logs: make logs${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Upgrade completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Access DeepHunter at: https://localhost:9000${NC}"
echo ""
echo -e "${YELLOW}Backup location: ./data/backups/${NC}"
echo -e "${YELLOW}If you encounter issues, restore with:${NC}"
echo -e "${YELLOW}make restore BACKUP_FILE=./data/backups/latest.tar.gz${NC}"
echo ""
