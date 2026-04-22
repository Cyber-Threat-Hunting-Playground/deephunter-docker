# DeepHunter Docker — Project Specification

Living document capturing technology choices, design decisions, feature status, and roadmap.
Update this file whenever a significant choice is made or a feature ships.

---

## Technology Choices

| Area | Choice | Alternatives Considered | Rationale |
|------|--------|------------------------|-----------|
| **Container runtime** | Docker + Compose v2 | Kubernetes, Podman | Single-host deployment target; Compose is sufficient and familiar. K8s planned as a future option. |
| **Base image** | Debian bookworm-slim | Alpine, Ubuntu | Broad package availability; slim variant reduces size. Alpine causes musl-related issues with Python C extensions (numpy, scipy). |
| **Database** | MariaDB LTS | PostgreSQL, MySQL | MySQL-compatible; required by upstream DeepHunter. LTS tag for stability. |
| **Cache / message broker** | Redis (latest, AOF) | RabbitMQ, Memcached | Required by DeepHunter for Celery broker and result backend. AOF persistence avoids data loss on restart. |
| **Task queue** | Celery 5.5 | Django Q, Huey | Required by upstream DeepHunter; mature, well-supported. |
| **Web server** | Apache 2 + mod_wsgi | Nginx + Gunicorn | Upstream DeepHunter installer configures Apache; keeping alignment avoids divergence. |
| **Process manager** | Supervisor | systemd, s6-overlay | Runs Apache + Celery + cron in one container. Simple config, well-documented, used by upstream installer. |
| **Init system** | Tini | dumb-init, none | Lightweight PID 1; reaps zombies, forwards signals correctly. Docker best practice. |
| **DB admin UI** | Adminer (optional) | phpMyAdmin, DBeaver | Lightweight single-file PHP app. Enabled via Compose profile so it's zero-cost when unused. |
| **Build automation** | Makefile | Just, Task, shell scripts | Universal availability on Linux/macOS; self-documenting with `make help`. |
| **CI** | GitHub Actions | GitLab CI, CircleCI | Project hosted on GitHub; native integration. |

---

## Design Decisions

### DD-001: Single container for app + workers

- **Status**: Implemented
- **Context**: DeepHunter needs Django (Apache), Celery worker, Celery beat, and cron. Running each as a separate container follows 12-factor orthodoxy but complicates the setup for a single-host deployment.
- **Decision**: Run all processes inside one container managed by Supervisor.
- **Trade-off**: Violates one-process-per-container principle but dramatically simplifies deployment, logging, and the Makefile. Acceptable for the target audience (security analysts, not platform engineers).

### DD-002: Bind-mount settings.py instead of baking into image

- **Status**: Implemented
- **Context**: Django settings contain secrets (SECRET_KEY, DB password) and site-specific values (ALLOWED_HOSTS). Baking them into the image would require a rebuild for every config change and risk leaking secrets in image layers.
- **Decision**: `data/settings.py` is bind-mounted read-only at runtime.
- **Trade-off**: Requires manual sync between `.env` and `data/settings.py`. Mitigated by `make validate-config`.

### DD-003: Optional cron inside the container

- **Status**: Implemented
- **Context**: The orchestrator script needs periodic execution. Options: host crontab calling `docker exec`, Kubernetes CronJob, or cron inside the container.
- **Decision**: Cron runs inside the container via Supervisor. Enabled/disabled via `ENABLE_CRON` env var. The entrypoint script installs or removes the crontab entry at startup.
- **Trade-off**: Container must run cron daemon. Benefit: self-contained, works identically on any Docker host.

### DD-004: Patch overlay system for upstream customization

- **Status**: Implemented
- **Context**: The upstream DeepHunter repo is not forked; customizations must be applied non-destructively.
- **Decision**: `patch/` directory mirrors the upstream file tree. The Dockerfile `COPY` commands replace specific files after the upstream installer runs.
- **Trade-off**: Patches can break on upstream updates. Each patch file must be reviewed when upgrading DeepHunter versions.

### DD-005: Multi-stage Docker build

- **Status**: Implemented
- **Context**: Build tools (pip, compilers) and temporary files inflate the final image.
- **Decision**: Two-stage build: `builder` installs everything, `runtime` copies only what's needed.
- **Trade-off**: Slightly more complex Dockerfile. Benefit: ~33% smaller image, no pip/build tools in production (reduced attack surface).

### DD-006: Custom Root CA trust at build time

- **Status**: Implemented
- **Context**: Corporate environments use TLS-intercepting proxies. Python's `requests` and `urllib3` fail on internal HTTPS endpoints without the corporate Root CA in the trust store.
- **Decision**: Place `.crt` files in `resources/root_ca/` before build. Dockerfile copies them and runs `update-ca-certificates`. `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` env vars point Python at the system bundle.
- **Trade-off**: Root CA certs are baked into the image — must not push to public registries. Mitigated by `.gitignore` and `.dockerignore` rules.

### DD-007: REST API with DRF + drf-spectacular

- **Status**: Implemented
- **Context**: DeepHunter needed a programmatic API for automation and integration.
- **Decision**: Django REST Framework with drf-spectacular for OpenAPI/Swagger documentation. Custom API key authentication with session fallback.
- **Trade-off**: Adds pip dependencies (installed at build time). Benefit: auto-generated API docs, standardized auth.

---

## Features — Implemented

### Infrastructure & Deployment
- [x] Multi-stage Docker build (builder + runtime)
- [x] Docker Compose v2 orchestration with health checks on all services
- [x] Tini init system for proper signal handling
- [x] Supervisor managing Apache + Celery + cron
- [x] Non-root user execution (deephunter, celery, www-data service accounts)
- [x] Makefile with 20+ management targets (`make help` for full list)
- [x] One-command installation (`make install`)
- [x] Environment-based configuration (`.env` + `data/settings.py`)
- [x] Configuration validation (`make validate-config`)

### Operations
- [x] Backup and restore with configurable retention
- [x] Automated database initialization
- [x] Health check endpoints and scripts
- [x] Real-time performance monitoring (`make monitor`)
- [x] Diagnostic report generation (`make diagnostics`)
- [x] Log rotation and filtering (`make logs-filter`)
- [x] Upgrade path with automatic backup (`make upgrade`)
- [x] Uninstall script

### Security
- [x] Multi-stage build — no build tools in production image
- [x] Non-root container execution
- [x] Custom Root CA trust (corporate proxies)
- [x] `.gitignore` / `.dockerignore` protecting secrets and private keys
- [x] Self-signed TLS out of the box
- [x] Network isolation (Docker bridge network)

### Application Patches
- [x] Dashboard view patches
- [x] Report template patches (stats.html)
- [x] REST API v1 with custom ApiKey auth + session fallback
- [x] REST API v2 (DRF + drf-spectacular, Swagger/ReDoc)
- [x] AI debug tab (config app)
- [x] Query Manager patches (views, signals, templates)
- [x] Connector and repository view patches
- [x] Plugin patches (OpenAI custom, SentinelOne enabled by default)
- [x] Optional cron orchestrator (configurable schedule)
- [x] Adminer (optional, profile-based)

---

## Features — Planned / Roadmap

### High Priority
- [ ] **CI/CD pipeline** — GitHub Actions workflow for build, test, and publish. Partially scaffolded in `examples/github-actions.yml`.
- [ ] **SSL certificate automation** — Let's Encrypt integration via Certbot or Traefik reverse proxy. Currently using self-signed certs.
- [ ] **Multi-environment support** — Separate Compose files or profiles for dev / staging / prod with environment-specific defaults.

### Medium Priority
- [ ] **Kubernetes deployment manifests** — Helm chart or plain YAML for K8s clusters. Would require splitting the single container into separate deployments (app, worker, beat).
- [ ] **Prometheus metrics export** — Django-prometheus or a sidecar exporter for container and application metrics.
- [ ] **Grafana dashboard templates** — Pre-built dashboards for DeepHunter operational metrics.
- [ ] **Automated testing suite** — Smoke tests for container startup, health checks, API endpoints, and backup/restore.

### Low Priority / Future
- [ ] **Blue-green deployment support** — Zero-downtime upgrades with parallel stacks.
- [ ] **Horizontal scaling guide** — Multiple app containers behind a load balancer.
- [ ] **Load balancer integration** — Nginx or Traefik reverse proxy with TLS termination.
- [ ] **Disaster recovery procedures** — Documented runbook for full recovery from backup.
- [ ] **Performance tuning guide** — MariaDB, Redis, Apache, and Celery tuning recommendations.
- [ ] **Cost optimization guide** — Resource sizing recommendations for different workload profiles.

---

## Constraints

- **Single-host deployment** — The current architecture targets a single Docker host. Clustering requires the Kubernetes track.
- **Upstream DeepHunter is external** — This repo does not maintain the core Django application. Upstream changes may break patches; each upgrade requires patch review.
- **No frontend build pipeline** — Static assets (JS, CSS) are vendored upstream. No Node.js or webpack tooling exists in this repo.
- **Python dependencies are frozen at build time** — The venv is pre-built in the Docker image. pip is deliberately removed from the production image to reduce attack surface.
- **Docker Compose v1 is unsupported** — The legacy `docker-compose` binary mishandles `start_period` in health checks. Only `docker compose` (v2 plugin, v2.17+) is supported.

## Non-Goals

- Replacing the upstream DeepHunter installer — this repo wraps it, not replaces it.
- Supporting non-Docker deployment methods (bare-metal, VM images).
- Managing DeepHunter user accounts or RBAC — that belongs to the application layer.
- Providing a general-purpose Django Docker template — this is purpose-built for DeepHunter.
