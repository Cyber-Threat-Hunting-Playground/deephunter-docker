from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.views.decorators.http import require_http_methods, require_POST
from connectors.models import Connector
from .models import AIQueryLog, ApiKey, AppSetting, Module, ModulePermission
from .app_settings import SETTINGS_REGISTRY, build_settings_context, is_appsetting_table_ready
from qm.models import TasksStatus
from notifications.utils import add_debug_notification, add_error_notification, add_success_notification
from .utils import check_group_permission, touch
from celery import current_app
import os

DEBUG = settings.DEBUG

@login_required
def deephunter_settings(request):
    return render(request, 'deephunter_settings.html')


def _app_settings_ctx(**extra):
    ctx = {
        "groups": build_settings_context(),
        "table_ready": is_appsetting_table_ready(),
    }
    ctx.update(extra)
    return ctx


@login_required
@permission_required('config.view_admin', raise_exception=True)
def app_settings_panel(request):
    """
    Application settings editable from the Web GUI (overrides settings.py when saved).
    """
    return render(request, 'partials/app_settings.html', _app_settings_ctx())


_REGISTRY_KEYS = {e["key"]: e for e in SETTINGS_REGISTRY}


@login_required
@permission_required('config.view_admin', raise_exception=True)
@require_http_methods(['POST'])
def app_settings_save(request):
    """
    Generic save for any registered setting.
    POST params: key=<SETTING_KEY> value=<new_value> action=inherit|override
    """
    key = request.POST.get("key", "").strip()
    action = request.POST.get("action", "override").strip()
    value = request.POST.get("value", "").strip()

    entry = _REGISTRY_KEYS.get(key)
    if not entry:
        add_error_notification(f"Unknown setting: {key}")
        return render(request, 'partials/app_settings.html', _app_settings_ctx())

    if entry.get("readonly"):
        add_error_notification(f"{key} is read-only and cannot be changed from the GUI.")
        return render(request, 'partials/app_settings.html', _app_settings_ctx())

    try:
        if action == "inherit":
            AppSetting.objects.filter(key=key).delete()
            add_success_notification(f'{entry.get("label", key)} now follows settings.py.')
        else:
            stype = entry["type"]
            if stype == "bool":
                value = "True" if value in ("True", "true", "1", "on") else "False"
            elif stype == "int":
                try:
                    int(value)
                except (ValueError, TypeError):
                    add_error_notification(f'{entry.get("label", key)}: expected an integer.')
                    return render(request, 'partials/app_settings.html', _app_settings_ctx())
            elif stype == "choice":
                allowed = [c[0] for c in entry.get("choices", [])]
                if value not in allowed:
                    add_error_notification(f'{entry.get("label", key)}: invalid choice "{value}".')
                    return render(request, 'partials/app_settings.html', _app_settings_ctx())
            elif stype == "ai_connector":
                if value and not Connector.objects.filter(domain="ai", name=value).exists():
                    add_error_notification(f'Invalid AI connector: "{value}".')
                    return render(request, 'partials/app_settings.html', _app_settings_ctx())

            AppSetting.objects.update_or_create(key=key, defaults={"value": value})
            add_success_notification(f'{entry.get("label", key)} saved.')
    except Exception as exc:
        add_error_notification(
            f'Could not save {entry.get("label", key)}: {exc}. '
            'Make sure the config_appsetting table exists '
            '(run: python manage.py runscript upgrade.fr_327_app_setting).'
        )

    return render(request, 'partials/app_settings.html', _app_settings_ctx())


@login_required
@permission_required('config.view_admin', raise_exception=True)
@require_http_methods(['POST'])
def app_settings_restart(request):
    """
    Touch wsgi.py to force mod_wsgi to reload Django, and restart Celery
    so workers pick up the updated AppSetting values.
    """
    try:
        wsgi_path = os.path.join(settings.BASE_DIR, 'deephunter', 'wsgi.py')
        touch(wsgi_path)
    except Exception as exc:
        add_error_notification(f'Failed to touch wsgi.py: {exc}')

    try:
        current_app.control.broadcast('shutdown')
    except Exception:
        pass

    add_success_notification('Application restart triggered. Changes will take effect momentarily.')
    return render(request, 'partials/app_settings.html', _app_settings_ctx(restart_triggered=True))


@login_required
@permission_required('config.change_modulepermission', raise_exception=True)
def permissions(request):
    groups = Group.objects.order_by('name')
    modules = []
    for module in Module.objects.all():
        permissions = []
        for permission in module.modulepermission_set.all():
            group_permission = []
            for group in groups:
                group_permission.append({
                    'group_id': group.id,
                    'name': group.name,
                    'has_perm': check_group_permission(group.name, permission.permission),
                })
            permissions.append({
                'permission_id': permission.id,
                'action': permission.action,
                'description': permission.description,
                'permission': permission.permission,
                'groups': group_permission,
            })
        modules.append({
            'module': module.name,
            'permissions': permissions,
        })

    context = {
        'groups': [group.name for group in Group.objects.order_by('name')],
        'modules': modules,
    }
    return render(request, 'permissions.html', context)

@login_required
@permission_required('config.change_modulepermission', raise_exception=True)
def update_permission(request, group_id, permission_id):

    group = get_object_or_404(Group, id=group_id)
    permission = get_object_or_404(ModulePermission, id=permission_id)
    group_permission = check_group_permission(group.name, permission.permission)

    perm_app_label, perm_codename = permission.permission.split('.')
    perm = get_object_or_404(Permission, codename=perm_codename, content_type__app_label=perm_app_label)
    if group_permission:
        # Remove permission
        group.permissions.remove(perm)
        if DEBUG:
            add_debug_notification(f"Removed {permission.permission} from {group.name}")
    else:
        # Add permission
        group.permissions.add(perm)
        if DEBUG:
            add_debug_notification(f"Added {permission.permission} to {group.name}")
    return HttpResponse(status=204)

@login_required
@permission_required('qm.delete_tasksstatus', raise_exception=True)
def running_tasks(request):
    return render(request, 'running_tasks.html')

@login_required
@permission_required('qm.delete_tasksstatus', raise_exception=True)
def running_tasks_table(request):
    context = {
        'running_tasks': TasksStatus.objects.all(),
    }
    return render(request, 'partials/running_tasks_table.html', context)

@login_required
@permission_required('qm.delete_tasksstatus', raise_exception=True)
def task_status(request, task_id):
    task_status = get_object_or_404(TasksStatus, pk=task_id)
    code = f"{round(task_status.progress)}%"
    if task_status.taskid:
        code += f' | <button class="buttonred" hx-get="/config/stop-running-task/{task_status.id}/" hx-swap="outerHTML">Stop</button>'
    return HttpResponse(code)

@login_required
@permission_required('qm.delete_tasksstatus', raise_exception=True)
def stop_running_task(request, task_id):
    try:
        task = get_object_or_404(TasksStatus, pk=task_id)
        # without signal='SIGKILL', the task is not cancelled immediately
        current_app.control.revoke(task.taskid, terminate=True, signal='SIGKILL')
        # delete task in DB
        celery_status = get_object_or_404(TasksStatus, taskid=task.taskid)
        celery_status.delete()
        add_success_notification(f'Celery Task {task.taskname} terminated')
        return HttpResponse('Task terminated')
    except Exception as e:
        add_error_notification(f'Error terminating Celery Task: {e}')
        return HttpResponse(f'Error terminating Celery Task: {e}')

import secrets
from datetime import timedelta
from django.utils import timezone

EXPIRATION_CHOICES = [
    ('1d',   '1 day'),
    ('7d',   '7 days'),
    ('30d',  '30 days'),
    ('90d',  '90 days'),
    ('180d', '180 days'),
    ('1y',   '1 year'),
    ('2y',   '2 years'),
    ('never', 'Never'),
]

EXPIRATION_DELTAS = {
    '1d':   timedelta(days=1),
    '7d':   timedelta(days=7),
    '30d':  timedelta(days=30),
    '90d':  timedelta(days=90),
    '180d': timedelta(days=180),
    '1y':   timedelta(days=365),
    '2y':   timedelta(days=730),
}

@login_required
@permission_required('config.view_admin', raise_exception=True)
def api_keys(request):
    keys = ApiKey.objects.all()
    return render(request, 'api_keys.html', {
        'api_keys': keys,
        'expiration_choices': EXPIRATION_CHOICES,
    })

@login_required
@permission_required('config.view_admin', raise_exception=True)
@require_POST
def generate_api_key(request):
    name = request.POST.get('name', '').strip()
    key_type = request.POST.get('key_type', 'READ')
    expiration = request.POST.get('expiration', 'never')

    if name:
        new_key = secrets.token_urlsafe(32)
        expires_at = None
        if expiration in EXPIRATION_DELTAS:
            expires_at = timezone.now() + EXPIRATION_DELTAS[expiration]
        ApiKey.objects.create(name=name, key=new_key, key_type=key_type, expires_at=expires_at)
        add_success_notification(f"Created new API key: {name}")
    else:
        add_error_notification("A name is required for the new API key.")
    
    keys = ApiKey.objects.all()
    return render(request, 'api_keys.html', {
        'api_keys': keys,
        'expiration_choices': EXPIRATION_CHOICES,
    })

@login_required
@permission_required('config.view_admin', raise_exception=True)
@require_POST
def delete_api_key(request, pk):
    key = get_object_or_404(ApiKey, pk=pk)
    name = key.name
    key.delete()
    add_success_notification(f"Deleted API key: {name}")
    
    keys = ApiKey.objects.all()
    return render(request, 'api_keys.html', {
        'api_keys': keys,
        'expiration_choices': EXPIRATION_CHOICES,
    })


@login_required
@permission_required('config.view_admin', raise_exception=True)
def ai_debug_log(request):
    qs = AIQueryLog.objects.select_related('user').all()

    connector = request.GET.get('connector', '')
    action = request.GET.get('action', '')
    success = request.GET.get('success', '')

    if connector:
        qs = qs.filter(connector_name=connector)
    if action:
        qs = qs.filter(action=action)
    if success in ('1', '0'):
        qs = qs.filter(success=(success == '1'))

    logs = qs[:200]

    connector_choices = (
        AIQueryLog.objects.values_list('connector_name', flat=True)
        .distinct()
        .order_by('connector_name')
    )

    return render(request, 'partials/ai_debug_log.html', {
        'logs': logs,
        'connector_choices': connector_choices,
        'action_choices': AIQueryLog.ACTION_CHOICES,
        'f_connector': connector,
        'f_action': action,
        'f_success': success,
    })
