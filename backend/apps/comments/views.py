from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from backend.apps.notifications.models import Notification

from .models import Comment
from .serializers import CommentCreateSerializer, CommentSerializer, MyCommentSerializer

class CommentCreate(APIView):
    # 댓글 등록
    def post(self, request):
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_comment=serializer.save(user=request.user)

        # 루트댓글은 게시물 작성자에게, 대댓글은 루트댓글 작성자에게 알림 송신
        recipient=None
        if new_comment.root:
            recipient=new_comment.root.user
        else:
            recipient=new_comment.post.user

        # 본인에게 본인이 송신하지 않음
        if recipient != request.user:
            Notification.objects.create(
                user=recipient,
                post=new_comment.post,
                message=new_comment.content,
            )
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
        if comment.thread_comments.exists():
            comment.content='작성자에 의해 삭제된 댓글입니다.'
            comment.save()
            return Response({'message': '댓글이 삭제 처리되었습니다.'}, status=status.HTTP_200_OK)

        # 자신을 참조하는 댓글이 없는 경우
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MyComment(APIView):
    # 유저의 댓글 조회
    def get(self, request):
        comments = Comment.objects.filter(user=request.user)
        serializer = MyCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
