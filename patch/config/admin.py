from django.contrib import admin
from .models import AIQueryLog, ApiKey, AppSetting, Module, ModulePermission

class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('module__name', 'action', 'description', 'permission')
    list_filter = ['module__name', 'permission']
    search_fields = ['action', 'description', 'permission']

class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_type', 'created_at', 'expires_at', 'is_expired')
    list_filter = ['key_type']
    search_fields = ['name']
    readonly_fields = ('key', 'created_at')

class AIQueryLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'connector_name', 'action', 'success', 'duration_ms')
    list_filter = ['connector_name', 'action', 'success']
    search_fields = ['input_text', 'output_text', 'error_message']
    readonly_fields = ('created_at', 'user', 'connector_name', 'action',
                       'input_text', 'output_text', 'success', 'error_message', 'duration_ms')

admin.site.register(Module)
admin.site.register(ModulePermission, ModulePermissionAdmin)
admin.site.register(ApiKey, ApiKeyAdmin)
admin.site.register(AppSetting)
admin.site.register(AIQueryLog, AIQueryLogAdmin)
