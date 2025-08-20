from django.db.models import F
from rest_framework import serializers
from .models import Post, PostSurvey, PostGithub, BestPost
from backend.apps.comments.models import Comment
from backend.apps.users.serializers import UserTagSerializer

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

# 게시글 목록 조회 및 검색용 게시글 리스트 시리얼라이저
class PostListSerializer(serializers.ModelSerializer):
    # 유저 정보에 태그 정보를 같이 보내는 시리얼라이저
    user = UserTagSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'board', 'title', 'user', 'view_count', 'like_count', 'created_at', 'updated_at']

# 일반 게시글 상세 정보를 위한 메인 시리얼라이저
class PostDetailSerializer(serializers.ModelSerializer):
    root_comments = serializers.SerializerMethodField()
    bookmarks = serializers.SerializerMethodField()
    # 유저 정보에 태그 정보를 같이 보내는 시리얼라이저
    user=UserTagSerializer(read_only=True)

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
            'root_comments',
            'bookmarks'
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
            'bookmarks',

        )

    def get_root_comments(self, post_obj):
        # 최상위 댓글(root)을 찾음
        toplevel_comments = post_obj.comments.filter(root=F('id'))
        return CommentSerializer(toplevel_comments, many=True).data

    def get_bookmarks(self, post_obj):
        return post_obj.bookmark_count

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





# 알림기능에 포스트 정보 제한
class NotificationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields=('id','title')

# 최신 게시글 기능에 사용
class MainPostSerializer(serializers.ModelSerializer):
    user = UserTagSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ('id', 'board', 'user', 'title', 'view_count', 'like_count', 'created_at')

# 인기 게시글 기능에 사용
class HotPostSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Post
        fields = ('id', 'board', 'title', 'view_count', 'like_count', 'comment_count')
