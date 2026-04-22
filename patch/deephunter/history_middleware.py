"""
Custom simple_history middleware that gracefully handles non-Django-User
request users (e.g. ApiKeyUser from API key authentication).

When request.user is not a real Django User instance, simple_history will
record the change without an associated user rather than crashing with a
ValueError on the history_user FK assignment.
"""

from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()


class _HistorySafeRequest:
    """Proxy that returns None for .user when it is not a Django User."""

    __slots__ = ("_request",)

    def __init__(self, request):
        object.__setattr__(self, "_request", request)

    @property
    def user(self):
        real_user = self._request.user
        if isinstance(real_user, User):
            return real_user
        return None

    def __getattr__(self, name):
        return getattr(self._request, name)


class SafeHistoryRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        HistoricalRecords.thread.request = _HistorySafeRequest(request)
        response = self.get_response(request)
        return response
