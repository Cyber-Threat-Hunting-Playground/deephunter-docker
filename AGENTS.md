# DeepHunter Docker — AI Context

Production-ready Docker deployment for the **DeepHunter Security Analytics Platform**.
This repo packages the upstream [DeepHunter](https://github.com/Cyber-Threat-Hunting-Playground/deephunter) Django application into a Docker Compose stack with MariaDB, Redis, and optional Adminer.

> For technology rationale, design decisions, feature status, and roadmap see [PROJECT-SPEC.md](PROJECT-SPEC.md).

## Tech Stack

| Layer | Technology | Version / Notes |
|-------|-----------|-----------------|
| Container runtime | Docker + Compose v2 | `docker compose` (space, not hyphen) — v2.17+ required |
| Application | Django | 5.2 (Python, runs under Apache mod_wsgi) |
| Database | MariaDB | LTS tag, utf8mb4 |
| Cache / Broker | Redis | latest, AOF persistence, 256 MB maxmemory allkeys-lru |
| Task queue | Celery | Connects via `redis://redis:6379` |
| Process manager | Supervisor | Runs Apache + Celery + cron inside the app container |
| Init system | Tini | PID 1 signal handling |
| Web server | Apache 2 | mod_wsgi, self-signed TLS on port 443 |
| DB admin (optional) | Adminer | Enabled via Compose profile `adminer` |
| Base image | Debian bookworm-slim | Multi-stage build (builder → runtime) |

## Architecture

```
┌─────────────────────────────────────────────────┐
│           DeepHunter Application                │
│         (Host port ${DEEPHUNTER_PORT} → 443)    │
│  ┌────────────────────────────────────────────┐ │
│  │  Supervisor: Apache + Celery + cron        │ │
│  └────────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│   MariaDB   │  │   Redis     │
│  (backend)  │  │  (backend)  │
└──────┬──────┘  └─────────────┘
       │
┌──────▼──────────────┐
│   Adminer           │
│  (optional – :8080) │
└─────────────────────┘
```

All services share a single Docker bridge network (`backend`). Only the app (HTTPS) and Adminer (HTTP) ports are published to the host.

## File Organization

```
deephunter-docker/
├── Dockerfile              Multi-stage production build
├── Dockerfile.debug        Optional: adds debug tools
├── docker-compose.yml      Service orchestration (production)
├── docker-compose.dev.yml  Compose override for local development
├── Makefile                Primary operational interface (20+ targets)
├── build.sh                Image build wrapper with metadata
├── .env.example            Environment variable template
├── .env                    Local overrides (NOT committed)
│
├── data/                   Persistent runtime data (bind-mounted)
│   ├── settings.py         Django settings — MUST stay in sync with .env
│   ├── mariadb/            MariaDB data files (generated)
│   ├── redis/              Redis AOF data (generated)
│   ├── logs/               Application + cron logs (generated)
│   └── backups/            Backup archives (generated)
│
├── patch/                  Upstream overrides copied during Docker build
│   ├── dashboard/          Dashboard view patches
│   ├── reports/            Report template patches
│   ├── connectors/         Connector view patches
│   ├── repos/              Repository view patches
│   ├── qm/                 Query Manager patches (views, signals, templates)
│   ├── config/             Config app patches (AI debug tab, REST API auth)
│   ├── deephunter/         URL routing, API auth, history middleware
│   └── plugins/catalog/    Plugin patches (OpenAI custom, GitHub, Bitbucket)
│
├── resources/              Build-time resources
│   ├── installer-*.sh      DeepHunter installer script
│   ├── supervisord.conf    Supervisor configuration
│   └── root_ca/            Custom Root CA .crt files (gitignored)
│
├── scripts/                Operational bash scripts
│   ├── docker-entrypoint.sh
│   ├── init-db.sh / init-deephunter.sh
│   ├── backup.sh / restore.sh
│   ├── health-check.sh / monitor.sh / diagnostics.sh
│   ├── validate-config.sh / check-requirements.sh
│   ├── upgrade.sh / uninstall.sh / logs.sh
│   └── common.sh           Shared color/utility functions
│
└── examples/               Reference configurations
```

## Key Conventions

### Makefile-first operations
Always use `make <target>` instead of raw `docker` commands. Run `make help` to list all targets. Key targets: `install`, `build`, `up`, `down`, `restart`, `init`, `backup`, `restore`, `status`, `health`, `validate-config`.

### Dual-source configuration (critical)
Credentials and host names live in **two places** that must be kept in sync manually:
- **`.env`** — read by `docker-compose.yml` for container environment variables
- **`data/settings.py`** — read by Django at runtime (hardcoded values, NOT sourced from env)

When changing a password or hostname, update **both** files. `make validate-config` checks for common mismatches.

### Patch overlay system
Files under `patch/` replace upstream DeepHunter files during the Docker build (`COPY patch/... /data/deephunter/...` in the Dockerfile). When modifying upstream behavior, add or edit files in `patch/` — never edit files inside a running container.

### Shell script standards
- Scripts use `#!/usr/bin/env bash`
- Scripts source `scripts/common.sh` for shared color output and utility functions
- Include `--help` support and descriptive error messages

### Forbidden-string guard (git hooks)
Git hooks in `.githooks/` prevent committing or pushing files that contain sensitive strings. Run `make setup-hooks` (or `make install`, which includes it) to activate. The hooks read patterns from `.githooks/forbidden-patterns.txt` (gitignored, local-only); copy the committed `.githooks/forbidden-patterns.txt.example` template to get started. Two layers of protection:
- **pre-commit** — scans staged files before each commit.
- **pre-push** — scans the diff of commits about to be pushed.

### Plugin management
Plugins are enabled by symlinking from `plugins/catalog/` in the Dockerfile. To enable a new plugin, add an `ln -s` line in the builder stage.

## Rules

### Do
- Use `make` targets for all operations
- Update `CHANGELOG.md` when making user-visible changes
- Keep `.env` and `data/settings.py` in sync after credential changes
- Run `make validate-config` before deploying configuration changes
- Place new upstream overrides in `patch/` and add corresponding `COPY` lines in the Dockerfile
- Use `docker compose` (v2 with space) — never `docker-compose` (v1)
- Test with `make health` and `make status` after changes
- Run `make setup-hooks` after cloning to activate the forbidden-string guard

### Don't
- Edit generated files under `data/mariadb/`, `data/redis/`, or `data/logs/`
- Commit `.env` or `data/settings.py` with real credentials
- Use `docker-compose` (v1 binary) — it mishandles `start_period` in health checks
- Run `pip install` inside the running container — add dependencies to the Dockerfile builder stage
- Remove `tini` entrypoint — it is required for correct signal propagation
- Hardcode container names in scripts — use `docker compose` service names
- Commit `.githooks/forbidden-patterns.txt` — it is gitignored; only the `.example` template is tracked
