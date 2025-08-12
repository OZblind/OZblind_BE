# backend/apps/bookmarks/serializers.py

from rest_framework import serializers
from .models import Bookmark
from backend.apps.posts.models import Post

class BookmarkSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user']

class BookmarkedPostSerializer(serializers.ModelSerializer):
    postId = serializers.IntegerField(source='id')

    class Meta:
        model = Post
        fields = ['postId', 'title']

# 2-2. 북마크 목록 전체를 위한 "메인 시리얼라이저" (바깥쪽 부품)
class BookmarkListSerializer(serializers.ModelSerializer):
    post = BookmarkedPostSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['post']