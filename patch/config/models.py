import logging

from django.conf import settings as django_settings
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)

class Module(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class ModulePermission(models.Model):
    """
    Permissions associated with modules.
    IMPORTANT: this table does not store groups permissions, but only lists permissions used in DeepHunter.
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    permission = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.module.name}:{self.action}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['module', 'action'], name='unique_module_action')
        ]
        ordering = ['module__name', 'action']

class ApiKey(models.Model):
    KEY_TYPES = [
        ('READ', 'Read Only'),
        ('WRITE', 'Read and Write'),
    ]
    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=64, unique=True, editable=False)
    key_type = models.CharField(max_length=10, choices=KEY_TYPES, default='READ')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Leave empty for a key that never expires.")

    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.name} ({self.key_type})"
    
    class Meta:
        ordering = ['-created_at']


class AppSetting(models.Model):
    """
    Optional overrides for values normally set in settings.py.
    If no row exists for a given key, the project reverts to Django settings.
    """

    key = models.CharField(max_length=80, unique=True, db_index=True)
    value = models.TextField(blank=True, default="")

    def __str__(self):
        return self.key

    class Meta:
        ordering = ["key"]


class AIQueryLog(models.Model):
    ACTION_CHOICES = [
        ('mitre_suggestion', 'MITRE Suggestion'),
        ('query_assistant', 'Query Assistant'),
    ]

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    connector_name = models.CharField(max_length=40)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    input_text = models.TextField()
    output_text = models.TextField(blank=True, default="")
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, default="")
    duration_ms = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} | {self.connector_name} | {self.get_action_display()}"

    class Meta:
        ordering = ["-created_at"]


def log_ai_query(*, user, connector_name, action, input_text,
                 output_text="", success=True, error_message="", duration_ms=0):
    """Create an AIQueryLog entry. Silently swallows DB errors so logging
    never breaks the caller."""
    try:
        AIQueryLog.objects.create(
            user=user,
            connector_name=connector_name,
            action=action,
            input_text=input_text,
            output_text=output_text,
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
        )
    except Exception:
        logger.exception("Failed to write AIQueryLog entry")
