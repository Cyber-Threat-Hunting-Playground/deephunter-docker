# DeepHunter Docker - Troubleshooting Guide

## Table of Contents
- [Pre-Installation Issues](#pre-installation-issues)
- [Build Issues](#build-issues)
- [Startup Issues](#startup-issues)
- [Runtime Issues](#runtime-issues)
- [Database Issues](#database-issues)
- [Network Issues](#network-issues)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)

---

## Pre-Installation Issues

### Docker or Docker Compose not installed / wrong version

**Symptoms:**
```
Cannot connect to the Docker daemon
docker: 'compose' is not a docker command
```

**Solution:**
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Enable Docker on boot
sudo systemctl enable docker

# Verify Docker Compose v2 plugin is installed (space, not hyphen)
docker compose version        # expect v2.17+
```

If `docker compose version` fails, install the Compose plugin:

```bash
# Ubuntu / Debian
sudo apt-get update && sudo apt-get install docker-compose-plugin

# Fedora / RHEL / CentOS
sudo dnf install docker-compose-plugin
```

> **Important:** The legacy standalone `docker-compose` (v1) is **not supported**.
> It does not honour `start_period` in health checks, causing intermittent startup
> failures. See [README.md § Prerequisites](README.md#-prerequisites) for details.

### Insufficient permissions

**Symptoms:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

### System requirements not met

**Solution:**
```bash
# Check requirements
make check-requirements

# View detailed system info
docker info
free -h
df -h
```

---

## Build Issues

### Build fails with "No space left on device"

**Solution:**
```bash
# Clean up Docker
docker system prune -a
docker volume prune

# Check disk space
df -h
```

### Build fails with network errors

**Symptoms:**
```
Failed to fetch packages
Could not resolve host
ERROR: Script failed at line 104. Check /tmp/install.log.
```

**Solution 1 – Offline build (recommended for corporate/proxy environments):**

If the build fails during "DOWNLOADING DEEPHUNTER", download the tarball manually and bundle it:

```bash
# Download DeepHunter source (run from project root, outside Docker)
curl -L -o resources/v2.5.tar.gz https://github.com/Cyber-Threat-Hunting-Playground/deephunter/archive/refs/tags/v2.5.tar.gz

# Rebuild – installer will use the bundled tarball instead of fetching
make build
```

**Solution 2 – Fix Docker network:**

```bash
# Check network
ping google.com

# Configure DNS in Docker
sudo nano /etc/docker/daemon.json
# Add:
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}

# Restart Docker
sudo systemctl restart docker

# Retry build
make build
```

### Build cache issues

**Solution:**
```bash
# Build without cache
docker build --no-cache -t deephunter:latest ./

# Or clean and rebuild
make clean
make build
```

---

## Startup Issues

### Containers won't start

**Diagnosis:**
```bash
# Check status
make status

# View logs
make logs

# Check specific container
docker logs deephunter-app
docker logs deephunter-mariadb
docker logs deephunter-redis
```

### Port already in use

**Symptoms:**
```
Bind for 0.0.0.0:9000 failed: port is already allocated
```

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :9000
sudo netstat -tlnp | grep 9000

# Kill the process or change port
nano .env
# Change: DEEPHUNTER_PORT=9001

# Restart
make restart
```

### MariaDB fails to start

**Symptoms:**
```
mariadb exited with code 1
```

**Solutions:**

1. Check logs:
```bash
make logs-db
```

2. Permissions issue:
```bash
sudo chown -R 999:999 data/mariadb/
```

3. Corrupted data:
```bash
# Backup first!
make down
mv data/mariadb data/mariadb.old
make up
```

### Health check failures

**Symptoms:**
```
Container is unhealthy
```

**Diagnosis:**
```bash
# Check health status
make health
docker inspect deephunter-app --format='{{.State.Health.Status}}'

# View health check logs
docker inspect deephunter-app --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```

**Solution:**
```bash
# Wait longer (health checks need time)
# Increase start_period in docker-compose.yml if needed
# NOTE: requires Docker Compose v2 (docker compose) to honour start_period

# Check if service is actually running
make shell
curl -k https://localhost:443/
```

---

## Runtime Issues

### Cannot access web interface

**Symptoms:**
- Browser shows "Connection refused"
- "This site can't be reached"

**Solutions:**

1. Check if container is running:
```bash
make status
docker ps | grep deephunter
```

2. Check if port is accessible:
```bash
curl -k https://localhost:9000/
netstat -tlnp | grep 9000
```

3. Check firewall:
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 9000/tcp

# CentOS/RHEL
sudo firewall-cmd --list-all
sudo firewall-cmd --add-port=9000/tcp --permanent
sudo firewall-cmd --reload
```

4. Check if using correct URL:
```
https://localhost:9000  ✓
http://localhost:9000   ✗ (HTTPS only)
```

### SSL/Certificate errors

**Symptoms (browser):**
```
NET::ERR_CERT_AUTHORITY_INVALID
```

**Solution:**
- This is expected with self-signed certificates
- Click "Advanced" → "Proceed anyway" in browser
- For production, use valid SSL certificates

### Python / connector HTTPS errors (corporate proxy or internal services)

**Symptoms:**
```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
requests.exceptions.SSLError: ... unable to get local issuer certificate
```

**Solution:** Place your corporate Root CA certificate(s) in `resources/root_ca/` and rebuild:

```bash
cp /path/to/Corporate-Root-CA.crt resources/root_ca/
make build
make restart
```

The Dockerfile installs these into the system trust store and sets `SSL_CERT_FILE` / `REQUESTS_CA_BUNDLE` so Python trusts them. See [SECURITY.md](SECURITY.md) for details.

### Application errors after initialization

**Solution:**
```bash
# Check application logs
make logs-app

# Access container for debugging
make shell

# Check Django settings
cat /data/deephunter/deephunter/settings.py

# Restart application
make restart
```

---

## Database Issues

### Cannot connect to database

**Diagnosis:**
```bash
# Check database health
make db-shell

# From app container
make shell
mysql -h mariadb -u deephunter -p
```

**Solutions:**

1. Wrong credentials:
```bash
# Check .env file
cat .env | grep MARIADB

# Update if needed
nano .env
make restart
```

2. Database not initialized:
```bash
make init
```

3. Database corruption:
```bash
# Restore from backup
make restore BACKUP_FILE=./data/backups/latest.tar.gz
```

### Database is slow

**Solutions:**

1. Check resources:
```bash
docker stats deephunter-mariadb
```

2. Optimize configuration:
```yaml
# In docker-compose.yml adjust:
--innodb_buffer_pool_size=512M  # Increase if you have RAM
--max_connections=500            # Increase if needed
```

3. Check disk I/O:
```bash
iostat -x 1
```

### Database migrations fail

**Solution:**
```bash
# Access container
make shell

# Check migration status
source /data/venv/bin/activate
cd /data/deephunter
./manage.py showmigrations

# Apply migrations manually
./manage.py migrate --fake-initial
```

---

## Network Issues

### Containers can't communicate

**Diagnosis:**
```bash
# Check network
docker network ls
docker network inspect deephunter-docker_backend

# Test connectivity
docker exec deephunter-app ping mariadb
docker exec deephunter-app ping redis
```

**Solution:**
```bash
# Recreate network
make down
docker network prune
make up
```

### DNS resolution issues

**Solution:**
```bash
# In docker-compose.yml add to each service:
dns:
  - 8.8.8.8
  - 8.8.4.4
```

---

## Performance Issues

### High CPU usage

**Diagnosis:**
```bash
docker stats
top
```

**Solutions:**
1. Limit resources in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

2. Check for infinite loops in logs:
```bash
make logs-app
```

### High memory usage

**Solutions:**
1. Increase swap if needed
2. Reduce Redis memory limit
3. Optimize MariaDB buffer pool
4. Check for memory leaks in logs

### Slow response times

**Diagnosis:**
```bash
# Check all services
docker stats

# Check disk I/O
iotop

# Check network
iftop
```

**Solutions:**
1. Add more resources
2. Optimize database queries
3. Increase Redis memory
4. Use SSD for data volumes

---

## Common Error Messages

### "no space left on device"

```bash
# Clean Docker
docker system prune -a -f
docker volume prune -f

# Check disk usage
df -h
du -sh data/*
```

### "network not found"

```bash
make down
docker network prune
make up
```

### "container name already in use"

```bash
# Remove old containers
docker rm -f deephunter-app deephunter-mariadb deephunter-redis

# Or
make down
make up
```

### "no such file or directory"

**Solution:**
```bash
# Create missing directories
mkdir -p data/{mariadb,redis,logs,backups}

# Check permissions
ls -la data/
```

### "permission denied"

```bash
# Fix ownership
sudo chown -R $USER:$USER data/

# Fix Docker permissions
sudo chown -R 999:999 data/mariadb/
```

---

## Advanced Debugging

### Enable debug mode

1. Edit [data/settings.py](data/settings.py):
```python
DEBUG = True
```

2. Restart:
```bash
make restart
```

### View detailed container info

```bash
docker inspect deephunter-app
docker inspect deephunter-mariadb
docker inspect deephunter-redis
```

### Access container as root

```bash
docker exec -it -u root deephunter-app bash
```

### Check supervisord processes

```bash
make shell
supervisorctl status
supervisorctl tail deephunter
```

### Export logs for support

```bash
# Export all logs
docker compose logs > deephunter-logs.txt

# Or specific service
make logs-app > app-logs.txt
```

---

## Still Having Issues?

### Gather diagnostic information:

```bash
# System info
make check-requirements > diagnostics.txt

# Container status
make status >> diagnostics.txt

# Health status
make health >> diagnostics.txt

# Recent logs
make logs --tail=100 >> diagnostics.txt

# Docker info
docker info >> diagnostics.txt
docker compose config >> diagnostics.txt
```

### Reset to clean state:

```bash
# WARNING: This deletes all data!
make clean
rm -rf data/
make install
```

### Check documentation:
- [README.md](README.md) - Main guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start
- [SECURITY.md](SECURITY.md) - Security guide
- [Original docs](README.docker.txt) - Original instructions

---

## Quick Command Reference

```bash
make status          # Check what's running
make health          # Check health status
make logs            # View all logs
make logs-app        # View app logs only
make shell           # Access app container
make db-shell        # Access database
make restart         # Restart everything
make backup          # Create backup
make validate        # Check configuration
```

---

**Last Updated:** December 2025
