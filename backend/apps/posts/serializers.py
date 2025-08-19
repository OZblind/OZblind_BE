from django.db.models import F
from rest_framework import serializers
from .models import Post, PostSurvey, PostGithub
from backend.apps.comments.models import Comment

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'user', 'root', 'content', 'like_count', 'dislike_count', 'created_at', 'updated_at'
        ]

class CommentSerializer(serializers.ModelSerializer):
    thread_comments = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'user', 'root', 'content', 'like_count', 'dislike_count', 'created_at', 'updated_at', 'thread_comments'
        ]

# 일반 게시글 상세 정보를 위한 메인 시리얼라이저
class PostSerializer(serializers.ModelSerializer):
    root_comments = serializers.SerializerMethodField()

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
            'root_comments'
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
            'root_comments',
        )

    def get_root_comment(self, post_obj):
        # 최상위 댓글(root)을 찾음
        toplevel_comments = post_obj.comments.filter(root=F('id'))
        return CommentSerializer(toplevel_comments, many=True).data

# 알림기능에 포스트 정보 제한
class NotificationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields=('id','title')


class PostSurveyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostSurvey
        fields = ['end_date', 'link']


class PostGithubDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostGithub
        fields = ['link']


class SurveyPostCreateSerializer(serializers.ModelSerializer):
    end_date = serializers.DateTimeField(write_only=True)
    link = serializers.URLField(write_only=True)

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'end_date', 'link']

    def create(self, validated_data):
        board = self.context['board']
        user = self.context['request'].user
        survey_data = {'end_date': validated_data.pop('end_date'), 'link': validated_data.pop('link')}
        post = Post.objects.create(board=board, user=user, **validated_data)
        PostSurvey.objects.create(post=post, **survey_data)
        return post


class GithubPostCreateSerializer(serializers.ModelSerializer):
    link = serializers.URLField(write_only=True)

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'link']

    def create(self, validated_data):
        board = self.context['board']
        user = self.context['request'].user
        github_data = {'link': validated_data.pop('link')}
        post = Post.objects.create(board=board, user=user, **validated_data)
        PostGithub.objects.create(post=post, **github_data)
        return post