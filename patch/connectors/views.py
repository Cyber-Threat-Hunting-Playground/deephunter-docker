from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .forms import ConnectorConfFormSet
from connectors.models import Connector, ConnectorConf
from qm.models import Analytic
from django.contrib.auth.decorators import login_required, permission_required
from config.utils import touch
from django.conf import settings
import os
from notifications.utils import add_error_notification
import shutil

# Dynamically import all "not installed" connectors (in plugins/catalog)
import importlib
import importlib.util
import pkgutil
import logging
import plugins.catalog

logger = logging.getLogger(__name__)

all_catalog_connectors = {}
for loader, module_name, is_pkg in pkgutil.iter_modules(plugins.catalog.__path__):
    try:
        module = importlib.import_module(f"plugins.catalog.{module_name}")
        all_catalog_connectors[module_name] = module
    except Exception as exc:
        logger.warning("Failed to import catalog connector %s: %s", module_name, exc)

BASE_DIR = settings.BASE_DIR


def _extract_description(module):
    """Extract a human-readable description from a plugin's docstring."""
    doc = getattr(module, '__doc__', '') or ''
    marker = 'Description\n-----------\n'
    if marker in doc:
        return doc.split(marker, 1)[1].strip()
    return doc.strip()


def sync_catalog_connectors():
    """
    Ensure every plugin in plugins/catalog/ has a matching Connector row
    (and ConnectorConf rows) in the database.  Called each time the Catalog
    page is loaded so that newly added or updated plugins are visible
    without a manual fixture reload or upgrade script.
    """
    for module_name, module in all_catalog_connectors.items():
        try:
            if hasattr(module, 'get_connector_metadata'):
                meta = module.get_connector_metadata()
                description = meta.get('description', _extract_description(module))
                domain = meta.get('domain', '')
                connector_conf = meta.get('connector_conf', [])
            else:
                description = _extract_description(module)
                domain = ''
                connector_conf = []

            connector, _created = Connector.objects.update_or_create(
                name=module_name,
                defaults={
                    'description': description,
                    'domain': domain,
                },
            )

            for conf in connector_conf:
                ConnectorConf.objects.get_or_create(
                    connector=connector,
                    key=conf['key'],
                    defaults={
                        'value': conf.get('value', ''),
                        'fieldtype': conf.get('fieldtype', 'char'),
                        'description': conf.get('description', ''),
                    },
                )
        except Exception:
            logger.exception("Failed to sync catalog connector '%s'", module_name)


# pip distribution name -> Python import name (only where they differ)
PIP_TO_IMPORT = {
    'beautifulsoup4': 'bs4',
    'google-genai':   'google.genai',
    'Pillow':         'PIL',
}

@login_required
@permission_required('connectors.change_connectorconf', raise_exception=True)
def connector_conf(request):
    context = { 'connectors': Connector.objects.filter(installed=True).order_by('name') }
    return render(request, "connector_conf.html", context)


@login_required
@permission_required('connectors.change_connectorconf', raise_exception=True)
def selected_connector_settings(request, connector_id):
    connector = get_object_or_404(Connector, pk=connector_id, installed=True)
    qs = ConnectorConf.objects.filter(connector=connector)

    if request.method == "POST":
        formset = ConnectorConfFormSet(request.POST, queryset=qs)
        if formset.is_valid():
            formset.save()
            # Bug #233 - touch the WSGI script file to force mod_wsgi to reload Django
            # unless you do that, changes to the settings may not be applied
            touch(os.path.join(BASE_DIR, 'deephunter', 'wsgi.py'))
        
        return HttpResponseRedirect('/config/deephunter-settings/')
    
    else:
        formset = ConnectorConfFormSet(queryset=qs)

    return render(request, "selected_connector_settings.html", {
        "formset": formset,
        "connector": connector,
        "is_used": Analytic.objects.filter(connector=connector).exists(),
    })

@login_required
@permission_required('connectors.change_connectorconf', raise_exception=True)
def toggle_connector_enabled(request, connector_id):
    connector = get_object_or_404(Connector, pk=connector_id, installed=True)
    connector.enabled = not connector.enabled
    connector.save()
    return HttpResponse("")

@login_required
@permission_required('connectors.add_connector', raise_exception=True)
def catalog(request):
    return render(request, 'catalog.html')

@login_required
@permission_required('connectors.add_connector', raise_exception=True)
def filter_catalog(request):
    sync_catalog_connectors()
    connectors = Connector.objects.all()
    if request.method == "POST":

        domains = request.POST.getlist('domain')
        if domains:
            connectors = connectors.filter(domain__in=domains)

        status = request.POST.getlist('status')
        if status:
            if not 'installed' in status:
                connectors = connectors.exclude(installed=True)
            if not 'notinstalled' in status:
                connectors = connectors.exclude(installed=False)

    context = {
        'connectors': connectors.order_by('name'),
    }
    return render(request, 'partials/filtered_catalog.html', context)

def connector_prerequisites(connector_name):
    """
    Check if the prerequisites for installing a connector are met.
    :param connector_name: Name of the connector to check.
    :return: Boolean (true if prerequisites are met, false otherwise).
    """

    catalog_module = all_catalog_connectors.get(connector_name)
    if catalog_module is None:
        add_error_notification(f"Cannot install connector {connector_name}. Plugin catalog module not found.")
        return False

    get_req = getattr(catalog_module, 'get_requirements', None)
    if get_req is None:
        return True

    requirements = get_req()

    missing = []
    for requirement in requirements:
        import_name = PIP_TO_IMPORT.get(requirement, requirement)
        if importlib.util.find_spec(import_name) is None:
            missing.append(requirement)
    if missing:
        add_error_notification(f"Cannot install connector {connector_name}. Missing prerequisites: {', '.join(missing)}")
        return False

    return True


@login_required
@permission_required('connectors.add_connector', raise_exception=True)
def toggle_connector_installed(request, connector_id):

    # Only disabled connectors can be uninstalled
    connector = get_object_or_404(Connector, pk=connector_id, enabled=False)
    plugins_path = BASE_DIR / 'plugins'

    # Move the connector file to the appropriate directory
    if connector.installed:
        # Uninstall: remove the symlink
        os.remove(plugins_path / f"{connector.name}.py")
    else:

        # Check prerequisites
        if not connector_prerequisites(connector.name):
            # missing prerequisites
            return HttpResponse("Missing prerequisites", status=400)

        # Install: create a symlink
        os.symlink(plugins_path / 'catalog' / f"{connector.name}.py", plugins_path / f"{connector.name}.py")

    # touch the WSGI script file to force mod_wsgi to reload Django
    # unless you do that, changes to the settings may not be applied
    touch(os.path.join(BASE_DIR, 'deephunter', 'wsgi.py'))

    # Restart Celery so it picks up the new/removed plugin module.
    # Celery loads plugins once at import time; broadcasting shutdown
    # via Redis lets supervisord respawn the worker with the updated set.
    _restart_celery()

    # Save in DB
    connector.enabled = False
    connector.installed = not connector.installed
    connector.save()

    return HttpResponse("")


def _restart_celery():
    """Broadcast shutdown to Celery workers via the broker (Redis).

    supervisord will auto-restart the worker process, which will then
    import the current set of plugin symlinks.
    """
    try:
        from deephunter.tomato import app
        app.control.broadcast('shutdown')
    except Exception:
        pass
