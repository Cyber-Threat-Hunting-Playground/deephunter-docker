from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Notification, UserNotification
from .serializers import NotificationSerializer, UserNotificationSerializer


@extend_schema_view(
    list=extend_schema(tags=['Notifications']),
    retrieve=extend_schema(tags=['Notifications']),
    create=extend_schema(tags=['Notifications']),
    update=extend_schema(tags=['Notifications']),
    partial_update=extend_schema(tags=['Notifications']),
    destroy=extend_schema(tags=['Notifications']),
)
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message']
    ordering_fields = ['created_at', 'level']

    def get_queryset(self):
        qs = super().get_queryset()
        level = self.request.query_params.get('level')
        if level:
            qs = qs.filter(level=level)
        return qs


@extend_schema_view(
    list=extend_schema(tags=['User Notifications']),
    retrieve=extend_schema(tags=['User Notifications']),
    create=extend_schema(tags=['User Notifications']),
    update=extend_schema(tags=['User Notifications']),
    partial_update=extend_schema(tags=['User Notifications']),
    destroy=extend_schema(tags=['User Notifications']),
)
class UserNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = UserNotificationSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['notification__created_at', 'is_read']

    def get_queryset(self):
        qs = UserNotification.objects.select_related('notification', 'user').all()
        user = self.request.query_params.get('user')
        if user:
            qs = qs.filter(user_id=user)
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() in ('true', '1'))
        return qs
