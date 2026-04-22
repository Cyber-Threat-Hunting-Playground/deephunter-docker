#!/bin/bash
# Legacy helper — NOT mounted by docker-compose.yml.
#
# The official MariaDB image creates MARIADB_DATABASE, MARIADB_USER, and grants from
# environment variables (see docker-compose.yml) during its built-in init, before any
# files in /docker-entrypoint-initdb.d run. A custom .sh that calls `mysql -u root` there
# often fails with "Access denied ... (using password: NO)" because bootstrap uses the
# entrypoint's socket/sql path, not a plain root password client session.
#
# For extra DDL after first start, use a .sql file mounted into /docker-entrypoint-initdb.d/
# or run migrations from the app container (make init).

exit 0
