#!/bin/bash
# Configuration validator for DeepHunter Docker deployment
# Checks settings.py for Docker compatibility

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DeepHunter Configuration Validator${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

SETTINGS_FILE="data/settings.py"

if [ ! -f "$SETTINGS_FILE" ]; then
    echo -e "${RED}✗ $SETTINGS_FILE not found!${NC}"
    exit 1
fi

echo "Checking $SETTINGS_FILE..."
echo ""

# Check database host
echo -n "Database HOST... "
DB_HOST=$(grep -A 10 "DATABASES = {" "$SETTINGS_FILE" | grep "'HOST':" | head -1 | sed "s/.*'HOST': '\([^']*\)'.*/\1/")
if [ "$DB_HOST" = "mariadb" ]; then
    echo -e "${GREEN}✓ mariadb (Docker)${NC}"
elif [ "$DB_HOST" = "127.0.0.1" ] || [ "$DB_HOST" = "localhost" ]; then
    echo -e "${YELLOW}⚠ $DB_HOST (should be 'mariadb' for Docker)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ $DB_HOST${NC}"
fi

# Check Redis/Celery URL
echo -n "Redis/Celery HOST... "
REDIS_HOST=$(grep "CELERY_BROKER_URL" "$SETTINGS_FILE" | sed 's/.*redis:\/\/\([^:]*\):.*/\1/')
if [ "$REDIS_HOST" = "redis" ] || [ "$REDIS_HOST" = "localhost" ]; then
    echo -e "${GREEN}✓ $REDIS_HOST${NC}"
else
    echo -e "${YELLOW}⚠ $REDIS_HOST (expected 'redis' for Docker)${NC}"
    ((WARNINGS++))
fi

# Check SECRET_KEY
echo -n "SECRET_KEY... "
SECRET_KEY=$(grep "^SECRET_KEY = " "$SETTINGS_FILE" | cut -d"'" -f2)
if [ "$SECRET_KEY" = "helloworld" ] || [ ${#SECRET_KEY} -lt 20 ]; then
    echo -e "${RED}✗ Using weak/default SECRET_KEY!${NC}"
    echo -e "  ${YELLOW}Generate a secure key: python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✓ Custom key configured${NC}"
fi

# Check DEBUG mode
echo -n "DEBUG mode... "
DEBUG=$(grep "^DEBUG = " "$SETTINGS_FILE" | awk '{print $3}')
if [ "$DEBUG" = "True" ]; then
    echo -e "${YELLOW}⚠ DEBUG=True (disable in production!)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ DEBUG=False${NC}"
fi

# Check ALLOWED_HOSTS
echo -n "ALLOWED_HOSTS... "
ALLOWED_HOSTS=$(grep "^ALLOWED_HOSTS = " "$SETTINGS_FILE")
if echo "$ALLOWED_HOSTS" | grep -q "\*"; then
    echo -e "${YELLOW}⚠ Contains '*' wildcard${NC}"
    ((WARNINGS++))
elif echo "$ALLOWED_HOSTS" | grep -q "domain.com"; then
    echo -e "${YELLOW}⚠ Still contains example domain${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ Configured${NC}"
fi

# Check database password
echo -n "Database password... "
DB_PASSWORD=$(grep -A 5 "DATABASES = {" "$SETTINGS_FILE" | grep "'PASSWORD':" | sed "s/.*'PASSWORD': '\(.*\)'.*/\1/")
if [ "$DB_PASSWORD" = "helloworld" ] || [ "$DB_PASSWORD" = "password" ]; then
    echo -e "${RED}✗ Using default password!${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✓ Custom password configured${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ Configuration looks good!${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) - Review recommended${NC}"
else
    echo -e "${RED}✗ $ERRORS error(s) - Fix before deployment!${NC}"
    echo -e "${YELLOW}⚠ $WARNINGS warning(s)${NC}"
fi
echo -e "${BLUE}========================================${NC}"

[ $ERRORS -eq 0 ] || exit 1
