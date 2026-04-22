# DeepHunter Docker - Change Log

## [Unreleased]

### Changed
- **Migrated from `docker-compose` v1 to `docker compose` v2 (CLI plugin)** across Makefile and all documentation. The legacy standalone `docker-compose` binary is no longer supported — it does not honour `start_period` in health checks, causing intermittent startup failures. Minimum required version is **Docker Compose v2.17+**.
- `check-requirements.sh` now verifies Docker Compose v2 plugin presence and minimum version.

### Added
- **Git secret-string guard**: pre-commit and pre-push hooks that block commits/pushes containing forbidden strings (case-insensitive). Patterns are configurable via `.githooks/forbidden-patterns.txt` (gitignored, local-only); a committed `.example` template is provided. Activate with `make setup-hooks`. The `install` target now includes hook setup automatically.
- **Custom Root CA trust**: place `.crt` files in `resources/root_ca/` to have them trusted by the system and Python at build time (corporate proxies, internal services)
- `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` environment variables so Python `requests`/`urllib3` use the system CA bundle
- `.gitignore` rule to prevent private `.crt` files from being committed
- `.dockerignore` rules to exclude private key material (`*.key`, `*.pem`, `*.p12`, `*.pfx`) from the build context

## [Enhanced] - December 2025

### Added
- **Multi-stage Dockerfile** for reduced image size and better security
- **Health checks** for all services with proper startup dependencies
- **Automated initialization script** (`scripts/init-deephunter.sh`)
- **Backup and restore functionality** with configurable retention
- **Makefile** with comprehensive management commands
- **Environment variable management** with `.env.example`
- **Enhanced docker-compose.yml** with:
  - Health checks for all services
  - Proper dependency management
  - Resource limits and optimizations
  - Logging configuration
  - Named containers
- **Security improvements**:
  - Non-root user in container
  - Tini for proper signal handling
  - Minimal runtime dependencies
  - Separated debug tools
- **Documentation**:
  - Comprehensive README.md
  - Usage examples
  - Troubleshooting guide
  - Security checklist
- **Utility scripts**:
  - Enhanced build script with versioning
  - Database initialization script
  - Application initialization script
  - Backup script with compression
  - Restore script with safety checks
  - Health check script
- **.dockerignore** for optimized builds
- **.gitignore** for version control
- **Development Compose override** for local testing

### Improved
- **Build process** with better error handling and feedback
- **Container orchestration** with health-based dependencies
- **Resource usage** through multi-stage builds
- **Maintainability** with Makefile commands
- **Security posture** through hardening measures
- **User experience** with automated setup

### Changed
- Dockerfile now uses multi-stage build
- Debug tools moved to optional Dockerfile.debug
- docker-compose.yml enhanced with health checks and logging
- build.sh enhanced with versioning and validation

### Fixed
- Container startup order issues
- Resource cleanup after installation
- Permission issues with proper user setup

## Original Features

- Docker-based deployment
- MariaDB database
- Redis caching
- Supervisor for process management
- Plugin support (VirusTotal, SentinelOne)
- Custom patches for dashboard and reports
- Cron job integration
