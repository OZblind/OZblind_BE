# backend/apps/bookmarks/serializers.py

from rest_framework import serializers
from .models import Bookmark
from backend.apps.posts.models import Post

# --- 1. 생성/삭제를 위한 기존 시리얼라이저 (이 부분은 그대로 둡니다!) ---
class BookmarkSerializer(serializers.ModelSerializer):
    # post 필드를 ID 값으로 받을 수 있도록 명시
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user']


# --- 2. 목록 조회를 위해 새로 추가하는 코드 (이 부분을 통째로 붙여넣으세요!) ---

# 2-1. 게시물 정보를 담을 "미니 시리얼라이저" (안쪽 부품)
class BookmarkedPostSerializer(serializers.ModelSerializer):
    postId = serializers.IntegerField(source='id') # 명세서의 'postId'에 맞게 필드 이름 변경

    class Meta:
        model = Post
        fields = ['postId', 'title'] # id와 title만 보여줍니다.

# 2-2. 북마크 목록 전체를 위한 "메인 시리얼라이저" (바깥쪽 부품)
class BookmarkListSerializer(serializers.ModelSerializer):
    # post 필드를 렌더링할 때, 위에서 만든 BookmarkedPostSerializer를 사용합니다.
    post = BookmarkedPostSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['post'] # 우리는 북마크 객체에서 post 정보만 필요합니다.