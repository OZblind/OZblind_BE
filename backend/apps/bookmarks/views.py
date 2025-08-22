from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiResponse

from django.shortcuts import get_object_or_404
from backend.apps.posts.models import Post
from .models import Bookmark
from .serializers import BookmarkSerializer, BookmarkListSerializer

# 북마크 생성 및 삭제를 위한 APIView
class BookmarkAPIView(APIView):
    permission_classes = [IsAuthenticated] # 로그인사용자만 접근 가능
    
    @extend_schema(
        tags=["Bookmarks"],
        summary="북마크 생성",
        description="특정 게시물에 북마크 추가(이미 북마크 시 400에러 반환)",
        responses={
            201: OpenApiResponse(description="북마크 생성됨"),
            400: OpenApiResponse(description="이미 북마크 존재함"),
            401: OpenApiResponse(description="인증 되지 않은 사용자 접근"),
            404: OpenApiResponse(description="존재하지 않는 게시물"),
        }
    )


    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        # 이미 북마크가 존재한다면 에러 반환
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
        tags=["Bookmarks"],
        summary="북마크 삭제",
        description="특정 게시물에 대한 북마크 삭제",
        responses={
            200: OpenApiResponse(description="북마크 삭제됨"),
            404: OpenApiResponse(description="존재하지 않는 게시물 혹은 북마크"),
            401: OpenApiResponse(description="인증 되지 않은 사용자 접근"),
        }
    )

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        
        bookmark = get_object_or_404(Bookmark, user=request.user, post=post)
        bookmark.delete()
        return Response({"message": "삭제완료"}, status=status.HTTP_200_OK)
    
# 북마크 목록 조회 (api/bookmarks/me/)
@extend_schema(
    tags=["Bookmarks"],
    summary="내 북마크 목록 조회",
    description="로그인한 사용자의 북마크 목록을 반환",
    # 북마크가 하나도 없다면 404 not found 반환
    responses={
        200: BookmarkListSerializer(many=True),
        404: OpenApiResponse(description="북마크가 존재하지 않음"),
        401: OpenApiResponse(description="인증 되지 않은 사용자 접근"),
    }
)
# generics.ListAPIView가 get의 기본 구현을 제공하므로, 별도의 get 메서드를 구현할 필요 없음 개꿀 ㅋㅋㅋㅋㅋ
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
