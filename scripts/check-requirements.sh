#!/bin/bash
# System requirements check script

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DeepHunter System Requirements Check${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Check Docker
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    echo -e "${GREEN}✓ Found version $DOCKER_VERSION${NC}"
    
    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        echo -e "  ${GREEN}✓ Docker daemon is running${NC}"
    else
        echo -e "  ${RED}✗ Docker daemon is not running${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${RED}✗ Not installed${NC}"
    echo -e "  Install: https://docs.docker.com/engine/install/"
    ((ERRORS++))
fi

# Check Docker Compose v2 (CLI plugin)
COMPOSE_MIN_MAJOR=2
COMPOSE_MIN_MINOR=17
echo -n "Checking Docker Compose v2 plugin... "
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null | sed 's/^v//')
    COMPOSE_MAJOR=$(echo "$COMPOSE_VERSION" | cut -d. -f1)
    COMPOSE_MINOR=$(echo "$COMPOSE_VERSION" | cut -d. -f2)
    if [ "$COMPOSE_MAJOR" -gt "$COMPOSE_MIN_MAJOR" ] 2>/dev/null || \
       { [ "$COMPOSE_MAJOR" -eq "$COMPOSE_MIN_MAJOR" ] && [ "$COMPOSE_MINOR" -ge "$COMPOSE_MIN_MINOR" ]; } 2>/dev/null; then
        echo -e "${GREEN}✓ Found version $COMPOSE_VERSION${NC}"
    else
        echo -e "${YELLOW}⚠ Found version $COMPOSE_VERSION (v${COMPOSE_MIN_MAJOR}.${COMPOSE_MIN_MINOR}+ recommended)${NC}"
        ((WARNINGS++))
    fi
elif command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Legacy docker-compose (v1) detected — not supported${NC}"
    echo -e "  This project requires Docker Compose v2 (the 'docker compose' CLI plugin)."
    echo -e "  The standalone docker-compose v1 does not honour start_period in health checks."
    echo -e "  Install: ${BLUE}sudo apt-get install docker-compose-plugin${NC}  (Debian/Ubuntu)"
    echo -e "           ${BLUE}sudo dnf install docker-compose-plugin${NC}      (Fedora/RHEL)"
    echo -e "  Docs:    https://docs.docker.com/compose/install/linux/"
    ((ERRORS++))
else
    echo -e "${RED}✗ Not installed${NC}"
    echo -e "  Install: ${BLUE}sudo apt-get install docker-compose-plugin${NC}  (Debian/Ubuntu)"
    echo -e "           ${BLUE}sudo dnf install docker-compose-plugin${NC}      (Fedora/RHEL)"
    echo -e "  Docs:    https://docs.docker.com/compose/install/linux/"
    ((ERRORS++))
fi

# Check available disk space
echo -n "Checking disk space... "
AVAILABLE_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE_GB" -ge 20 ]; then
    echo -e "${GREEN}✓ ${AVAILABLE_GB}GB available${NC}"
else
    echo -e "${YELLOW}⚠ Only ${AVAILABLE_GB}GB available (20GB recommended)${NC}"
    ((WARNINGS++))
fi

# Check available memory
echo -n "Checking memory... "
TOTAL_MEM_MB=$(free -m | awk '/^Mem:/{print $2}')
TOTAL_MEM_GB=$((TOTAL_MEM_MB / 1024))
if [ "$TOTAL_MEM_GB" -ge 8 ]; then
    echo -e "${GREEN}✓ ${TOTAL_MEM_GB}GB total${NC}"
elif [ "$TOTAL_MEM_GB" -ge 4 ]; then
    echo -e "${YELLOW}⚠ ${TOTAL_MEM_GB}GB total (8GB recommended)${NC}"
    ((WARNINGS++))
else
    echo -e "${RED}✗ Only ${TOTAL_MEM_GB}GB total (minimum 4GB required)${NC}"
    ((ERRORS++))
fi

# Check CPU cores
echo -n "Checking CPU... "
CPU_CORES=$(nproc)
if [ "$CPU_CORES" -ge 2 ]; then
    echo -e "${GREEN}✓ ${CPU_CORES} cores${NC}"
else
    echo -e "${YELLOW}⚠ Only ${CPU_CORES} core (2+ recommended)${NC}"
    ((WARNINGS++))
fi

# Check for required files
echo ""
echo "Checking required files..."
REQUIRED_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "build.sh"
    "data/settings.py"
    "Makefile"
)

for file in "${REQUIRED_FILES[@]}"; do
    echo -n "  $file... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ Missing${NC}"
        ((ERRORS++))
    fi
done

# Check if .env exists
echo -n "  .env... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ Not found (will use defaults)${NC}"
    echo -e "    Run: ${BLUE}cp .env.example .env${NC}"
    ((WARNINGS++))
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo "Summary:"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! System is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Configure environment: cp .env.example .env && nano .env"
    echo "  2. Start deployment: make install"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) - System should work but not optimal${NC}"
    echo ""
    echo "You can proceed, but consider addressing warnings for better performance."
else
    echo -e "${RED}✗ $ERRORS error(s) found - Please fix before proceeding${NC}"
    echo -e "${YELLOW}⚠ $WARNINGS warning(s)${NC}"
    exit 1
fi
echo -e "${BLUE}========================================${NC}"
