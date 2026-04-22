from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Repo, RepoAnalytic
from .serializers import RepoSerializer, RepoAnalyticSerializer


@extend_schema_view(
    list=extend_schema(tags=['Repos']),
    retrieve=extend_schema(tags=['Repos']),
    create=extend_schema(tags=['Repos']),
    update=extend_schema(tags=['Repos']),
    partial_update=extend_schema(tags=['Repos']),
    destroy=extend_schema(tags=['Repos']),
)
class RepoViewSet(viewsets.ModelViewSet):
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'url']
    ordering_fields = ['name', 'last_check_date', 'last_import_date']


@extend_schema_view(
    list=extend_schema(tags=['Repo Analytics']),
    retrieve=extend_schema(tags=['Repo Analytics']),
    create=extend_schema(tags=['Repo Analytics']),
    update=extend_schema(tags=['Repo Analytics']),
    partial_update=extend_schema(tags=['Repo Analytics']),
    destroy=extend_schema(tags=['Repo Analytics']),
)
class RepoAnalyticViewSet(viewsets.ModelViewSet):
    serializer_class = RepoAnalyticSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

    def get_queryset(self):
        qs = RepoAnalytic.objects.select_related('repo').all()
        repo = self.request.query_params.get('repo')
        if repo:
            qs = qs.filter(repo_id=repo)
        is_valid = self.request.query_params.get('is_valid')
        if is_valid is not None:
            qs = qs.filter(is_valid=is_valid.lower() in ('true', '1'))
        return qs
