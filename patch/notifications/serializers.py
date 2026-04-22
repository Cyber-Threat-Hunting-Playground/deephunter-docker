from rest_framework import serializers
from .models import Notification, UserNotification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at']


class UserNotificationSerializer(serializers.ModelSerializer):
    message = serializers.CharField(source='notification.message', read_only=True)
    level = serializers.CharField(source='notification.level', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserNotification
        fields = '__all__'
        extra_fields = ['message', 'level', 'username']
