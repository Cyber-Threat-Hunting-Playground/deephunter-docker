# DeepHunter Docker — uninstall and start fresh

This document describes how to **fully remove** the running stack and **local application data** so the next `make up` behaves like a **first-time install**. It does not remove the project files, `.env`, or the `deephunter:latest` image unless you choose those optional steps.

---

## 1. Understand what is stored where

| Location | Purpose |
|----------|---------|
| Docker containers | `deephunter-redis`, `deephunter-mariadb`, `deephunter-app` (fixed names in `docker-compose.yml`) |
| Docker network | `deephunter-docker_backend` (or similar project-prefixed name) |
| Host directory `data/mariadb/` | MariaDB data files (bind mount) |
| Host directory `data/redis/` | Redis persistence (bind mount) |
| Host directory `data/logs/` | Application logs |
| Host directory `data/backups/` | Backups |
| Host file `data/settings.py` | App settings (not deleted by default below) |

This project uses **bind mounts** for database and Redis data, not Compose named volumes for those services. Clearing **`data/mariadb`** and **`data/redis`** is what forces MariaDB and Redis to **re-initialize** on the next start.

---

## 2. Full reset (recommended “start fresh” procedure)

Run these from the **project root** (the directory that contains `docker-compose.yml` and `Makefile`).

### 2.1 Stop and remove the stack

```bash
docker compose down
```

If Compose reports conflicts or leftover containers:

```bash
docker rm -f deephunter-app deephunter-mariadb deephunter-redis 2>/dev/null || true
docker compose down
```

### 2.2 Delete local data (destructive)

**This removes the database, Redis data, logs, and backups under `data/`.** Copy anything you need before continuing.

```bash
sudo rm -rf data/mariadb/* data/redis/* data/logs/* data/backups/*
```

On some systems, MariaDB files are owned by UID `999`; if `rm` fails with permission errors:

```bash
sudo chown -R "$(id -u):$(id -g)" data/mariadb data/redis 2>/dev/null || true
sudo rm -rf data/mariadb/* data/redis/* data/logs/* data/backups/*
```

Leave the **directories** `data/mariadb`, `data/redis`, etc. in place (or recreate empty dirs); `make up` creates them if missing.

### 2.3 Optional: reset application settings

To restore default settings from the repo (only if you keep a template in-tree or know what to restore):

```bash
# Example only — adjust if your workflow uses a different template path
# cp path/to/default/settings.py data/settings.py
```

If you do nothing here, your existing `data/settings.py` is reused.

### 2.4 Optional: remove the DeepHunter image

Use this if you want a **clean rebuild** of the application image:

```bash
docker rmi deephunter:latest
```

### 2.5 Optional: prune unused Docker resources

Only if you want to reclaim disk space (affects **other** projects too if you use broad prune):

```bash
docker system prune -f
# Stronger (removes unused images, not just dangling):
# docker system prune -af
```

---

## 3. Using `make clean` (interactive shortcut)

The Makefile target **`make clean`** runs `docker compose down -v` and removes contents under `data/mariadb`, `data/redis`, `data/logs`, and `data/backups` after confirmation. It is equivalent in spirit to sections 2.1–2.2, with a prompt:

```bash
make clean
```

Use **`y`** only when you accept total loss of that local data.

---

## 4. Before you bring the stack up again

1. **`.env`**
   - Ensure **`MARIADB_ROOT_PASSWORD`** is set to a **non-empty** value (no `MARIADB_ROOT_PASSWORD=` with nothing after `=`).
   - Keep **`MARIADB_PASSWORD`** and app DB settings aligned with what DeepHunter expects (`docker-compose.yml` / `data/settings.py`).

2. **WSL / Windows drives**
   - If the project lives under **`/mnt/c/...`**, MariaDB on a bind-mounted Windows filesystem can stay **unhealthy** (I/O / permissions). For reliability, use a clone under the Linux filesystem (e.g. **`$HOME/deephunter-docker`**) and run the same steps there.

3. **Recreate directories** (if you removed the whole `data` tree):

   ```bash
   mkdir -p data/mariadb data/redis data/logs data/backups
   ```

---

## 5. Fresh install sequence

From project root:

```bash
make build    # if you removed the image or changed the Dockerfile
make up
```

Check MariaDB:

```bash
docker ps
docker logs deephunter-mariadb 2>&1 | tail -80
```

When MariaDB and Redis are healthy and the app container is up:

```bash
make init
```

---

## 6. If MariaDB is still unhealthy after a full reset

1. Capture logs: `docker logs deephunter-mariadb 2>&1 | tail -100`
2. Confirm **`data/mariadb`** is empty before the first `make up` after reset.
3. On Linux/WSL, try: `sudo chown -R 999:999 data/mariadb` **only on an empty** `data/mariadb`, then `make down` and `make up` again.
4. Temporarily increase MariaDB **`healthcheck`** `start_period` in `docker-compose.yml` (e.g. 120s–180s) if the host disk is very slow.

---

## 7. Complete removal (optional)

To remove the stack and **also** delete the local project checkout (irreversible):

1. Complete sections **2.1** and **2.2** (and optional **2.4**).
2. Delete the project directory yourself (e.g. `rm -rf` the repo folder).

Docker images, volumes, and networks used **only** by this project are already addressed by `docker compose down` and the data cleanup above; other images remain until you run `docker rmi` / `docker system prune` yourself.
