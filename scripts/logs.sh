#!/bin/bash
# Log viewer with filtering and real-time monitoring

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

SERVICE="${1:-all}"
FILTER="${2:-}"
LINES="${3:-100}"

show_help() {
    echo "Usage: $0 [service] [filter] [lines]"
    echo ""
    echo "Arguments:"
    echo "  service    Service to view (all|app|db|redis) [default: all]"
    echo "  filter     Filter logs by pattern (optional)"
    echo "  lines      Number of lines to show [default: 100]"
    echo ""
    echo "Examples:"
    echo "  $0                     # View all logs"
    echo "  $0 app                 # View only app logs"
    echo "  $0 app error           # View app logs containing 'error'"
    echo "  $0 db                  # View database logs"
    echo "  $0 all WARNING 50      # Last 50 lines with 'WARNING'"
    echo ""
}

if [ "$SERVICE" = "help" ] || [ "$SERVICE" = "-h" ] || [ "$SERVICE" = "--help" ]; then
    show_help
    exit 0
fi

echo -e "${BLUE}DeepHunter Log Viewer${NC}"
echo -e "${BLUE}===================${NC}"
echo ""

case "$SERVICE" in
    app)
        CONTAINER="deephunter-app"
        ;;
    db)
        CONTAINER="deephunter-mariadb"
        ;;
    redis)
        CONTAINER="deephunter-redis"
        ;;
    all)
        CONTAINER=""
        ;;
    *)
        echo -e "${RED}Unknown service: $SERVICE${NC}"
        show_help
        exit 1
        ;;
esac

if [ -n "$CONTAINER" ]; then
    if ! docker ps | grep -q "$CONTAINER"; then
        echo -e "${RED}Container $CONTAINER is not running${NC}"
        exit 1
    fi
    echo -e "${GREEN}Service: $SERVICE${NC}"
else
    echo -e "${GREEN}Service: all${NC}"
fi

if [ -n "$FILTER" ]; then
    echo -e "${GREEN}Filter: $FILTER${NC}"
fi

echo -e "${GREEN}Lines: $LINES${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop${NC}"
echo ""

# Build docker-compose logs command
CMD="docker-compose logs --tail=$LINES"

if [ -n "$CONTAINER" ]; then
    CMD="$CMD ${SERVICE}"
fi

CMD="$CMD -f"

# Apply filter if specified
if [ -n "$FILTER" ]; then
    eval "$CMD" | grep --color=auto -i "$FILTER"
else
    eval "$CMD"
fi
