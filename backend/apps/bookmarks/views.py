from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from django.shortcuts import get_object_or_404
from backend.apps.posts.models import Post
from .models import Bookmark
from .serializers import BookmarkSerializer, BookmarkListSerializer

class BookmarkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        
        serializer = BookmarkSerializer(data={'post': post.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        # 명세서에 맞게 응답 데이터를 구성합니다.
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
    
class BookmarkListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkListSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('post')
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "bookmarks not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        bookmarks_data = [item['post'] for item in serializer.data]
        response_data = {
            "status": "success",
            "bookmarks": bookmarks_data
        }
        return Response(response_data, status=status.HTTP_200_OK)
