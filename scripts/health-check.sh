#!/bin/bash
# Health check script for DeepHunter services

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "DeepHunter Health Check"
echo "======================"
echo ""

# Check Redis
echo -n "Redis:      "
if docker exec deephunter-redis redis-cli ping &>/dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Check MariaDB
echo -n "MariaDB:    "
if docker exec deephunter-mariadb healthcheck.sh --connect &>/dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Check DeepHunter App
echo -n "DeepHunter: "
if docker exec deephunter-app curl -f -k https://localhost:443/ &>/dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

echo ""
echo "Container Status:"
docker ps --filter "name=deephunter" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
