from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Country, MitreTactic, MitreTechnique, ThreatName, ThreatActor,
    TargetOs, Vulnerability, Tag, Category, Analytic,
    Campaign, Snapshot, Endpoint, TasksStatus,
    Review, SavedSearch,
)

try:
    from .models import AnalyticMeta
    HAS_ANALYTIC_META = True
except ImportError:
    HAS_ANALYTIC_META = False

try:
    from .models import CampaignCompletion
    HAS_CAMPAIGN_COMPLETION = True
except ImportError:
    HAS_CAMPAIGN_COMPLETION = False


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class MitreTacticSerializer(serializers.ModelSerializer):
    class Meta:
        model = MitreTactic
        fields = '__all__'


class MitreTechniqueListSerializer(serializers.ModelSerializer):
    parent_technique_id = serializers.PrimaryKeyRelatedField(
        source='mitre_technique', read_only=True,
    )

    class Meta:
        model = MitreTechnique
        fields = ['id', 'mitre_id', 'name', 'is_subtechnique', 'parent_technique_id']


class MitreTechniqueSerializer(serializers.ModelSerializer):
    mitre_tactic = serializers.PrimaryKeyRelatedField(
        many=True, queryset=MitreTactic.objects.all(),
    )
    tactics = MitreTacticSerializer(source='mitre_tactic', many=True, read_only=True)

    class Meta:
        model = MitreTechnique
        fields = [
            'id', 'mitre_id', 'name', 'is_subtechnique',
            'mitre_technique', 'mitre_tactic', 'tactics', 'description',
        ]


class ThreatNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatName
        fields = '__all__'


class ThreatActorSerializer(serializers.ModelSerializer):
    source_country_name = serializers.CharField(
        source='source_country.name', read_only=True, default=None,
    )

    class Meta:
        model = ThreatActor
        fields = '__all__'
        extra_fields = ['source_country_name']


class TargetOsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetOs
        fields = '__all__'


class VulnerabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerability
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# ── Analytics ──────────────────────────────────────────────────────────────

if HAS_ANALYTIC_META:
    class AnalyticMetaSerializer(serializers.ModelSerializer):
        class Meta:
            model = AnalyticMeta
            fields = [
                'analytic', 'maxhosts_count', 'query_error',
                'query_error_message', 'query_error_date',
                'next_review_date', 'last_time_seen',
            ]
            read_only_fields = ['analytic']


class AnalyticListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    connector_name = serializers.CharField(source='connector.name', read_only=True)
    repo_name = serializers.CharField(source='repo.name', read_only=True, default=None)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, default=None)

    class Meta:
        model = Analytic
        fields = [
            'id', 'name', 'status', 'confidence', 'relevance',
            'category', 'category_name',
            'connector', 'connector_name', 'repo', 'repo_name',
            'created_by', 'created_by_username',
            'run_daily', 'create_rule', 'pub_date',
        ]
        read_only_fields = ['pub_date', 'created_by', 'repo']


class AnalyticSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=False,
    )
    mitre_techniques = serializers.PrimaryKeyRelatedField(
        many=True, queryset=MitreTechnique.objects.all(), required=False,
    )
    threats = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ThreatName.objects.all(), required=False,
    )
    actors = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ThreatActor.objects.all(), required=False,
    )
    target_os = serializers.PrimaryKeyRelatedField(
        many=True, queryset=TargetOs.objects.all(), required=False,
    )
    vulnerabilities = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Vulnerability.objects.all(), required=False,
    )

    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    mitre_techniques_detail = MitreTechniqueListSerializer(
        source='mitre_techniques', many=True, read_only=True,
    )
    threats_detail = ThreatNameSerializer(source='threats', many=True, read_only=True)
    actors_detail = ThreatActorSerializer(source='actors', many=True, read_only=True)
    target_os_detail = TargetOsSerializer(source='target_os', many=True, read_only=True)
    vulnerabilities_detail = VulnerabilitySerializer(
        source='vulnerabilities', many=True, read_only=True,
    )

    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    connector_name = serializers.CharField(source='connector.name', read_only=True)
    repo_name = serializers.CharField(source='repo.name', read_only=True, default=None)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, default=None)

    class Meta:
        model = Analytic
        exclude = []
        fields = '__all__'
        read_only_fields = ['pub_date', 'created_by', 'repo']


# ── Campaigns ──────────────────────────────────────────────────────────────

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


if HAS_CAMPAIGN_COMPLETION:
    class CampaignCompletionSerializer(serializers.ModelSerializer):
        connector_name = serializers.CharField(source='connector.name', read_only=True)
        campaign_name = serializers.CharField(source='campaign.name', read_only=True)

        class Meta:
            model = CampaignCompletion
            fields = '__all__'
            extra_fields = ['connector_name', 'campaign_name']


class SnapshotSerializer(serializers.ModelSerializer):
    analytic_name = serializers.CharField(source='analytic.name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)

    class Meta:
        model = Snapshot
        fields = '__all__'
        extra_fields = ['analytic_name', 'campaign_name']


class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = '__all__'


# ── Workflow ───────────────────────────────────────────────────────────────

class TasksStatusSerializer(serializers.ModelSerializer):
    started_by_username = serializers.CharField(
        source='started_by.username', read_only=True, default=None,
    )

    class Meta:
        model = TasksStatus
        fields = '__all__'
        read_only_fields = ['date', 'started_by']
        extra_fields = ['started_by_username']


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(
        source='reviewer.username', read_only=True, default=None,
    )
    analytic_name = serializers.CharField(source='analytic.name', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['date']
        extra_fields = ['reviewer_username', 'analytic_name']


class SavedSearchSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True, default=None,
    )

    class Meta:
        model = SavedSearch
        fields = '__all__'
        read_only_fields = ['pub_date', 'update_date', 'created_by']
        extra_fields = ['created_by_username']
