from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Comment
from .serializers import CommentCreateSerializer, CommentSerializer

class CommentCreate(APIView):
    # 댓글 등록
    def post(self, request):
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentUpdateDelete(APIView):
    # 댓글 수정
    def patch(self, request, pk):
        comment=get_object_or_404(Comment, pk=pk)
        if comment.user != request.user:
            return Response(
                {"error": "댓글은 작성자 본인만 수정 가능합니다."},
                status=status.HTTP_403_FORBIDDEN)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)  # 유효성 검사
        serializer.save()
        return Response({'message':'다음으로 내용 업데이트:'+request.data['content']},status=status.HTTP_200_OK)

    # 댓글 삭제, 대댓글이 있는 경우 소프트딜리트
    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.user != request.user:
            return Response(
                {"error": "댓글은 작성자 본인만 삭제 가능합니다."},
                status=status.HTTP_403_FORBIDDEN)

        # 자신을 참조하는 댓글이 있는 경우
        if comment.children.exists():
            comment.content='작성자에 의해 삭제된 댓글입니다.'
            comment.save()
            return Response({'message': '댓글이 삭제 처리되었습니다.'}, status=status.HTTP_200_OK)

        # 자신을 참조하는 댓글이 없는 경우
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)