from rest_framework import serializers
from .models import Post
from ..notifications.models import Notification


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = (
            'id',
            'user',
            'view_count',
            'like_count',
            'dislike_count',
            'bookmark_count',
            'created_at',
            'updated_at'
        )

# 알림기능에 포스트 정보 제한
class NotificationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields=('id','title')