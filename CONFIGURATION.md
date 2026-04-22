# DeepHunter Docker - Configuration Guide

## Overview

The `data/settings.py` file contains all Django configuration for DeepHunter. This guide explains critical settings for Docker deployment.

## ⚠️ Critical Configuration Issues Fixed

### 1. Database Host Configuration

**Problem**: Default `settings.py` uses `127.0.0.1` which doesn't work in Docker

**Solution**:
```python
DATABASES = {
    'default': {
        'HOST': 'mariadb',  # Use Docker container name
        # NOT '127.0.0.1' or 'localhost'
    }
}
```

### 2. Redis/Celery Configuration

**Problem**: Default uses `localhost` which doesn't work in Docker

**Solution**:
```python
CELERY_BROKER_URL = "redis://redis:6379"  # Use Docker container name
CELERY_RESULT_BACKEND = "redis://redis:6379"
```

### 3. ALLOWED_HOSTS Syntax

**Problem**: Original has syntax error with comma inside string

**Solution**:
```python
ALLOWED_HOSTS = ['domain1.com', 'domain2.com', 'localhost', '*']
# NOT ['domain1.com,domain2.com']
```

## Required Changes Before Deployment

### 1. Generate Secure SECRET_KEY ⚠️

**Current (INSECURE)**:
```python
SECRET_KEY = 'helloworld'
```

**Generate secure key**:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Update in settings.py**:
```python
SECRET_KEY = 'your-generated-key-here'
```

### 2. Update Database Password ⚠️

**Current (INSECURE)**:
```python
DATABASES = {
    'default': {
        'PASSWORD': 'Awes0meP4ssW0rd',  # Change this!
    }
}
```

**Must match `.env` file**:
```bash
MARIADB_PASSWORD=YourSecurePassword123!
```

### 3. Configure ALLOWED_HOSTS

**For production**:
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

**For development/testing**:
```python
ALLOWED_HOSTS = ['*']  # Accept all hosts (NOT for production!)
```

### 4. Disable DEBUG in Production ⚠️

**Development**:
```python
DEBUG = True
```

**Production**:
```python
DEBUG = False
```

## Docker-Specific Settings

### Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'deephunter',              # Match MARIADB_DATABASE in .env
        'USER': 'deephunter',              # Match MARIADB_USER in .env
        'PASSWORD': 'Awes0meP4ssW0rd',    # Match MARIADB_PASSWORD in .env
        'HOST': 'mariadb',                 # Docker container name
        'PORT': '3306'
    }
}
```

### Redis Configuration

```python
CELERY_BROKER_URL = "redis://redis:6379"       # Docker container name
CELERY_RESULT_BACKEND = "redis://redis:6379"
```

## Validation

### Validate your configuration:

```bash
# Check for common issues
make validate-config

# Or manually:
./scripts/validate-config.sh
```

### Common Issues:

| Issue | Symptom | Fix |
|-------|---------|-----|
| Wrong DB host | Can't connect to database | Change `HOST` to `mariadb` |
| Wrong Redis host | Celery tasks fail | Change to `redis://redis:6379` |
| Default SECRET_KEY | Security warning | Generate new key |
| DEBUG=True | Verbose errors in prod | Set `DEBUG = False` |
| Wrong ALLOWED_HOSTS | Bad Request (400) | Add your domain |

## Environment Variable Mapping

| .env Variable | settings.py Setting | Purpose |
|---------------|-------------------|---------|
| `MARIADB_DATABASE` | `DATABASES['NAME']` | Database name |
| `MARIADB_USER` | `DATABASES['USER']` | Database user |
| `MARIADB_PASSWORD` | `DATABASES['PASSWORD']` | Database password |
| N/A | `DATABASES['HOST']` | Must be 'mariadb' |
| N/A | `CELERY_BROKER_URL` | Must be 'redis://redis:6379' |
| `ENABLE_CRON` | N/A | Enable cron sidecar (`true`/`false`, default `false`) |
| `CRON_SCHEDULE` | N/A | Cron expression for orchestrator (default `30 10 * * *`) |
| `TZ` | N/A | Timezone for cron schedule (default `UTC`) |
| `COMPOSE_PROFILES` | N/A | Set to `adminer` to enable the Adminer service |
| `ADMINER_PORT` | N/A | Host port for Adminer web UI (default `8080`) |
| `ADMINER_DB_USER` | N/A | Dedicated DB admin username created on first init |
| `ADMINER_DB_PASSWORD` | N/A | Password for the dedicated DB admin user |

## Configuration Workflow

```bash
# 1. Check current configuration
./scripts/validate-config.sh

# 2. Edit settings
nano data/settings.py

# 3. Update critical settings:
#    - SECRET_KEY (generate new)
#    - DATABASES['PASSWORD'] (match .env)
#    - ALLOWED_HOSTS (your domain)
#    - DEBUG = False (production)

# 4. Verify Docker settings:
#    - DATABASES['HOST'] = 'mariadb'
#    - CELERY_BROKER_URL = 'redis://redis:6379'

# 5. Validate again
./scripts/validate-config.sh

# 6. Restart services
make restart
```

## Optional: Database Administration UI (Adminer)

Adminer is an optional, lightweight web UI for managing the MariaDB database. It is controlled entirely via the `.env` file and disabled by default.

### Enabling Adminer

1. Set `COMPOSE_PROFILES=adminer` in `.env` (uncomment the line).
2. Configure the dedicated admin account:
   ```bash
   ADMINER_DB_USER=dbadmin
   ADMINER_DB_PASSWORD=DbAdm1nP4ssW0rd!   # change this!
   ADMINER_PORT=8080
   ```
3. If the MariaDB data directory already exists (not a fresh init), create the user manually:
   ```bash
   docker exec -i deephunter-mariadb mariadb -u root -p"$MARIADB_ROOT_PASSWORD" -e "\
     CREATE USER IF NOT EXISTS 'dbadmin'@'%' IDENTIFIED BY 'DbAdm1nP4ssW0rd!'; \
     GRANT ALL PRIVILEGES ON \`deephunter\`.* TO 'dbadmin'@'%'; \
     FLUSH PRIVILEGES;"
   ```
4. Start the stack normally (`make up` or `docker compose up -d`). Adminer will be available at `http://localhost:8080`.

### Disabling Adminer

Comment out or remove `COMPOSE_PROFILES=adminer` in `.env`. The Adminer container will not start on the next `docker compose up`.

### Logging In

Open `http://localhost:<ADMINER_PORT>` and log in with:
- **System:** MySQL
- **Server:** `mariadb` (pre-filled)
- **Username:** value of `ADMINER_DB_USER` (default `dbadmin`)
- **Password:** value of `ADMINER_DB_PASSWORD`
- **Database:** `deephunter` (or leave blank to see all granted databases)

## Security Checklist

- [ ] Generated secure SECRET_KEY (50+ characters)
- [ ] Changed database password from default
- [ ] Set DEBUG = False for production
- [ ] Configured proper ALLOWED_HOSTS (no '*' in production)
- [ ] Database HOST uses 'mariadb' (not localhost)
- [ ] Redis uses 'redis' container name (not localhost)
- [ ] Passwords match between settings.py and .env
- [ ] Activated git secret-string guard (`make setup-hooks`)
- [ ] Tested configuration with validate-config.sh

## Quick Reference

### Generate SECRET_KEY:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Generate Strong Password:
```bash
openssl rand -base64 32
```

### Test Database Connection:
```bash
make db-shell
# If this works, database config is correct
```

### Test Redis Connection:
```bash
make redis-shell
# Run: PING
# Should return: PONG
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) § Database Issues for detailed solutions.

---

**Last Updated:** December 2025  
**Status:** Critical for Docker deployment
