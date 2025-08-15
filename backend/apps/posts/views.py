#from django.db.models import F 추후 인기게시글 좋아요 반영시 작성예정
from django.utils import timezone
from django.db import transaction
from django.db.models import Count
from datetime import timedelta
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Post, BestPost
from .serializers import PostSerializer, HotPostSerializer, MainPostSerializer

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

class MainPostView(APIView):
    # 최신 게시물 5개
    def get(self, request):
        posts = Post.objects.all()[:5]
        serializer = MainPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class HotPostView(APIView):
    # 핫 게시물 5개 가져오기
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
        return Response({'message': '핫게시글 갱신 성공'}, status=status.HTTP_200_OK)