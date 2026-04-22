#!/bin/bash
# Performance monitoring script for DeepHunter

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

INTERVAL="${1:-5}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DeepHunter Performance Monitor${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Refresh interval: ${INTERVAL}s${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

while true; do
    clear
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}DeepHunter Performance - $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Container stats
    echo -e "${GREEN}Container Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" \
        deephunter-app deephunter-mariadb deephunter-redis 2>/dev/null || echo "Containers not running"
    
    echo ""
    echo -e "${GREEN}Container Health:${NC}"
    docker ps --filter "name=deephunter" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null
    
    echo ""
    echo -e "${GREEN}System Resources:${NC}"
    echo -n "CPU Load: "
    uptime | awk -F'load average:' '{print $2}'
    echo -n "Memory: "
    free -h | awk '/^Mem:/ {printf "%s used / %s total (%.1f%%)\n", $3, $2, ($3/$2)*100}'
    echo -n "Disk: "
    df -h . | awk 'NR==2 {printf "%s used / %s total (%s)\n", $3, $2, $5}'
    
    echo ""
    echo -e "${GREEN}Database Connections:${NC}"
    docker exec deephunter-mariadb mysql -u root -p"${MARIADB_ROOT_PASSWORD:-password}" \
        -e "SHOW STATUS LIKE 'Threads_connected';" 2>/dev/null | tail -1 || echo "Unable to connect"
    
    echo ""
    echo -e "${GREEN}Redis Memory:${NC}"
    docker exec deephunter-redis redis-cli INFO memory 2>/dev/null | grep "used_memory_human:" || echo "Unable to connect"
    
    echo ""
    echo -e "${YELLOW}Refreshing in ${INTERVAL}s... (Ctrl+C to stop)${NC}"
    
    sleep "$INTERVAL"
done
