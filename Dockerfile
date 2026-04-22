# syntax=docker/dockerfile:1
FROM debian:bookworm-slim AS builder

ARG GITHUB_REPO=Cyber-Threat-Hunting-Playground/deephunter
ARG DEEPHUNTER_VERSION=2.5

# Install prerequisites
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
	openssl \
	supervisor \
	cron \
	ca-certificates && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

# Install deephunter
# For offline/corporate builds: place v<VERSION>.tar.gz in resources/ first:
#   curl -L -o resources/v2.5.tar.gz https://github.com/<owner>/<repo>/archive/refs/tags/v2.5.tar.gz
COPY resources/ /resources

# Trust custom Root CA certificates (corporate proxies, internal services)
RUN if ls /resources/root_ca/*.crt >/dev/null 2>&1; then \
        cp /resources/root_ca/*.crt /usr/local/share/ca-certificates/ && \
        update-ca-certificates; \
    fi

RUN chmod 755 /resources/installer-v2.5-docker.sh && \
    GITHUB_REPO="${GITHUB_REPO}" DEEPHUNTER_VERSION="${DEEPHUNTER_VERSION}" \
    /resources/installer-v2.5-docker.sh

# Install REST API v2 dependencies at build time (avoids runtime pip + network)
RUN /data/venv/bin/pip install --no-cache-dir \
    djangorestframework==3.16.0 \
    drf-spectacular==0.28.0

# Enable plugins (symlink from catalog/ into the plugins package root)
RUN cd /data/deephunter/plugins && \
    ln -s /data/deephunter/plugins/catalog/sentinelone.py
#    To enable additional plugins, add more symlinks here:
#    ln -s /data/deephunter/plugins/catalog/virustotal.py && \
#    ln -s /data/deephunter/plugins/catalog/github.py && \
#    ln -s /data/deephunter/plugins/catalog/bitbucket.py

# Patch deephunter
COPY patch/dashboard/views.py /data/deephunter/dashboard/views.py
COPY patch/reports/templates/stats.html /data/deephunter/reports/templates/stats.html
COPY patch/connectors/views.py /data/deephunter/connectors/views.py
COPY patch/repos/views.py /data/deephunter/repos/views.py
#COPY patch/plugins/catalog/github.py /data/deephunter/plugins/catalog/github.py
#COPY patch/plugins/catalog/bitbucket.py /data/deephunter/plugins/catalog/bitbucket.py
COPY patch/plugins/catalog/openai_custom.py /data/deephunter/plugins/catalog/openai_custom.py
COPY patch/qm/views.py /data/deephunter/qm/views.py
COPY patch/qm/signals.py /data/deephunter/qm/signals.py
COPY patch/qm/templates/analytic_form.html /data/deephunter/qm/templates/analytic_form.html
COPY patch/qm/scripts/upgrade/fr_ai_query_log.py /data/deephunter/qm/scripts/upgrade/fr_ai_query_log.py

# AI Debug tab (config app patches)
COPY patch/config/models.py /data/deephunter/config/models.py
COPY patch/config/admin.py /data/deephunter/config/admin.py
COPY patch/config/views.py /data/deephunter/config/views.py
COPY patch/config/urls.py /data/deephunter/config/urls.py
COPY patch/config/templates/deephunter_settings.html /data/deephunter/config/templates/deephunter_settings.html
COPY patch/config/templates/partials/ai_debug_log.html /data/deephunter/config/templates/partials/ai_debug_log.html

# REST API v1 (custom ApiKey auth + session fallback)
COPY patch/deephunter/urls.py /data/deephunter/deephunter/urls.py
COPY patch/deephunter/api_auth.py /data/deephunter/deephunter/api_auth.py
COPY patch/config/decorators.py /data/deephunter/config/decorators.py

# Strip Windows CRLF from scripts and Python files (safety net for local tarballs)
RUN find /data -type f \( -name '*.py' -o -name '*.sh' \) -exec sed -i 's/\r$//' {} +

# Collect static files (admin, DRF, Swagger, etc.) into STATIC_ROOT
RUN cd /data/deephunter && /data/venv/bin/python manage.py collectstatic --noinput 2>/dev/null || true

# Install crontab
RUN mkdir -p /var/spool/cron/crontabs/ && \
    cp /data/deephunter/install/scripts/common/crontab /var/spool/cron/crontabs/root && \
    chmod 600 /var/spool/cron/crontabs/root

# Supervisor configuration
RUN mkdir -p /var/log/supervisor && \
    mv /resources/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# ── Trim build-only artifacts before copying to final stage ────────────
# Removes pip binary (attack surface), bytecode caches, temp files.
# setuptools/pkg_resources are kept (runtime need).
# NOTE: do NOT rm test/tests/testing dirs — packages like numpy.testing
# are core subpackages, not test suites, and scipy imports them at init.
RUN find /data/venv -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
    find /data/venv -name '*.pyc' -delete 2>/dev/null; \
    rm -rf /data/venv/lib/python*/site-packages/pip \
           /data/venv/lib/python*/site-packages/pip-*.dist-info; \
    rm -f  /data/venv/bin/pip /data/venv/bin/pip3 /data/venv/bin/pip3.*; \
    find /data/deephunter -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
    rm -rf /data/deephunter/docs /data/deephunter/.git; \
    rm -rf /data/tmp /resources /tmp/*.tar.gz /tmp/install.log; \
    true

# ======================================================================
# Final stage – runtime only, no build tools
# ======================================================================
FROM debian:bookworm-slim

ARG GITHUB_REPO=Cyber-Threat-Hunting-Playground/deephunter
ARG DEEPHUNTER_VERSION=2.5
ARG BUILD_DATE
ARG VCS_REF

LABEL maintainer="deephunter" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="deephunter" \
      org.label-schema.description="DeepHunter Security Analytics Platform" \
      org.label-schema.version=$DEEPHUNTER_VERSION \
      org.label-schema.vcs-url="https://github.com/${GITHUB_REPO}" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0"

# Copy application and data from builder
COPY --from=builder /data /data
COPY --from=builder /var/spool/cron /var/spool/cron
COPY --from=builder /etc/supervisor /etc/supervisor
COPY --from=builder /var/log/supervisor /var/log/supervisor

# Install runtime dependencies BEFORE overlaying custom configs to avoid
# dpkg conffile prompts that break non-interactive Docker builds.
# python3-pip deliberately excluded: venv is pre-built, pip removed to
# shrink image and reduce attack surface.
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
	openssl \
	supervisor \
	cron \
	ca-certificates \
	python3 \
	curl \
	tini \
	apache2 \
	libapache2-mod-wsgi-py3 \
	libmariadb3 && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* /var/log/apt/* /var/log/dpkg.log \
           /usr/share/doc /usr/share/man /usr/share/info /usr/share/lintian

# Apache config (sites, mods, confs enabled by the installer)
COPY --from=builder /etc/apache2 /etc/apache2
# Self-signed TLS cert and DH params generated by the installer
COPY --from=builder /etc/ssl /etc/ssl

# Trust custom Root CA certificates (corporate proxies, internal services)
COPY resources/root_ca/ /usr/local/share/ca-certificates/custom/
RUN update-ca-certificates || true

# Point Python/requests at the system CA bundle so custom Root CAs are trusted
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Create service accounts (least-privilege: separate user per daemon)
# www-data needs group write on plugins/ and deephunter/wsgi.py for connector install/toggle
RUN groupadd -r deephunter && \
    useradd -r -g deephunter -d /data/deephunter -s /sbin/nologin deephunter && \
    usermod -aG deephunter www-data && \
    groupadd -r celery && \
    useradd -r -g celery -d /nonexistent -s /sbin/nologin celery && \
    chown -R deephunter:deephunter /data/deephunter && \
    chmod g+w /data/deephunter/plugins && \
    chmod g+w /data/deephunter/deephunter/wsgi.py && \
    chown -R deephunter:deephunter /var/log/supervisor && \
    mkdir -p /var/run/celery /var/log/celery && \
    chown -R celery:celery /var/run/celery /var/log/celery

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f https://localhost:443/ -k || exit 1

EXPOSE 443

WORKDIR /data/deephunter

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
