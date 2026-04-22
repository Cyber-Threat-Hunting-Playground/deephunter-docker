# DeepHunter Docker Deployment

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Django](https://img.shields.io/badge/django-%23092E20.svg?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=flat&logo=mariadb&logoColor=white)](https://mariadb.org/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![Adminer](https://img.shields.io/badge/Adminer-34567C?style=flat&logo=adminer&logoColor=white)](https://www.adminer.org/)

Production-ready Docker deployment for the DeepHunter Security Analytics Platform.

## 🚀 Features

- **Multi-stage Docker builds** for optimized image size
- **Health checks** for all services with proper dependency management
- **Automated initialization** script for hassle-free setup
- **Optional scheduled orchestrator** via built-in cron (configurable schedule, default 10:30 AM UTC)
- **Backup and restore** functionality with configurable retention
- **Environment-based configuration** using .env files
- **Makefile** for simplified operations
- **Security hardened** Dockerfile with non-root user
- **Git secret-string guard** via pre-commit and pre-push hooks with configurable forbidden patterns
- **Comprehensive logging** with rotation
- **Container orchestration** with Docker Compose

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose **v2.17+** (the `docker compose` CLI plugin — **not** the legacy `docker-compose` v1 binary)
- 4GB RAM minimum (8GB recommended)
- 20GB disk space minimum

### Checking prerequisites

```bash
docker --version            # expect 20.10+
docker compose version      # expect v2.17+ (note: space, not hyphen)
```

### Installing Docker Compose v2 (if missing)

Docker Compose v2 ships as a CLI plugin for Docker Engine (`docker compose` with a space).
The legacy standalone `docker-compose` (v1) is **not supported** — it does not correctly
honour `start_period` in health checks, causing intermittent startup failures.

| Platform | Install command |
|----------|----------------|
| Ubuntu / Debian | `sudo apt-get update && sudo apt-get install docker-compose-plugin` |
| Fedora / RHEL / CentOS | `sudo dnf install docker-compose-plugin` |
| Docker Desktop (Windows / macOS) | Included by default — update Docker Desktop if `docker compose version` fails |
| Manual / other Linux | See [Docker Compose install docs](https://docs.docker.com/compose/install/linux/) |

After installation verify with `docker compose version`.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           DeepHunter Application            │
│         (Port 9000 → HTTPS 443)             │
│  ┌──────────────────────────────────────┐   │
│  │  Cron (optional) – orchestrator.sh   │   │
│  └──────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│   MariaDB   │  │   Redis     │
│  (Database) │  │   (Cache)   │
└──────┬──────┘  └─────────────┘
       │
┌──────▼──────────────┐
│   Adminer           │
│   (optional – :8080)│
└─────────────────────┘
```

## 🚀 Quick Start

### 1. Clone and Configure

```bash
# Clone the repository (or navigate to your project)
cd deephunter-docker

# Create environment file from template
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 2. One-Command Installation

```bash
make install
```

This will:
- Create necessary directories
- Build the Docker image
- Start all services
- Initialize the database
- Load default fixtures
- Create superuser account

### 3. Access the Application

Open your browser and navigate to:
```
https://localhost:9000
```

## 📖 Detailed Setup

### Manual Step-by-Step Installation

#### 1. Environment Configuration

Edit the [.env.example](.env.example) file (copy to `.env` first: `cp .env.example .env`):

```bash
# MariaDB Configuration
MARIADB_ROOT_PASSWORD=YourSecureRootPassword123!
MARIADB_DATABASE=deephunter
MARIADB_USER=deephunter
MARIADB_PASSWORD=Awes0meP4ssW0rd

# DeepHunter Configuration
DEEPHUNTER_PORT=9000

# Optional: Scheduled Orchestrator (disabled by default)
ENABLE_CRON=false
CRON_SCHEDULE="30 10 * * *"
```

#### 2. Application Settings

⚠️ **CRITICAL**: The default `settings.py` has been updated for Docker, but you **MUST** change:

**Security Critical** (Change before deployment!):
```bash
# Generate secure SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Customize [data/settings.py](data/settings.py):
- ⚠️ **MUST CHANGE**: `SECRET_KEY` (use generated key above)
- ⚠️ **MUST CHANGE**: Database `PASSWORD` (match `.env` file)
- Update `ALLOWED_HOSTS` with your domain
- Set `DEBUG = False` for production
- Configure proxy settings if needed

> **Important:** `data/settings.py` contains its own hardcoded database credentials, Redis
> host, and other values. These are **not** read from the `.env` file or from the environment
> variables defined in `docker-compose.yml`. You must keep **both** files in sync manually:
> any credential you change in `.env` (e.g. `MARIADB_PASSWORD`) must also be updated in the
> matching field inside `data/settings.py` (`DATABASES … PASSWORD`), and vice-versa.
> The same applies to host names (`DB_HOST` ↔ `DATABASES … HOST`) and Redis URLs
> (`REDIS_HOST` ↔ `CELERY_BROKER_URL`).

**Validate your configuration**:
```bash
make validate-config
```

📖 See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration guide.

#### 3. Build the Image

```bash
make build
# or
./build.sh
```

#### 4. Start Services

```bash
make up
```

#### 5. Initialize the Application

```bash
make init
```

Follow the prompts to create your superuser account.

## 🛠️ Management Commands

### Using Make (Recommended)

#### Lifecycle Management
```bash
make build             # Build Docker image
make up                # Start all services
make down              # Stop all services
make restart           # Restart all services
```

#### Monitoring & Diagnostics
```bash
make status            # Show service status
make health            # Check health of services
make monitor           # Real-time performance monitoring
make diagnostics       # Generate diagnostic report
```

#### Logging
```bash
make logs              # View logs from all services
make logs-app          # View application logs only
make logs-cron         # View cron orchestrator logs
make logs-filter SERVICE=app FILTER=error  # Filter logs
```

#### Operations
```bash
make shell             # Open shell in app container
make db-shell          # Open MariaDB shell
make redis-shell       # Open Redis CLI
make init              # Initialize DeepHunter
make backup            # Create backup
make restore           # Restore from backup
make upgrade           # Upgrade with backup & health checks
```

#### Validation
```bash
make check-requirements  # Check system requirements
make validate           # Validate Compose config
make validate-config    # Validate settings.py
make setup-hooks        # Activate git secret-string guard
```

#### Maintenance
```bash
make clean             # Remove all data (WARNING: destructive!)
make update            # Update to latest version
make rebuild           # Clean rebuild everything
```

### Direct Docker Commands

```bash
# Build
docker build -t deephunter:latest ./

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Execute commands in container
docker exec -it deephunter-app bash
```

## 💾 Backup & Restore

### Create Backup

```bash
make backup
```

Backups are stored in `./data/backups/` and include:
- Complete database dump
- Application settings
- Configuration files

### Restore from Backup

```bash
make restore BACKUP_FILE=./data/backups/deephunter_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Backup Retention

Configure retention in [.env.example](.env.example) (copy to `.env` if not done yet):
```bash
BACKUP_RETENTION_DAYS=30
```

## ⏰ Scheduled Orchestrator (Optional)

The DeepHunter app container can optionally run the orchestrator script (`/data/deephunter/qm/scripts/orchestrator.sh`) on a recurring cron schedule. The cron daemon is already running inside the container via supervisord; enabling this feature simply installs an additional crontab entry at startup.

### Enable the Orchestrator

Edit `.env` **before** running `make up`:

```bash
# Enable the orchestrator cron job
ENABLE_CRON=true

# Schedule in cron syntax (default: 10:30 AM UTC daily)
CRON_SCHEDULE="30 10 * * *"
```

Common schedule examples:

| Schedule | Cron Expression |
|----------|----------------|
| Daily at 10:30 AM UTC (default) | `30 10 * * *` |
| Daily at 6:00 AM UTC | `0 6 * * *` |
| Every 6 hours | `0 */6 * * *` |
| Weekdays at 8:00 AM UTC | `0 8 * * 1-5` |
| Twice a day (6 AM and 6 PM UTC) | `0 6,18 * * *` |

> **Note:** The schedule is evaluated in the timezone set by the `TZ` variable (default `UTC`).

### Monitor the Orchestrator

```bash
# Tail the orchestrator execution log (bind-mounted to the host)
make logs-cron

# Or read the log inside the container
docker exec deephunter-app cat /var/log/deephunter/cron-orchestrator.log

# Verify the crontab was installed
docker exec deephunter-app cat /etc/cron.d/orchestrator
```

### Disable the Orchestrator

Set `ENABLE_CRON=false` in `.env` and restart:

```bash
make restart
```

The crontab entry is automatically removed on the next container start.

## 🔒 Security Considerations

1. **Change default passwords** in `.env` (see [.env.example](.env.example)) **and** in `data/settings.py`
2. **Generate secure SECRET_KEY** in [data/settings.py](data/settings.py)
3. **Enable HTTPS** with valid certificates in production
4. **Trust corporate Root CAs** - place `.crt` files in `resources/root_ca/` before building
5. **Configure firewall** to restrict access
6. **Regular backups** - automate with cron
7. **Activate secret-string guard** - `make setup-hooks` to block commits/pushes containing forbidden strings
8. **Update regularly** - `make update`
9. **Monitor logs** - `make logs`

### Hardening Checklist

- [ ] Changed all default passwords
- [ ] Generated secure SECRET_KEY
- [ ] Configured proper ALLOWED_HOSTS
- [ ] Set up SSL/TLS certificates
- [ ] Added corporate Root CA certs to `resources/root_ca/` (if applicable)
- [ ] Activated git secret-string guard (`make setup-hooks`)
- [ ] Configured firewall rules
- [ ] Set up automated backups
- [ ] Configured log rotation
- [ ] Reviewed security settings

## 📁 Directory Structure

```
deephunter-docker/
├── data/                          # Persistent data
│   ├── settings.py               # Application settings
│   ├── mariadb/                  # Database files
│   ├── redis/                    # Redis data
│   ├── logs/                     # Application logs
│   └── backups/                  # Backup files
├── patch/                        # Application patches
│   ├── dashboard/
│   └── reports/
├── resources/                    # Installation resources
│   ├── installer-v2.5-docker.sh
│   ├── supervisord.conf
│   └── root_ca/                 # Custom Root CA certificates (.crt)
├── .githooks/                    # Git hooks (activate: make setup-hooks)
│   ├── pre-commit               # Blocks commits with forbidden strings
│   ├── pre-push                 # Blocks pushes with forbidden strings
│   └── forbidden-patterns.txt.example  # Pattern template (copy to .txt)
├── scripts/                      # Management scripts
│   ├── init-db.sh               # Database initialization
│   ├── init-deephunter.sh       # App initialization
│   ├── backup.sh                # Backup script
│   ├── restore.sh               # Restore script
│   └── docker-entrypoint.sh     # Container entrypoint (optional cron setup)
├── Dockerfile                    # Main Dockerfile
├── Dockerfile.debug             # Debug tools (optional)
├── docker-compose.yml           # Service orchestration
├── Makefile                     # Management commands
├── build.sh                     # Build script
├── .env.example                 # Environment template
├── .env                         # Environment config (create from example)
├── .dockerignore               # Docker build exclusions
└── README.md                    # This file
```

## 🔧 Troubleshooting

### Services won't start

```bash
# Check service status
make status
make health

# View logs
make logs

# Validate configuration
make validate
```

### Database connection issues

```bash
# Check MariaDB health
docker exec deephunter-mariadb healthcheck.sh --connect

# Open database shell
make db-shell
```

### Application errors

```bash
# View application logs
make logs-app

# Open shell for debugging
make shell

# Check settings
cat data/settings.py
```

### Reset everything

```bash
# WARNING: This deletes all data!
make clean
make install
```

## 🐛 Known Issues

### Microsoft Sentinel Bug

The presence of a Microsoft Sentinel analytics rule prevents editing other analytics rules by default.

**Solutions:**
1. Enable Microsoft Sentinel plugin, or
2. Delete Microsoft Sentinel analytic rule from admin settings

### Permission Issues

If you encounter permission issues:

```bash
# Fix permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

## 📊 Monitoring

### View Real-time Logs

```bash
# All services
make logs

# Specific service
make logs-app
make logs-db
make logs-redis
```

### Check Health

```bash
make health
```

### Resource Usage

```bash
docker stats
```

## 🔄 Updates

### Update to Latest Version

```bash
make update
```

This will:
1. Pull latest images
2. Rebuild application
3. Restart services
4. Preserve your data and settings

### Manual Update

```bash
make down
make build
make up
```

## 🐳 Docker Hub

The DeepHunter image is published to Docker Hub at [`cyberthreatplayground/deephunter`](https://hub.docker.com/r/cyberthreatplayground/deephunter).

### Pulling the Image

```bash
docker pull cyberthreatplayground/deephunter:latest
```

To use the Docker Hub image instead of building locally, set `DEEPHUNTER_IMAGE` in your `.env`:

```bash
DEEPHUNTER_IMAGE=cyberthreatplayground/deephunter:2.5
```

Then `docker compose up -d` will pull from Docker Hub automatically.

### Image Verification

Every release is signed with [cosign](https://github.com/sigstore/cosign) (keyless, via GitHub OIDC) and includes an attached SBOM:

```bash
# Verify signature
cosign verify \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp 'github\.com/Cyber-Threat-Hunting-Playground/deephunter-docker' \
  cyberthreatplayground/deephunter:latest

# Download SBOM
cosign download sbom cyberthreatplayground/deephunter:latest > sbom.cdx.json
```

### Publishing (Maintainers)

Images are published automatically by GitHub Actions when a version tag is pushed:

```bash
git tag v2.5.1
git push origin v2.5.1
```

The CI pipeline will lint, build, test, security-scan, publish to Docker Hub, sign the image, and attach an SBOM.

#### Required GitHub Secrets

Configure these in the repository settings under **Settings > Secrets and variables > Actions**:

| Secret | Purpose |
|--------|---------|
| `DOCKERHUB_USERNAME` | Docker Hub account username |
| `DOCKERHUB_TOKEN` | Docker Hub access token ([create one here](https://hub.docker.com/settings/security)) |

Cosign uses GitHub OIDC (keyless) — no additional secrets are needed for image signing.

#### Manual Push

```bash
make push DOCKER_REGISTRY=cyberthreatplayground
```

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Run `make setup-hooks` after cloning to activate the secret-string guard
- All scripts are tested
- Documentation is updated
- Follow existing code style
- Test with `make validate`

## 📝 License

This Docker deployment configuration is licensed under the [MIT License](LICENSE).  
DeepHunter is developed by Sebastien Damaye.

## 🆘 Support

For issues related to:
- **DeepHunter application**: See [DeepHunter documentation](https://github.com/Cyber-Threat-Hunting-Playground/deephunter)
- **Docker deployment**: Open an issue in this repository
- **Configuration help**: Check [data/settings.py](data/settings.py) comments

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MariaDB Documentation](https://mariadb.com/kb/en/)
- [Redis Documentation](https://redis.io/documentation)
