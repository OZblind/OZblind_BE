#from django.db.models import F 추후 인기게시글 좋아요 반영시 작성예정
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    # 게시글 CRUD, 정렬, 검색 API viewset
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [SearchFilter]
    search_fields = ['title', 'content']

    # 인기순 정렬을 위한 쿼리셋 메소드
    def _get_popular_queryset(self, queryset):
        return queryset.order_by('-view_count', '-created_at')

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', None)

        if ordering == 'popular':
            return self._get_popular_queryset(queryset)

        if ordering == 'created_at':
            return  queryset.order_by('-created_at')

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)