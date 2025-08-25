from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction # DB 작업을 안전하게 묶어주기 위한 도구
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Reaction
from .serializers import ReactionSerializer
from backend.apps.posts.models import Post
from backend.apps.comments.models import Comment


class ReactionAPIView(APIView):
    """
    게시물 또는 댓글에 대한 리액션을 처리
    - POST: 리액션을 생성, 변경, 또는 취소 (토글 방식)
    """
    permission_classes = [IsAuthenticated] # 로그인한 사용자만 접근 가능

    @extend_schema(
        tags=["Reactions"],
        summary="리액션 생성/변경/취소 (토글)",
        description="사용자가 게시물 또는 댓글에 리액션을 추가하거나 변경, 취소할 수 있는 API",
        request=ReactionSerializer,
        responses={
            201: OpenApiResponse(description="리액션이 성공적으로 생성됨"),
            200: OpenApiResponse(description="리액션이 성공적으로 변경되거나 취소됨"),
            400: OpenApiResponse(description="잘못된 요청 데이터"),
            401: OpenApiResponse(description="인증 되지 않은 사용자 접근"),
        }
    )

    
    @transaction.atomic # 이 메서드 안의 모든 DB 작업이 하나의 단위로 처리되도록 보장함
    def post(self, request, *args, **kwargs):
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        reaction_choice = validated_data['reaction']

        existing_reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            content_type=validated_data['content_type'],
            object_id=validated_data['object_id'],
            defaults={'reaction': reaction_choice}
        )

        if created:
            serializer = ReactionSerializer(existing_reaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if existing_reaction.reaction == reaction_choice:
            existing_reaction.delete()
            return Response({"detail": "리액션이 취소되었습니다."}, status=status.HTTP_200_OK)
        
        else:
            existing_reaction.delete()
            new_reaction = Reaction.objects.create(
                user=request.user,
                content_type=validated_data['content_type'],
                object_id=validated_data['object_id'],
                reaction=reaction_choice
            )
            serializer = ReactionSerializer(new_reaction)
            return Response(serializer.data, status=status.HTTP_200_OK)