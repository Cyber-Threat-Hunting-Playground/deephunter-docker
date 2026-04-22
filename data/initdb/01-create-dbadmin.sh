#!/bin/bash
# Creates a dedicated database admin user for Adminer.
# Sourced by the MariaDB entrypoint on first initialization only.
# Requires ADMINER_DB_USER and ADMINER_DB_PASSWORD to be set;
# skips silently when they are absent so the stack works without Adminer.

if [ -z "${ADMINER_DB_USER:-}" ] || [ -z "${ADMINER_DB_PASSWORD:-}" ]; then
    return 0 2>/dev/null || exit 0
fi

docker_process_sql <<-EOSQL
    CREATE USER IF NOT EXISTS '${ADMINER_DB_USER}'@'%' IDENTIFIED BY '${ADMINER_DB_PASSWORD}';
    GRANT ALL PRIVILEGES ON \`${MARIADB_DATABASE:-deephunter}\`.* TO '${ADMINER_DB_USER}'@'%';
    FLUSH PRIVILEGES;
EOSQL
