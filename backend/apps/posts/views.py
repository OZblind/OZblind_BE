#from django.db.models import F 추후 인기게시글 좋아요 반영시 작성예정
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    # 게시글 CRUD, 정렬, 검색 API viewset
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    order_fields = ['created_at', 'view_count']
    order = ['-created_at']

    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)