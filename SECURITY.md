# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.5.x   | :white_check_mark: |
| < 2.5   | :x:                |

## Security Best Practices

### 1. Change Default Credentials
Before deploying to production:
- [ ] Update `MARIADB_ROOT_PASSWORD` in `.env`
- [ ] Update `MARIADB_PASSWORD` in `.env`
- [ ] Generate secure `SECRET_KEY` in `data/settings.py`
- [ ] Use strong passwords (16+ characters, mixed case, numbers, symbols)

### 2. Network Security & TLS
- [ ] Configure firewall to restrict access to ports
- [ ] Use HTTPS with valid certificates in production
- [ ] Add corporate Root CA certs to `resources/root_ca/*.crt` before building (see below)
- [ ] Keep Docker host updated
- [ ] Isolate Docker network from untrusted networks

### 3. Data Protection
- [ ] Enable automated backups (`crontab -e` → `make backup`)
- [ ] Store backups in secure, off-site location
- [ ] Test restore procedures regularly
- [ ] Encrypt sensitive data at rest

### 4. Container Security
- [ ] Run containers as non-root (already configured)
- [ ] Keep base images updated
- [ ] Scan images for vulnerabilities regularly
- [ ] Limit container resources (memory, CPU)

### 5. Access Control
- [ ] Use strong authentication for DeepHunter admin
- [ ] Enable 2FA if supported
- [ ] Regularly review user permissions
- [ ] Monitor access logs

### 6. Git Secret-String Guard
- [ ] Run `make setup-hooks` after cloning to activate pre-commit and pre-push hooks
- [ ] Review `.githooks/forbidden-patterns.txt` and add any project-specific sensitive terms
- [ ] Verify the guard blocks a test commit: stage a file containing a forbidden string and confirm the commit is rejected

The repository ships with git hooks (`.githooks/pre-commit` and `.githooks/pre-push`) that scan staged files and outbound diffs for forbidden strings (e.g. company names, internal product names). Patterns are read from `.githooks/forbidden-patterns.txt` (gitignored, local-only). Copy the committed template to get started:

```bash
make setup-hooks
# or manually:
cp .githooks/forbidden-patterns.txt.example .githooks/forbidden-patterns.txt
git config core.hooksPath .githooks
```

Matching is **case-insensitive** and **fixed-string** (no regex). Add one pattern per line; lines starting with `#` are comments.

### 7. Monitoring & Updates
- [ ] Monitor logs: `make logs`
- [ ] Check health: `make health`
- [ ] Update regularly: `make update`
- [ ] Subscribe to security advisories

## Reporting a Vulnerability

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email the maintainer with details:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. Allow reasonable time for response (48-72 hours)
4. Do not disclose publicly until patched

## Security Updates

Security updates will be released as soon as possible after verification.
Check `CHANGELOG.md` for security-related updates.

## Security Checklist

Before production deployment:

```bash
# 1. Activate git hooks (forbidden-string guard)
make setup-hooks

# 2. Update credentials
cp .env.example .env
nano .env  # Update all passwords

# 3. Configure secure settings
nano data/settings.py  # Update SECRET_KEY, ALLOWED_HOSTS

# 4. Enable firewall
sudo ufw allow 9000/tcp
sudo ufw enable

# 5. Set up automated backups
crontab -e
# Add: 0 2 * * * cd /path/to/deephunter-docker && make backup

# 6. Test backup/restore
make backup
make restore BACKUP_FILE=./data/backups/latest.tar.gz

# 7. Monitor
make health
make logs
```

## Custom Root CA Trust

Corporate environments often use internal Root CAs (e.g. for TLS-intercepting proxies or internal services). The Docker image automatically trusts any PEM-encoded `.crt` files placed in `resources/root_ca/` at build time.

**How it works:**
1. Place your Root CA `.crt` files in `resources/root_ca/` before building.
2. The Dockerfile copies them into `/usr/local/share/ca-certificates/` and runs `update-ca-certificates`.
3. The `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` environment variables point Python at the system CA bundle, so all outbound HTTPS (connectors, API calls) trusts these CAs.

**Privacy:** Root CA `.crt` files are excluded from git (`.gitignore`) to prevent accidental leaks to remote repositories. Each developer/operator places them locally before running `make build`.

```bash
# Example: add your corporate Root CA
cp /path/to/Corporate-Root-CA.crt resources/root_ca/
make build
```

## Known Security Considerations

1. **Self-signed certificates**: Default setup uses self-signed certs
   - **Risk**: Man-in-the-middle attacks
   - **Mitigation**: Use valid SSL certificates in production

2. **Container privileges**: Supervisor runs as root
   - **Risk**: Potential privilege escalation
   - **Mitigation**: Application processes run as non-root user

3. **Database credentials**: Stored in environment
   - **Risk**: Exposure if .env file is compromised
   - **Mitigation**: Use Docker secrets for production

4. **Root CA certificates**: Baked into the image at build time
   - **Risk**: Private CA certs could leak if the image is pushed to a public registry
   - **Mitigation**: `.crt` files are gitignored; only share images on trusted registries

5. **Sensitive strings in source code**: Company names or internal product references may be committed accidentally
   - **Risk**: Leaking organizational context to public repositories
   - **Mitigation**: Git pre-commit and pre-push hooks scan for forbidden patterns; activate with `make setup-hooks`

## Additional Resources

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
