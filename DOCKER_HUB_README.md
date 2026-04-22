# DeepHunter — Security Analytics Platform

[![CI/CD](https://github.com/Cyber-Threat-Hunting-Playground/deephunter-docker/actions/workflows/github-actions.yml/badge.svg)](https://github.com/Cyber-Threat-Hunting-Playground/deephunter-docker/actions)

Production-ready Docker image for the **DeepHunter** Security Analytics Platform. Includes Django, Apache mod_wsgi, Celery, cron, and Supervisor — all managed under Tini as PID 1.

## Supported Tags

| Tag | Description |
|-----|-------------|
| `latest` | Latest stable release |
| `X.Y.Z` (e.g. `2.5.1`) | Specific release |
| `X.Y` (e.g. `2.5`) | Latest patch for a minor release |
| `X` (e.g. `2`) | Latest minor for a major release |

## Quick Start

### 1. Pull the image

```bash
docker pull cyberthreatplayground/deephunter:latest
```

### 2. Run with Docker Compose

Create a `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:latest
    restart: always
    networks: [ backend ]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru

  mariadb:
    image: mariadb:lts
    restart: always
    networks: [ backend ]
    volumes:
      - mariadb_data:/var/lib/mysql
    environment:
      MARIADB_ROOT_PASSWORD: ${MARIADB_ROOT_PASSWORD:-ChangeMe!}
      MARIADB_DATABASE: ${MARIADB_DATABASE:-deephunter}
      MARIADB_USER: ${MARIADB_USER:-deephunter}
      MARIADB_PASSWORD: ${MARIADB_PASSWORD:-ChangeMe!}
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      interval: 10s
      timeout: 5s
      retries: 30
      start_period: 60s

  deephunter:
    image: cyberthreatplayground/deephunter:latest
    restart: unless-stopped
    networks: [ backend ]
    ports:
      - "9000:443"
    environment:
      - DB_HOST=mariadb
      - DB_PORT=3306
      - DB_NAME=${MARIADB_DATABASE:-deephunter}
      - DB_USER=${MARIADB_USER:-deephunter}
      - DB_PASSWORD=${MARIADB_PASSWORD:-ChangeMe!}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      redis:    { condition: service_healthy }
      mariadb:  { condition: service_healthy }

volumes:
  mariadb_data:

networks:
  backend:
```

```bash
docker compose up -d
```

Access the application at **https://localhost:9000**.

## Architecture

```
  DeepHunter (HTTPS :443)
  ┌────────────────────────────────┐
  │  Supervisor                    │
  │  ├─ Apache + mod_wsgi (Django) │
  │  ├─ Celery worker              │
  │  └─ cron (optional)            │
  └──────┬──────────┬──────────────┘
         │          │
    ┌────▼────┐ ┌───▼───┐
    │ MariaDB │ │ Redis │
    └─────────┘ └───────┘
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `mariadb` | Database hostname |
| `DB_PORT` | `3306` | Database port |
| `DB_NAME` | `deephunter` | Database name |
| `DB_USER` | `deephunter` | Database username |
| `DB_PASSWORD` | — | Database password |
| `REDIS_HOST` | `redis` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `DB_DATA_RETENTION` | `90` | Data retention in days |
| `ENABLE_CRON` | `false` | Enable scheduled orchestrator |
| `CRON_SCHEDULE` | `30 10 * * *` | Cron expression (UTC) |

## Image Verification

This image is signed with [cosign](https://github.com/sigstore/cosign) using keyless signing (GitHub OIDC). To verify:

```bash
cosign verify \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp 'github\.com/Cyber-Threat-Hunting-Playground/deephunter-docker' \
  cyberthreatplayground/deephunter:latest
```

An SBOM (CycloneDX) is attached to every release. To download:

```bash
cosign download sbom cyberthreatplayground/deephunter:latest > sbom.cdx.json
```

## Health Check

The image includes a built-in health check:

```
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3
  CMD curl -f -k https://localhost:443/ || exit 1
```

## Security

- Runs Apache as `www-data`, Celery as dedicated `celery` user
- Tini as PID 1 for proper signal handling
- No pip/build tools in the final image (reduced attack surface)
- Self-signed TLS certificate generated at build time
- Trivy-scanned for CRITICAL/HIGH vulnerabilities in CI

## Documentation

Full deployment guide, Makefile targets, backup/restore, and configuration reference:

**[https://github.com/Cyber-Threat-Hunting-Playground/deephunter-docker](https://github.com/Cyber-Threat-Hunting-Playground/deephunter-docker)**

## License

This project is licensed under the [MIT License](https://github.com/Cyber-Threat-Hunting-Playground/deephunter-docker/blob/main/LICENSE).
