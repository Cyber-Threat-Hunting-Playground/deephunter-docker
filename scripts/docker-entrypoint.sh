#!/usr/bin/env bash
# Wrapper entrypoint for the DeepHunter app container.
# Optionally installs the orchestrator cron job, then execs the main CMD.
set -euo pipefail

# Collect static files so DRF/Swagger assets are served by Apache
echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Collecting static files..."
cd /data/deephunter && /data/venv/bin/python manage.py collectstatic --noinput 2>&1 | tail -1

if [ "${ENABLE_CRON:-false}" = "true" ]; then
    CRON_SCHEDULE="${CRON_SCHEDULE:-30 10 * * *}"
    LOG_FILE="/var/log/deephunter/cron-orchestrator.log"
    ORCHESTRATOR="/data/deephunter/qm/scripts/orchestrator.sh"

    cat > /etc/cron.d/orchestrator <<CRONTAB
SHELL=/bin/bash
${CRON_SCHEDULE} root ${ORCHESTRATOR} >> ${LOG_FILE} 2>&1
CRONTAB
    chmod 0644 /etc/cron.d/orchestrator

    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Orchestrator cron enabled"
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')]   Schedule : ${CRON_SCHEDULE}"
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')]   Command  : ${ORCHESTRATOR}"
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')]   Log file : ${LOG_FILE}"
else
    rm -f /etc/cron.d/orchestrator
fi

# When /patch is bind-mounted (e.g. docker-compose.dev), keep runtime code in sync with the repo.
if [ -f /patch/dashboard/views.py ]; then
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Applying live patch: dashboard/views.py"
    cp /patch/dashboard/views.py /data/deephunter/dashboard/views.py
    chown deephunter:deephunter /data/deephunter/dashboard/views.py 2>/dev/null || true
fi

exec "$@"
