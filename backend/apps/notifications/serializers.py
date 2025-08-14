from rest_framework.serializers import ModelSerializer

from backend.apps.posts.serializers import NotificationPostSerializer

from .models import Notification

class NtfListSerializer(ModelSerializer):
    post=NotificationPostSerializer(read_only=True)
    class Meta:
        model = Notification
        exclude = ('user',)