from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from backend.apps.boards.models import Board
from .models import Post, PostSurvey, PostGithub
from .serializers import (
    PostSerializer,
    SurveyPostCreateSerializer, PostSurveyDetailSerializer,
    GithubPostCreateSerializer, PostGithubDetailSerializer
)
from django_filters.rest_framework import DjangoFilterBackend


# 페이지네이션 규칙 정의
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['board']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count']
    ordering = ['-created_at']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count = F('view_count') + 1
        instance.save(update_fields=['view_count'])
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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