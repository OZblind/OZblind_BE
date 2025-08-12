from rest_framework import serializers
from .models import Bookmark
from backend.apps.posts.models import Post

class BookmarkSerializer(serializers.ModelSerializer):
    # post 필드를 ID 값으로 받을 수 있도록 명시
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user'] # user는 서버에서 자동으로 채우므로 읽기 전용으로 설정합니다.