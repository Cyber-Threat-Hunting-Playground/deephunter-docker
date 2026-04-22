#!/bin/bash
# DeepHunter Uninstallation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}==================================="
echo "DeepHunter Uninstallation Script"
echo -e "===================================${NC}"
echo ""
echo -e "${YELLOW}WARNING: This will permanently remove all DeepHunter containers, images, volumes, and network.${NC}"
echo -e "${YELLOW}Any un-backed up data will be lost.${NC}"
echo ""

read -p "Are you sure you want to proceed? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Uninstallation cancelled.${NC}"
    exit 0
fi

echo -e "${BLUE}Stopping and removing containers...${NC}"
docker compose down -v || true

echo -e "${BLUE}Removing Docker images...${NC}"
docker rmi deephunter:latest deephunter:2.5 || true

echo -e "${BLUE}Removing dangling images (optional but recommended)...${NC}"
docker image prune -f || true

echo -e "${BLUE}Removing data directories...${NC}"
sudo rm -rf data/mariadb/* data/redis/* data/logs/* data/backups/* || true

echo -e "${GREEN}==================================="
echo "Uninstallation complete!"
echo -e "===================================${NC}"