from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from backend.apps.posts.models import Post
from .models import Bookmark
from .serializers import BookmarkSerializer

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