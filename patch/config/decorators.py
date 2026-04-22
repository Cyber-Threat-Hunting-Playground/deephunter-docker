from functools import wraps
from django.http import JsonResponse
from .models import ApiKey

def verify_api_key(request, required_type='READ'):
    """
    Verify the API key from request headers and check permission level.
    Also allows session-authenticated Django users (read for any authenticated
    user, write only for staff), mirroring ApiKeyPermission behaviour.
    Returns None on success, or a JsonResponse with an error on failure.
    """
    user = getattr(request, 'user', None)
    if user is not None and hasattr(user, 'is_staff') and user.is_authenticated:
        if required_type != 'WRITE' or user.is_staff:
            return None

    auth_header = request.headers.get('Authorization', '')
    api_key = request.headers.get('X-API-Key', '')

    if auth_header.startswith('Bearer '):
        api_key = auth_header.split(' ')[1]

    if not api_key:
        return JsonResponse({'error': 'Unauthorized', 'detail': 'API key is missing.'}, status=401)

    try:
        key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return JsonResponse({'error': 'Forbidden', 'detail': 'Invalid API key.'}, status=403)

    if required_type == 'WRITE' and key_obj.key_type == 'READ':
        return JsonResponse({'error': 'Forbidden', 'detail': 'API key does not have write permissions.'}, status=403)

    return None


def require_api_key(required_type='READ'):
    """
    Decorator to protect API endpoints.
    Accepts keys via the Authorization header (Bearer <key>) or X-API-Key header.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            error = verify_api_key(request, required_type)
            if error:
                return error
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
