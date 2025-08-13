from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from django.shortcuts import get_object_or_404
from backend.apps.posts.models import Post
from .models import Bookmark
from .serializers import BookmarkSerializer, BookmarkListSerializer

# 북마크 생성 및 삭제를 위한 APIView
class BookmarkAPIView(APIView):
    permission_classes = [IsAuthenticated] # 로그인사용자만 접근 가능

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        
        serializer = BookmarkSerializer(data={'post': post.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        response_data = {
            'id': serializer.instance.id,
            'post_id': serializer.instance.post.id
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        
        bookmark = get_object_or_404(Bookmark, user=request.user, post=post)
        bookmark.delete()
        return Response({"message": "삭제완료"}, status=status.HTTP_204_NO_CONTENT)
    
# 북마크 목록 조회 (api/bookmarks/me/)
class BookmarkListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkListSerializer

# 사용자의 북마크 목록만 필터링해 조회하는 API
    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('post')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # 북마크가 없을 경우
        if not queryset.exists():
            return Response({"message": "bookmarks not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        bookmarks_data = [item['post'] for item in serializer.data]
        response_data = {
            "status": "success",
            "bookmarks": bookmarks_data
        }
        return Response(response_data, status=status.HTTP_200_OK)
