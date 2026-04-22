#!/bin/bash
# Quick diagnostic script for troubleshooting

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

OUTPUT_FILE="deephunter-diagnostics-$(date +%Y%m%d-%H%M%S).txt"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DeepHunter Diagnostic Tool${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Collecting diagnostic information..."
echo "Output file: $OUTPUT_FILE"
echo ""

{
    echo "=========================================="
    echo "DeepHunter Diagnostics"
    echo "Generated: $(date)"
    echo "=========================================="
    echo ""
    
    echo "=========================================="
    echo "System Information"
    echo "=========================================="
    uname -a
    echo ""
    echo "CPU:"
    lscpu | grep "Model name" || echo "N/A"
    echo "CPU Cores: $(nproc)"
    echo ""
    echo "Memory:"
    free -h
    echo ""
    echo "Disk:"
    df -h .
    echo ""
    
    echo "=========================================="
    echo "Docker Information"
    echo "=========================================="
    docker version 2>&1 || echo "Docker not available"
    echo ""
    docker-compose version 2>&1 || echo "Docker Compose not available"
    echo ""
    
    echo "=========================================="
    echo "Container Status"
    echo "=========================================="
    docker ps -a --filter "name=deephunter" 2>&1 || echo "No containers found"
    echo ""
    
    echo "=========================================="
    echo "Container Health"
    echo "=========================================="
    for container in deephunter-app deephunter-mariadb deephunter-redis; do
        echo "--- $container ---"
        docker inspect $container --format='Status: {{.State.Status}}' 2>&1 || echo "Container not found"
        docker inspect $container --format='Health: {{.State.Health.Status}}' 2>&1 || echo "No health check"
        echo ""
    done
    
    echo "=========================================="
    echo "Network Configuration"
    echo "=========================================="
    docker network ls 2>&1 || echo "Unable to list networks"
    echo ""
    docker network inspect deephunter-docker_backend 2>&1 || echo "Network not found"
    echo ""
    
    echo "=========================================="
    echo "Volume Information"
    echo "=========================================="
    docker volume ls --filter "name=deephunter" 2>&1 || echo "No volumes found"
    echo ""
    ls -lah data/ 2>&1 || echo "Data directory not found"
    echo ""
    
    echo "=========================================="
    echo "Configuration Files"
    echo "=========================================="
    echo "--- .env ---"
    [ -f .env ] && echo "File exists" || echo "File not found"
    echo ""
    echo "--- data/settings.py ---"
    [ -f data/settings.py ] && echo "File exists" || echo "File not found"
    echo ""
    echo "--- docker-compose.yml ---"
    docker-compose config --quiet 2>&1 && echo "Valid" || echo "Invalid"
    echo ""
    
    echo "=========================================="
    echo "Recent Logs (Last 50 lines)"
    echo "=========================================="
    echo ""
    echo "--- Application Logs ---"
    docker logs deephunter-app --tail 50 2>&1 || echo "Unable to get logs"
    echo ""
    echo "--- Database Logs ---"
    docker logs deephunter-mariadb --tail 30 2>&1 || echo "Unable to get logs"
    echo ""
    echo "--- Redis Logs ---"
    docker logs deephunter-redis --tail 20 2>&1 || echo "Unable to get logs"
    echo ""
    
    echo "=========================================="
    echo "Database Connectivity"
    echo "=========================================="
    docker exec deephunter-mariadb mysqladmin ping 2>&1 || echo "Unable to ping database"
    echo ""
    
    echo "=========================================="
    echo "Redis Connectivity"
    echo "=========================================="
    docker exec deephunter-redis redis-cli PING 2>&1 || echo "Unable to ping Redis"
    echo ""
    
    echo "=========================================="
    echo "Port Bindings"
    echo "=========================================="
    docker ps --filter "name=deephunter" --format "table {{.Names}}\t{{.Ports}}" 2>&1 || echo "No containers"
    echo ""
    netstat -tlnp 2>/dev/null | grep -E ":(9000|3306|6379)" || ss -tlnp | grep -E ":(9000|3306|6379)" || echo "Unable to check ports"
    echo ""
    
    echo "=========================================="
    echo "Resource Usage"
    echo "=========================================="
    docker stats --no-stream 2>&1 || echo "Unable to get stats"
    echo ""
    
    echo "=========================================="
    echo "Environment Variables"
    echo "=========================================="
    if [ -f .env ]; then
        echo "Environment file exists"
        echo "Variables (sanitized):"
        grep -v "PASSWORD" .env | grep -v "SECRET" || echo "Unable to read .env"
    else
        echo ".env file not found"
    fi
    echo ""
    
    echo "=========================================="
    echo "End of Diagnostics"
    echo "=========================================="
    
} > "$OUTPUT_FILE" 2>&1

echo -e "${GREEN}✓ Diagnostics collected${NC}"
echo ""
echo -e "${BLUE}Report saved to: ${GREEN}$OUTPUT_FILE${NC}"
echo ""
echo "You can share this file for troubleshooting."
echo "Note: Sensitive information (passwords) has been excluded."
echo ""
