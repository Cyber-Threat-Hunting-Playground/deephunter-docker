#!/bin/bash
# DeepHunter application initialization script
# Run this after docker-compose up to initialize the application

set -e

CONTAINER_NAME="${1:-deephunter-app}"

echo "==================================="
echo "DeepHunter Initialization Script"
echo "==================================="
echo ""

# Check if container exists and is running
if ! docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME" 2>/dev/null | grep -q true; then
    echo "Error: Container $CONTAINER_NAME is not running (or does not exist yet)."
    echo ""
    echo "Start the stack first, then run init again:"
    echo "  make build   # if you have not built the image yet"
    echo "  make up      # or: docker compose up -d"
    echo "  make init"
    echo ""
    echo "Or run a full first-time install: make install"
    exit 1
fi

echo "Step 1: Preparing database migrations..."
docker exec -it "$CONTAINER_NAME" bash -c "
    source /data/venv/bin/activate && \
    sed -i 's/import qm.signals/pass #import qm.signals/' /data/deephunter/qm/apps.py
"

echo ""
echo "Step 2: Running migrations..."
docker exec -it "$CONTAINER_NAME" bash -c "
    source /data/venv/bin/activate && cd /data/deephunter && \
    ./manage.py makemigrations qm && \
    ./manage.py makemigrations extensions && \
    ./manage.py makemigrations reports && \
    ./manage.py makemigrations connectors && \
    ./manage.py makemigrations repos && \
    ./manage.py makemigrations notifications && \
    ./manage.py makemigrations dashboard && \
    ./manage.py makemigrations config && \
    ./manage.py makemigrations && \
    ./manage.py migrate
"

echo ""
echo "Step 3: Creating superuser..."
printf "Do you want to create an admin account now? [Y/n] "
read -r CREATE_ACCOUNT
case "$CREATE_ACCOUNT" in
    [Nn]*)
        echo "Skipping superuser creation. You can create one later with:"
        echo "  docker exec -it $CONTAINER_NAME bash -c 'source /data/venv/bin/activate && cd /data/deephunter && ./manage.py createsuperuser'"
        ;;
    *)
        echo "Please follow the prompts to create your admin account:"
        docker exec -it "$CONTAINER_NAME" bash -c "
            source /data/venv/bin/activate && cd /data/deephunter && \
            ./manage.py createsuperuser
        "
        ;;
esac

echo ""
echo "Step 4: Loading fixtures..."
docker exec -it "$CONTAINER_NAME" bash -c "
    source /data/venv/bin/activate && cd /data/deephunter && \
    ./manage.py loaddata install/fixtures/v2.5/qm_country.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_threatactor.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_threatname.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_vulnerability.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_mitretactic.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_mitretechnique.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_tag.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_category.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_targetos.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_savedsearch.json && \
    ./manage.py loaddata install/fixtures/v2.5/config.json && \
    sed -i 's|\"visible_in_analytics\": true|\"domain\": \"analytics\"|' install/fixtures/v2.5/connectors.json && \
    sed -i 's|\"visible_in_analytics\": false|\"domain\": \"\"|' install/fixtures/v2.5/connectors.json && \
    ./manage.py loaddata install/fixtures/v2.5/connectors.json && \
    ./manage.py loaddata install/fixtures/v2.5/qm_analytic.json
"

echo ""
echo "Step 5: Finalizing setup..."
docker exec -it "$CONTAINER_NAME" bash -c "
    source /data/venv/bin/activate && \
    sed -i 's/pass #import qm.signals/import qm.signals/' /data/deephunter/qm/apps.py && \
    cd /data/deephunter && \
    ./manage.py shell -c \"
from connectors.models import Connector
import os, pathlib
plugins_dir = pathlib.Path('/data/deephunter/plugins')
for name in [f.stem for f in plugins_dir.glob('*.py') if f.is_symlink()]:
    Connector.objects.filter(name=name).update(installed=True, enabled=True)
    print(f'  Enabled connector: {name}')
\"
"

echo ""
echo "==================================="
echo "Initialization Complete!"
echo "==================================="
echo ""
echo "You can now access DeepHunter at: https://localhost:9000 or any other address that fits your .env configuration"
echo ""
echo "Note: If you encounter the Microsoft Sentinel bug, you can:"
echo "  1. Enable the Microsoft Sentinel plugin, or"
echo "  2. Delete the Microsoft Sentinel analytic rule from the admin settings"
echo ""
