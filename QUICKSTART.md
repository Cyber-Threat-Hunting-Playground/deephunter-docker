# DeepHunter Docker - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites Check
```bash
# Verify Docker is installed and running
docker --version              # expect 20.10+
docker compose version        # expect v2.17+ (note: space, not hyphen)
```

> **Docker Compose v2 required.** This project uses `docker compose` (the CLI plugin),
> **not** the legacy standalone `docker-compose` (v1). If `docker compose version` fails,
> install the plugin:
>
> ```bash
> # Ubuntu / Debian
> sudo apt-get update && sudo apt-get install docker-compose-plugin
>
> # Fedora / RHEL
> sudo dnf install docker-compose-plugin
> ```
>
> Docker Desktop (Windows / macOS) includes it by default — update Docker Desktop if needed.
> See [README.md § Prerequisites](README.md#-prerequisites) for more details.

### Step 1: Configure Environment (1 minute)
```bash
# Copy environment template
cp .env.example .env

# Activate the git secret-string guard (prevents accidental commits of sensitive strings)
make setup-hooks

# Edit with your preferred editor
nano .env
# or
vim .env
```

**Minimum required changes:**
- Change `MARIADB_ROOT_PASSWORD`
- Change `MARIADB_PASSWORD`

**Optional — enable the scheduled orchestrator:**
```bash
ENABLE_CRON=true
CRON_SCHEDULE="30 10 * * *"   # daily at 10:30 AM UTC (default)
```

### Step 2: Configure Application Settings (Optional)
```bash
nano data/settings.py
```

**Recommended changes:**
- Update `SECRET_KEY` with a secure random string
- Update `ALLOWED_HOSTS` with your domain/IP
- Review other settings as needed

### Step 2b: Add Corporate Root CA Certificates (Optional)

If your environment uses a corporate proxy or internal services with a private Root CA, place the `.crt` files before building:

```bash
cp /path/to/Corporate-Root-CA.crt resources/root_ca/
```

They will be trusted by the system and Python inside the container. See [SECURITY.md](SECURITY.md) for details.

### Step 3: Install and Initialize (3-4 minutes)
```bash
# One command to do everything
make install
```

This will:
1. ✓ Create .env file
2. ✓ Build Docker image (~2 min)
3. ✓ Start all services
4. ✓ Initialize database
5. ✓ Create superuser (interactive)
6. ✓ Load fixtures

**During this process you'll be prompted to create an admin account:**
- Username: (your choice)
- Email: (your choice)
- Password: (your choice)

### Step 4: Access DeepHunter
```bash
# Open in your browser
https://localhost:9000
```

Login with the credentials you created in Step 3.

---

## 📝 Alternative: Manual Step-by-Step

If you prefer manual control:

```bash
# 1. Create environment
cp .env.example .env
nano .env

# 2. Build
make build

# 3. Start services
make up

# 4. Initialize
make init
```

---

## 🔧 Common Post-Installation Tasks

### View Logs
```bash
make logs          # All services
make logs-app      # Application only
```

### Check Status
```bash
make status        # Service status
make health        # Health checks
```

### Access Containers
```bash
make shell         # Application shell
make db-shell      # Database shell
make redis-shell   # Redis CLI
```

### Create Backup
```bash
make backup
```

---

## ⚠️ Troubleshooting

### Services won't start?
```bash
make status
make logs
```

### Can't connect to application?
```bash
# Check if running
docker ps | grep deephunter

# Check logs
make logs-app

# Verify port
netstat -tlnp | grep 9000
```

### Database issues?
```bash
# Check database health
docker exec deephunter-mariadb healthcheck.sh --connect

# Access database
make db-shell
```

### Need to start over?
```bash
# WARNING: Deletes all data!
make clean
make install
```

---

## 📚 Next Steps

1. **Configure integrations** - Add connectors for your security tools
2. **Create analytics** - Set up detection rules
3. **Enable the orchestrator** - Set `ENABLE_CRON=true` in `.env` and `make restart` (see [README.md § Scheduled Orchestrator](README.md#-scheduled-orchestrator-optional))
4. **Schedule backups** - `crontab -e` to automate `make backup`
5. **Harden security** - Review security checklist in README.md and [SECURITY.md](SECURITY.md)
6. **Review forbidden-patterns** - Edit `.githooks/forbidden-patterns.txt` to add project-specific sensitive terms
7. **Explore features** - Check DeepHunter documentation

---

## 🆘 Getting Help

- **Full documentation**: See [README.md](README.md)
- **Command reference**: Run `make help`
- **DeepHunter issues**: Check [original README](README.docker.txt)

---

**Time to completion:** ~5 minutes  
**Difficulty:** Easy  
**Prerequisites:** Docker Engine 20.10+, Docker Compose v2.17+ (`docker compose` CLI plugin)
