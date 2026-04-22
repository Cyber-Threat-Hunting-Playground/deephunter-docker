from django.urls import path
from . import views

urlpatterns = [
    path('deephunter-settings/', views.deephunter_settings, name='deephunter_settings'),
    path('app-settings/', views.app_settings_panel, name='app_settings_panel'),
    path('app-settings/save/', views.app_settings_save, name='app_settings_save'),
    path('app-settings/restart/', views.app_settings_restart, name='app_settings_restart'),
    path('permissions/', views.permissions, name='permissions'), 
    path('update-permission/<int:group_id>/<int:permission_id>/', views.update_permission, name='update_permission'),
    path('running-tasks/', views.running_tasks, name='running_tasks'),
    path('running-tasks-table/', views.running_tasks_table, name='running_tasks_table'),
    path('task-status/<str:task_id>/', views.task_status, name='task_status'),
    path('stop-running-task/<str:task_id>/', views.stop_running_task, name='stop_running_task'),
    path('api-keys/', views.api_keys, name='api_keys'),
    path('generate-api-key/', views.generate_api_key, name='generate_api_key'),
    path('delete-api-key/<int:pk>/', views.delete_api_key, name='delete_api_key'),
    path('ai-debug-log/', views.ai_debug_log, name='ai_debug_log'),
]
