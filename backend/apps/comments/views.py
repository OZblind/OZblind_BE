from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer, OpenApiParameter

from backend.apps.notifications.models import Notification

from .models import Comment
from .serializers import CommentCreateSerializer, CommentSerializer, MyCommentSerializer

@extend_schema_view(
    post=extend_schema(
        summary='댓글 작성',
        description='API를 요청한 유저의 댓글을 작성합니다.\n\n'+
                    '**대댓글이 아닌경우 root키는 사용하면 안됨**',
        request=CommentCreateSerializer,
        responses=CommentCreateSerializer,
        tags=['Comment'],
        ))
class CommentCreate(APIView):
    # 댓글 등록
    def post(self, request):
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_comment=serializer.save(user=request.user)

        # 루트댓글은 게시물 작성자에게, 대댓글은 루트댓글 작성자에게 알림 송신
        recipient=None
        if new_comment.root==new_comment:
            recipient=new_comment.post.user
        else:
            recipient=new_comment.root.user

        # 본인에게 본인이 송신하지 않음
        if recipient != request.user:
            Notification.objects.create(
                user=recipient,
                post=new_comment.post,
                message=new_comment.content,
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema_view(
    patch=extend_schema(
        summary='유저의 댓글 수정',
        description='API를 요청한 유저의 댓글을 수정합니다.',
        parameters=[
                OpenApiParameter(name='id', description='수정할 댓글의 ID', required=True, type=int, location=OpenApiParameter.PATH),
        ],
        request=inline_serializer(
            name='CommentUpdateRequest',
            fields={'content': serializers.CharField(help_text='수정할 댓글 내용')},
        ),
        responses={200: inline_serializer( # 성공
                name='CommentUpdateSuccess',
                fields={'message': serializers.CharField(default='다음으로 내용 업데이트: <수정한 댓글 내용>')}
            )},
        tags=['Comment'],
        ),
    delete=extend_schema(
        summary='유저의 댓글 삭제',
        description='API를 요청한 유저의 댓글을 삭제합니다.\n\n'+
                    '대댓글이 없는 경우(204): 댓글을 데이터베이스에서 완전히 삭제\n\n'+
                    '대댓글이 있는 경우(200): 댓글 내용을 "작성자에 의해 삭제된 댓글입니다."로 변경(소프트 딜리트)',
        parameters=[
                OpenApiParameter(name='id', description='삭제할 댓글의 ID', required=True, type=int, location=OpenApiParameter.PATH),
        ],
        responses={
            200: inline_serializer( # 소프트 딜리트 성공
                name='CommentSoftDeleteSuccess',
                fields={'message': serializers.CharField(default='댓글이 삭제 처리되었습니다.')}
            ),
            204: None,  # 완전 삭제 성공
            403: inline_serializer( # 권한 없음
                name='CommentDeleteForbidden',
                fields={'error': serializers.CharField(default='댓글은 작성자 본인만 삭제 가능합니다.')}
            ),
            404: inline_serializer( # 댓글 없음
                name='CommentNotFound',
                fields={'detail': serializers.CharField(default='Not found.')}
            ),
        },
        tags=['Comment'],
        )
)
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

@extend_schema_view(
    get=extend_schema(
        summary='유저의 댓글 조회',
        description='API를 요청한 유저의 댓글을 조회합니다.',
        responses=MyCommentSerializer,
        tags=['profile'],
        ))
class MyComment(APIView):
    # 유저의 댓글 조회
    def get(self, request):
        comments = Comment.objects.filter(user=request.user)
        serializer = MyCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
