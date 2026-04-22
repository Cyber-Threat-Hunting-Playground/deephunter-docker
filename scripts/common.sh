#!/bin/bash
# Common utilities for DeepHunter scripts
# Source this file: source "$(dirname "$0")/common.sh"

# ── Colors ───────────────────────────────────────────────────────
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ── Logging helpers ──────────────────────────────────────────────

info()    { echo -e "${BLUE}$*${NC}"; }
success() { echo -e "${GREEN}✓ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠ $*${NC}"; }
error()   { echo -e "${RED}✗ $*${NC}"; }

# ── Docker helpers ───────────────────────────────────────────────

# Detect the correct compose command (V2 plugin > V1 standalone)
detect_compose_cmd() {
    if docker compose version &>/dev/null; then
        echo "docker compose"
    elif command -v docker-compose &>/dev/null; then
        echo "docker-compose"
    else
        error "Neither 'docker compose' nor 'docker-compose' found"
        exit 1
    fi
}

COMPOSE_CMD="${COMPOSE_CMD:-$(detect_compose_cmd)}"

# Check that Docker daemon is running
require_docker() {
    if ! docker info &>/dev/null; then
        error "Docker is not running"
        exit 1
    fi
}

# Check that a specific container is running
# Usage: require_container "deephunter-mariadb"
require_container() {
    local container="$1"
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        error "Container ${container} is not running"
        exit 1
    fi
}