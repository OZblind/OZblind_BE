from rest_framework import serializers
from .models import Post, BestPost

from ..comments.models import Comment

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'user',
            'parent',
            'content',
            'like_count',
            'dislike_count',
            'created_at',
            'updated_at'
        ]
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'user',
            'parent',
            'content',
            'like_count',
            'dislike_count',
            'created_at',
            'updated_at',
            'children'
        ]

class PostSerializer(serializers.ModelSerializer):

    root_comment = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'board',
            'user',
            'title',
            'content',
            'image',
            'view_count',
            'like_count',
            'dislike_count',
            'bookmark_count',
            'created_at',
            'updated_at',
            'root_comment'
        ]

        read_only_fields = (
            'id',
            'user',
            'view_count',
            'like_count',
            'dislike_count',
            'bookmark_count',
            'created_at',
            'updated_at',
            'root_comment',
        )

    def get_root_comment(self, post_obj):
        toplevel_comments = post_obj.comment_set.filter(parent__isnull = True)
        return CommentSerializer(toplevel_comments, many=True).data

# 알림기능에 포스트 정보 제한
class NotificationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields=('id','title')

# 인기 게시글 기능에 사용
class MainPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'board', 'user', 'title', 'view_count', 'like_count', 'created_at')

class HotPostSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Post
        fields = ('id', 'board', 'title', 'view_count', 'like_count', 'comment_count')
