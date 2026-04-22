from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.contrib.auth.models import User
from .models import Module, ModulePermission
from .serializers import (
    ModuleSerializer, ModulePermissionSerializer, UserSerializer,
)

try:
    from .models import ApiKey
    from .serializers import ApiKeySerializer
    HAS_APIKEY = True
except ImportError:
    HAS_APIKEY = False


@extend_schema_view(
    list=extend_schema(tags=['Modules']),
    retrieve=extend_schema(tags=['Modules']),
    create=extend_schema(tags=['Modules']),
    update=extend_schema(tags=['Modules']),
    partial_update=extend_schema(tags=['Modules']),
    destroy=extend_schema(tags=['Modules']),
)
class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


@extend_schema_view(
    list=extend_schema(tags=['Module Permissions']),
    retrieve=extend_schema(tags=['Module Permissions']),
    create=extend_schema(tags=['Module Permissions']),
    update=extend_schema(tags=['Module Permissions']),
    partial_update=extend_schema(tags=['Module Permissions']),
    destroy=extend_schema(tags=['Module Permissions']),
)
class ModulePermissionViewSet(viewsets.ModelViewSet):
    serializer_class = ModulePermissionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['action', 'permission', 'description']

    def get_queryset(self):
        qs = ModulePermission.objects.select_related('module').all()
        module = self.request.query_params.get('module')
        if module:
            qs = qs.filter(module_id=module)
        return qs


if HAS_APIKEY:
    @extend_schema_view(
        list=extend_schema(tags=['API Keys']),
        retrieve=extend_schema(tags=['API Keys']),
        create=extend_schema(tags=['API Keys']),
        update=extend_schema(tags=['API Keys']),
        partial_update=extend_schema(tags=['API Keys']),
        destroy=extend_schema(tags=['API Keys']),
    )
    class ApiKeyViewSet(viewsets.ModelViewSet):
        queryset = ApiKey.objects.all()
        serializer_class = ApiKeySerializer
        filter_backends = [filters.SearchFilter, filters.OrderingFilter]
        search_fields = ['name']
        ordering_fields = ['name', 'created_at', 'key_type']


@extend_schema_view(
    list=extend_schema(tags=['Users']),
    retrieve=extend_schema(tags=['Users']),
    create=extend_schema(tags=['Users']),
    update=extend_schema(tags=['Users']),
    partial_update=extend_schema(tags=['Users']),
    destroy=extend_schema(tags=['Users']),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('groups').all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'last_login']
