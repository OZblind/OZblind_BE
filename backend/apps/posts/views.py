from re import search

from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import serializers
from backend.apps.boards.models import Board
from .models import Post, PostSurvey, PostGithub
from .serializers import (
    PostListSerializer, PostDetailSerializer,
    SurveyPostCreateSerializer, PostSurveyDetailSerializer,
    GithubPostCreateSerializer, PostGithubDetailSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer


# 페이지네이션 규칙 정의
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['board']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count']
    ordering = ['-created_at']

    # 태그기능을 위한 n+1문제 해결을 위한 최적화 코드
    # get_queryset 오버라이드
    def get_queryset(self):
        queryset = super().get_queryset()
        optimized_queryset = queryset.select_related('user').prefetch_related('user__oz_keys')
        return optimized_queryset

    def get_serializer_class(self):
        if self.action == 'list':
            # 목록 요청일 경우 게시글을 리스트로 출력
            return PostListSerializer

        return PostDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 검색내용과 일치하는 결과가 없을 때
        search_keyword = request.query_params.get('search', None)
        if search_keyword and not queryset.exists():
            return Response({'detail': '검색결과가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 조회수 증가
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count = F('view_count') + 1
        instance.save(update_fields=['view_count'])
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 설문 게시판(board_id = 4) 전용 ViewSet
class SurveyPostViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):

        try:
            survey_board = Board.objects.get(id=4)
        except ObjectDoesNotExist:
            return Response({"error": "설문게시판이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        context = {'request': request, 'board': survey_board}
        serializer = SurveyPostCreateSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        response_data = {"post_id": post.id, "link": post.postsurvey.link}
        return Response(response_data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            survey = PostSurvey.objects.get(pk=pk)
            serializer = PostSurveyDetailSerializer(survey)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "조회할 수 없는 설문입니다."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def edit(self, request, pk=None):

        try:
            post = Post.objects.get(pk=pk, board_id=4)
            survey = PostSurvey.objects.get(post=post)
        except ObjectDoesNotExist:
            return Response({"error": "수정할 수 없는 설문입니다."}, status=status.HTTP_404_NOT_FOUND)

        if post.user != request.user:
            return Response({"error": "게시글은 작성자 본인만 수정 가능합니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SurveyPostCreateSerializer(instance=post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        post.title = validated_data.get('title', post.title)
        post.content = validated_data.get('content', post.content)
        post.image = validated_data.get('image', post.image)
        post.save()

        survey.end_date = validated_data.get('end_date', survey.end_date)
        survey.link = validated_data.get('link', survey.link)
        survey.save()

        response_data = {"post_id": post.id, "link": survey.link}
        return Response(response_data, status=status.HTTP_200_OK)


# Github 게시판 (board_id = 5) 전용 ViewSet
class GithubPostViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            github_board = Board.objects.get(id=5)
        except ObjectDoesNotExist:
            return Response({"error": "GitHub 게시판이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        context = {'request': request, 'board': github_board}
        serializer = GithubPostCreateSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        response_data = {"post_id": post.id, "link": post.postgithub.link}
        return Response(response_data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            github = PostGithub.objects.get(pk=pk)
            serializer = PostGithubDetailSerializer(github)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "조회할 수 없는 GitHub 정보입니다."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def edit(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk, board_id=5)
            github = PostGithub.objects.get(post=post)
        except ObjectDoesNotExist:
            return Response({"error": "수정할 수 없는 GitHub 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)

        if post.user != request.user:
            return Response({"error": "게시글은 작성자 본인만 수정 가능합니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = GithubPostCreateSerializer(instance=post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        post.title = validated_data.get('title', post.title)
        post.content = validated_data.get('content', post.content)
        post.image = validated_data.get('image', post.image)
        post.save()

        github.link = validated_data.get('link', github.link)
        github.save()

        response_data = {"post_id": post.id, "link": github.link}
        return Response(response_data, status=status.HTTP_200_OK)





# 메인페이지 뷰
from django.utils import timezone
from django.db import transaction
from django.db.models import Count
from datetime import timedelta
from rest_framework.views import APIView
from .models import Post, BestPost
from .serializers import HotPostSerializer, MainPostSerializer

@extend_schema_view(
    get=extend_schema(
        summary='메인페이지 최근 게시물 조회',
        description='API를 요청한 시점에서 모든 게시물 중 최근 5개의 게시물 목록을 조회합니다.',
        responses=MainPostSerializer,
        tags=['MainPage'],
    )
)
class MainPostView(APIView):
    # 최신 게시물 5개
    def get(self, request):
        posts = Post.objects.all()[:5]
        serializer = MainPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema_view(
    get=extend_schema(
        summary='메인페이지 인기 게시물 조회',
        description='API를 요청한 시점에서 베스트포스트 테이블에 등록된 게시물 목록을 조회합니다.',
        responses=HotPostSerializer,
        tags=['MainPage'],
        ),
    patch=extend_schema(
        summary='메인페이지 인기 게시물 갱신',
        description='API를 요청한 시점에서 7일 이내의 게시글 5개를 베스트포스트 테이블에 등록합니다.',
        responses={
            200: inline_serializer(
                name='HotPatchSuccess',
                fields={'message': serializers.CharField(default='인기 게시글 갱신 성공')},
            )
        },
        tags=['MainPage'],
    )
)
class HotPostView(APIView):
    # 인기 게시물 5개 가져오기
    def get(self, request):
        # 인기 게시글의 PostID조회
        hot_id=BestPost.objects.all().values_list('post_id', flat=True)

        posts=Post.objects.filter(id__in=hot_id).annotate(
            comment_count=Count('comments')
        ).order_by('-view_count')
        serializer = HotPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 핫 게시물 갱신
    @transaction.atomic
    def patch(self, request):
        BestPost.objects.all().delete()

        best_posts=Post.objects.filter(created_at__gte=timezone.now()-timedelta(days=7)).order_by('-view_count')[:5]
        new_best_posts = [
            BestPost(
                post=post,
                view_count=post.view_count,
            )
            for post in best_posts
        ]

        BestPost.objects.bulk_create(new_best_posts)
        return Response({'message': '인기 게시글 갱신 성공'}, status=status.HTTP_200_OK)