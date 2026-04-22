from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Connector, ConnectorConf
from .serializers import ConnectorSerializer, ConnectorConfSerializer


@extend_schema_view(
    list=extend_schema(tags=['Connectors']),
    retrieve=extend_schema(tags=['Connectors']),
    create=extend_schema(tags=['Connectors']),
    update=extend_schema(tags=['Connectors']),
    partial_update=extend_schema(tags=['Connectors']),
    destroy=extend_schema(tags=['Connectors']),
)
class ConnectorViewSet(viewsets.ModelViewSet):
    queryset = Connector.objects.all()
    serializer_class = ConnectorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'domain']

    def get_queryset(self):
        qs = super().get_queryset()
        domain = self.request.query_params.get('domain')
        if domain:
            qs = qs.filter(domain=domain)
        enabled = self.request.query_params.get('enabled')
        if enabled is not None:
            qs = qs.filter(enabled=enabled.lower() in ('true', '1'))
        installed = self.request.query_params.get('installed')
        if installed is not None:
            qs = qs.filter(installed=installed.lower() in ('true', '1'))
        return qs


@extend_schema_view(
    list=extend_schema(tags=['Connector Config']),
    retrieve=extend_schema(tags=['Connector Config']),
    create=extend_schema(tags=['Connector Config']),
    update=extend_schema(tags=['Connector Config']),
    partial_update=extend_schema(tags=['Connector Config']),
    destroy=extend_schema(tags=['Connector Config']),
)
class ConnectorConfViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectorConfSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['key', 'description']

    def get_queryset(self):
        qs = ConnectorConf.objects.select_related('connector').all()
        connector = self.request.query_params.get('connector')
        if connector:
            qs = qs.filter(connector_id=connector)
        return qs
