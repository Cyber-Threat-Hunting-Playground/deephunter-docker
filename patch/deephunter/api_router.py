from rest_framework.routers import DefaultRouter

from qm.api_viewsets import (
    CountryViewSet, MitreTacticViewSet, MitreTechniqueViewSet,
    ThreatNameViewSet, ThreatActorViewSet, TargetOsViewSet,
    VulnerabilityViewSet, TagViewSet, CategoryViewSet,
    AnalyticViewSet,
    CampaignViewSet,
    SnapshotViewSet, EndpointViewSet,
    TasksStatusViewSet, ReviewViewSet, SavedSearchViewSet,
)
from connectors.api_viewsets import ConnectorViewSet, ConnectorConfViewSet
from repos.api_viewsets import RepoViewSet, RepoAnalyticViewSet
from notifications.api_viewsets import NotificationViewSet, UserNotificationViewSet
from config.api_viewsets import (
    ModuleViewSet, ModulePermissionViewSet, UserViewSet,
)

router = DefaultRouter()

# QM – analytics & threat intelligence
router.register('analytics', AnalyticViewSet, basename='analytic')
router.register('categories', CategoryViewSet, basename='category')
router.register('tactics', MitreTacticViewSet, basename='mitretactic')
router.register('techniques', MitreTechniqueViewSet, basename='mitretechnique')
router.register('threats', ThreatNameViewSet, basename='threatname')
router.register('actors', ThreatActorViewSet, basename='threatactor')
router.register('countries', CountryViewSet, basename='country')
router.register('target-os', TargetOsViewSet, basename='targetos')
router.register('vulnerabilities', VulnerabilityViewSet, basename='vulnerability')
router.register('tags', TagViewSet, basename='tag')

# QM – campaigns & snapshots
router.register('campaigns', CampaignViewSet, basename='campaign')
router.register('snapshots', SnapshotViewSet, basename='snapshot')
router.register('endpoints', EndpointViewSet, basename='endpoint')

# QM – workflow
router.register('reviews', ReviewViewSet, basename='review')
router.register('saved-searches', SavedSearchViewSet, basename='savedsearch')
router.register('tasks', TasksStatusViewSet, basename='tasksstatus')

# Connectors
router.register('connectors', ConnectorViewSet, basename='connector')
router.register('connector-config', ConnectorConfViewSet, basename='connectorconf')

# Repos
router.register('repos', RepoViewSet, basename='repo')
router.register('repo-analytics', RepoAnalyticViewSet, basename='repoanalytic')

# Notifications
router.register('notifications', NotificationViewSet, basename='notification')
router.register('user-notifications', UserNotificationViewSet, basename='usernotification')

# Config & administration
router.register('modules', ModuleViewSet, basename='module')
router.register('module-permissions', ModulePermissionViewSet, basename='modulepermission')
router.register('users', UserViewSet, basename='user')

# Optional viewsets (depend on model availability)
try:
    from qm.api_viewsets import AnalyticMetaViewSet
    router.register('analytics-meta', AnalyticMetaViewSet, basename='analyticmeta')
except ImportError:
    pass

try:
    from qm.api_viewsets import CampaignCompletionViewSet
    router.register('campaign-completions', CampaignCompletionViewSet, basename='campaigncompletion')
except ImportError:
    pass

try:
    from config.api_viewsets import ApiKeyViewSet
    router.register('api-keys', ApiKeyViewSet, basename='apikey')
except ImportError:
    pass
