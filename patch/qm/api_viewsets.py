from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import (
    Country, MitreTactic, MitreTechnique, ThreatName, ThreatActor,
    TargetOs, Vulnerability, Tag, Category, Analytic,
    Campaign, Snapshot, Endpoint, TasksStatus,
    Review, SavedSearch,
)
from .serializers import (
    CountrySerializer, MitreTacticSerializer,
    MitreTechniqueSerializer, MitreTechniqueListSerializer,
    ThreatNameSerializer, ThreatActorSerializer,
    TargetOsSerializer, VulnerabilitySerializer,
    TagSerializer, CategorySerializer,
    AnalyticSerializer, AnalyticListSerializer,
    CampaignSerializer,
    SnapshotSerializer, EndpointSerializer,
    TasksStatusSerializer, ReviewSerializer, SavedSearchSerializer,
)

try:
    from .models import AnalyticMeta
    from .serializers import AnalyticMetaSerializer
    HAS_ANALYTIC_META = True
except ImportError:
    HAS_ANALYTIC_META = False

try:
    from .models import CampaignCompletion
    from .serializers import CampaignCompletionSerializer
    HAS_CAMPAIGN_COMPLETION = True
except ImportError:
    HAS_CAMPAIGN_COMPLETION = False


@extend_schema_view(
    list=extend_schema(tags=['Countries']),
    retrieve=extend_schema(tags=['Countries']),
    create=extend_schema(tags=['Countries']),
    update=extend_schema(tags=['Countries']),
    partial_update=extend_schema(tags=['Countries']),
    destroy=extend_schema(tags=['Countries']),
)
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']


@extend_schema_view(
    list=extend_schema(tags=['MITRE Tactics']),
    retrieve=extend_schema(tags=['MITRE Tactics']),
    create=extend_schema(tags=['MITRE Tactics']),
    update=extend_schema(tags=['MITRE Tactics']),
    partial_update=extend_schema(tags=['MITRE Tactics']),
    destroy=extend_schema(tags=['MITRE Tactics']),
)
class MitreTacticViewSet(viewsets.ModelViewSet):
    queryset = MitreTactic.objects.all()
    serializer_class = MitreTacticSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['mitre_id', 'name']
    ordering_fields = ['position', 'mitre_id', 'name']


@extend_schema_view(
    list=extend_schema(tags=['MITRE Techniques']),
    retrieve=extend_schema(tags=['MITRE Techniques']),
    create=extend_schema(tags=['MITRE Techniques']),
    update=extend_schema(tags=['MITRE Techniques']),
    partial_update=extend_schema(tags=['MITRE Techniques']),
    destroy=extend_schema(tags=['MITRE Techniques']),
)
class MitreTechniqueViewSet(viewsets.ModelViewSet):
    queryset = MitreTechnique.objects.select_related('mitre_technique').prefetch_related('mitre_tactic').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['mitre_id', 'name']
    ordering_fields = ['mitre_id', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return MitreTechniqueListSerializer
        return MitreTechniqueSerializer


@extend_schema_view(
    list=extend_schema(tags=['Threats']),
    retrieve=extend_schema(tags=['Threats']),
    create=extend_schema(tags=['Threats']),
    update=extend_schema(tags=['Threats']),
    partial_update=extend_schema(tags=['Threats']),
    destroy=extend_schema(tags=['Threats']),
)
class ThreatNameViewSet(viewsets.ModelViewSet):
    queryset = ThreatName.objects.all()
    serializer_class = ThreatNameSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'aka_name']
    ordering_fields = ['name']


@extend_schema_view(
    list=extend_schema(tags=['Threat Actors']),
    retrieve=extend_schema(tags=['Threat Actors']),
    create=extend_schema(tags=['Threat Actors']),
    update=extend_schema(tags=['Threat Actors']),
    partial_update=extend_schema(tags=['Threat Actors']),
    destroy=extend_schema(tags=['Threat Actors']),
)
class ThreatActorViewSet(viewsets.ModelViewSet):
    queryset = ThreatActor.objects.select_related('source_country').all()
    serializer_class = ThreatActorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'aka_name']
    ordering_fields = ['name']


@extend_schema_view(
    list=extend_schema(tags=['Target OS']),
    retrieve=extend_schema(tags=['Target OS']),
    create=extend_schema(tags=['Target OS']),
    update=extend_schema(tags=['Target OS']),
    partial_update=extend_schema(tags=['Target OS']),
    destroy=extend_schema(tags=['Target OS']),
)
class TargetOsViewSet(viewsets.ModelViewSet):
    queryset = TargetOs.objects.all()
    serializer_class = TargetOsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


@extend_schema_view(
    list=extend_schema(tags=['Vulnerabilities']),
    retrieve=extend_schema(tags=['Vulnerabilities']),
    create=extend_schema(tags=['Vulnerabilities']),
    update=extend_schema(tags=['Vulnerabilities']),
    partial_update=extend_schema(tags=['Vulnerabilities']),
    destroy=extend_schema(tags=['Vulnerabilities']),
)
class VulnerabilityViewSet(viewsets.ModelViewSet):
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'base_score']


@extend_schema_view(
    list=extend_schema(tags=['Tags']),
    retrieve=extend_schema(tags=['Tags']),
    create=extend_schema(tags=['Tags']),
    update=extend_schema(tags=['Tags']),
    partial_update=extend_schema(tags=['Tags']),
    destroy=extend_schema(tags=['Tags']),
)
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


@extend_schema_view(
    list=extend_schema(tags=['Categories']),
    retrieve=extend_schema(tags=['Categories']),
    create=extend_schema(tags=['Categories']),
    update=extend_schema(tags=['Categories']),
    partial_update=extend_schema(tags=['Categories']),
    destroy=extend_schema(tags=['Categories']),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'short_name']
    ordering_fields = ['name']


@extend_schema_view(
    list=extend_schema(tags=['Analytics']),
    retrieve=extend_schema(tags=['Analytics']),
    create=extend_schema(tags=['Analytics']),
    update=extend_schema(tags=['Analytics']),
    partial_update=extend_schema(tags=['Analytics']),
    destroy=extend_schema(tags=['Analytics']),
)
class AnalyticViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'query']
    ordering_fields = ['name', 'pub_date', 'status', 'confidence', 'relevance']

    def get_queryset(self):
        qs = Analytic.objects.select_related(
            'category', 'connector', 'repo', 'created_by',
        ).prefetch_related(
            'tags', 'mitre_techniques', 'threats', 'actors',
            'target_os', 'vulnerabilities',
        )
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        connector = self.request.query_params.get('connector')
        if connector:
            qs = qs.filter(connector__name=connector)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__name=category)
        run_daily = self.request.query_params.get('run_daily')
        if run_daily is not None:
            qs = qs.filter(run_daily=run_daily.lower() in ('true', '1'))
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return AnalyticListSerializer
        return AnalyticSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'pk') and hasattr(user, 'is_staff'):
            serializer.save(created_by=user)
        else:
            serializer.save()


if HAS_ANALYTIC_META:
    @extend_schema_view(
        list=extend_schema(tags=['Analytics Meta']),
        retrieve=extend_schema(tags=['Analytics Meta']),
        create=extend_schema(tags=['Analytics Meta']),
        update=extend_schema(tags=['Analytics Meta']),
        partial_update=extend_schema(tags=['Analytics Meta']),
        destroy=extend_schema(tags=['Analytics Meta']),
    )
    class AnalyticMetaViewSet(viewsets.ModelViewSet):
        queryset = AnalyticMeta.objects.select_related('analytic').all()
        serializer_class = AnalyticMetaSerializer
        filter_backends = [filters.OrderingFilter]
        ordering_fields = ['next_review_date', 'last_time_seen']


@extend_schema_view(
    list=extend_schema(tags=['Campaigns']),
    retrieve=extend_schema(tags=['Campaigns']),
    create=extend_schema(tags=['Campaigns']),
    update=extend_schema(tags=['Campaigns']),
    partial_update=extend_schema(tags=['Campaigns']),
    destroy=extend_schema(tags=['Campaigns']),
)
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'date_start', 'date_end']


if HAS_CAMPAIGN_COMPLETION:
    @extend_schema_view(
        list=extend_schema(tags=['Campaign Completions']),
        retrieve=extend_schema(tags=['Campaign Completions']),
        create=extend_schema(tags=['Campaign Completions']),
        update=extend_schema(tags=['Campaign Completions']),
        partial_update=extend_schema(tags=['Campaign Completions']),
        destroy=extend_schema(tags=['Campaign Completions']),
    )
    class CampaignCompletionViewSet(viewsets.ModelViewSet):
        queryset = CampaignCompletion.objects.select_related('campaign', 'connector').all()
        serializer_class = CampaignCompletionSerializer

        def get_queryset(self):
            qs = super().get_queryset()
            campaign = self.request.query_params.get('campaign')
            if campaign:
                qs = qs.filter(campaign_id=campaign)
            return qs


@extend_schema_view(
    list=extend_schema(tags=['Snapshots']),
    retrieve=extend_schema(tags=['Snapshots']),
    create=extend_schema(tags=['Snapshots']),
    update=extend_schema(tags=['Snapshots']),
    partial_update=extend_schema(tags=['Snapshots']),
    destroy=extend_schema(tags=['Snapshots']),
)
class SnapshotViewSet(viewsets.ModelViewSet):
    serializer_class = SnapshotSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'runtime', 'hits_count', 'hits_endpoints']

    def get_queryset(self):
        qs = Snapshot.objects.select_related('campaign', 'analytic').all()
        campaign = self.request.query_params.get('campaign')
        if campaign:
            qs = qs.filter(campaign_id=campaign)
        analytic = self.request.query_params.get('analytic')
        if analytic:
            qs = qs.filter(analytic_id=analytic)
        return qs


@extend_schema_view(
    list=extend_schema(tags=['Endpoints']),
    retrieve=extend_schema(tags=['Endpoints']),
    create=extend_schema(tags=['Endpoints']),
    update=extend_schema(tags=['Endpoints']),
    partial_update=extend_schema(tags=['Endpoints']),
    destroy=extend_schema(tags=['Endpoints']),
)
class EndpointViewSet(viewsets.ModelViewSet):
    serializer_class = EndpointSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['hostname', 'site']
    ordering_fields = ['hostname']

    def get_queryset(self):
        qs = Endpoint.objects.select_related('snapshot').all()
        snapshot = self.request.query_params.get('snapshot')
        if snapshot:
            qs = qs.filter(snapshot_id=snapshot)
        return qs


@extend_schema_view(
    list=extend_schema(tags=['Tasks']),
    retrieve=extend_schema(tags=['Tasks']),
    create=extend_schema(tags=['Tasks']),
    update=extend_schema(tags=['Tasks']),
    partial_update=extend_schema(tags=['Tasks']),
    destroy=extend_schema(tags=['Tasks']),
)
class TasksStatusViewSet(viewsets.ModelViewSet):
    queryset = TasksStatus.objects.select_related('started_by').all()
    serializer_class = TasksStatusSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['taskname']


@extend_schema_view(
    list=extend_schema(tags=['Reviews']),
    retrieve=extend_schema(tags=['Reviews']),
    create=extend_schema(tags=['Reviews']),
    update=extend_schema(tags=['Reviews']),
    partial_update=extend_schema(tags=['Reviews']),
    destroy=extend_schema(tags=['Reviews']),
)
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'decision']

    def get_queryset(self):
        qs = Review.objects.select_related('analytic', 'reviewer').all()
        analytic = self.request.query_params.get('analytic')
        if analytic:
            qs = qs.filter(analytic_id=analytic)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'pk') and hasattr(user, 'is_staff'):
            serializer.save(reviewer=user)
        else:
            serializer.save()


@extend_schema_view(
    list=extend_schema(tags=['Saved Searches']),
    retrieve=extend_schema(tags=['Saved Searches']),
    create=extend_schema(tags=['Saved Searches']),
    update=extend_schema(tags=['Saved Searches']),
    partial_update=extend_schema(tags=['Saved Searches']),
    destroy=extend_schema(tags=['Saved Searches']),
)
class SavedSearchViewSet(viewsets.ModelViewSet):
    serializer_class = SavedSearchSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'pub_date', 'update_date']

    def get_queryset(self):
        qs = SavedSearch.objects.select_related('created_by').all()
        is_public = self.request.query_params.get('is_public')
        if is_public is not None:
            qs = qs.filter(is_public=is_public.lower() in ('true', '1'))
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'pk') and hasattr(user, 'is_staff'):
            serializer.save(created_by=user)
        else:
            serializer.save()
