from rest_framework import serializers
from .models import Bookmark
from backend.apps.posts.models import Post

# 북마크 생성과 삭제
class BookmarkSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user']

# 북마크 목록 조회
class BookmarkedPostSerializer(serializers.ModelSerializer):
    postId = serializers.IntegerField(source='id')

    class Meta:
        model = Post
        fields = ['postId', 'title']

class BookmarkListSerializer(serializers.ModelSerializer):
    post = BookmarkedPostSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['post']