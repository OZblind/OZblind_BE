from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from backend.apps.posts.models import Post
from .models import Bookmark
from .serializers import BookmarkSerializer, BookmarkedPostSerializer

class BookmarkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="게시물 북마크 추가",
        description="특정 게시물(post_id)을 현재 로그인한 사용자의 북마크에 추가.",
        responses={
            201: BookmarkSerializer, # 성공 시 응답 예시
            400: OpenApiResponse(description="이미 북마크된 게시물"),
            404: OpenApiResponse(description="존재하지 않는 게시물입니다."),
        }
    )
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        if Bookmark.objects.filter(user=request.user, post=post).exists():
            return Response({"message": "이미 북마크가 존재함"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BookmarkSerializer(data={'post': post.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        response_data = {
            'id': serializer.instance.id,
            'post_id': serializer.instance.post.id
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="게시물 북마크 삭제",
        description="특정 게시물(post_id)을 현재 로그인한 사용자의 북마크에서 삭제",
        responses={
            200: OpenApiResponse(description="성공적으로 삭제됨"),
            404: OpenApiResponse(description="존재하지 않는 게시물 또는 해당 게시물을 북마크하지 않았음."),
        }
    )
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        
        bookmark = get_object_or_404(Bookmark, user=request.user, post=post)
        bookmark.delete()
        return Response({"message": "삭제완료"}, status=status.HTTP_200_OK)
    
class BookmarkListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkedPostSerializer

    def get_queryset(self):
        """
        현재 로그인한 사용자가 북마크한 '게시물(Post)' 목록을 반환합니다.
        """
        # 먼저 로그인한 유저의 북마크 객체들을 가져옴
        user_bookmarks = Bookmark.objects.filter(user=self.request.user)
        # 북마크들이 가리키고 있는 Post의 id 목록을 추출
        post_ids = user_bookmarks.values_list('post_id', flat=True)
        # 그 id 목록에 해당하는 Post 객체들을 최종적으로 반환
        return Post.objects.filter(id__in=post_ids)
    
    @extend_schema(
        summary="내 북마크 목록 조회",
        description="현재 로그인한 사용자가 북마크한 모든 게시물의 목록을 조회합니다.",
        responses={
            200: BookmarkedPostSerializer(many=True),
            404: OpenApiResponse(description="북마크한 게시물이 존재하지 않음."),
        }
    )
    def get(self, request, *args, **kwargs):
        # generics.ListAPIView의 기본 동작을 그대로 사용
        # 우리가 재정의한 list 메서드를 호출
        return self.list(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({"message": "bookmarks not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "status": "success",
            "bookmarks": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
