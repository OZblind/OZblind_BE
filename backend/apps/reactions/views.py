from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from .models import Reaction
from .serializers import ReactionSerializer
from backend.apps.posts.models import Post
from backend.apps.comments.models import Comment

# -----------------------------------------------------------------------------
# [리액션 생성/삭제/토글용 View]
# - 담당 API: POST, DELETE /api/reactions/
# - 역할: 게시물 또는 댓글에 대한 리액션을 처리하는 모든 로직을 담당합니다.
# - 특징: API 명세서에 따라, 하나의 View에서 복잡한 토글 로직을 처리합니다.
# -----------------------------------------------------------------------------
class ReactionAPIView(APIView):
    """
    게시물 또는 댓글에 대한 리액션을 처리
    - POST: 리액션을 생성, 변경, 또는 취소
    - DELETE: 리액션을 삭제합니다
    """
    permission_classes = [IsAuthenticated] # 로그인한 사용자만 접근 가능

    def post(self, request, *args, **kwargs):
  
        
        # Serializer를 통해 입력 데이터의 유효성 검증
        serializer = ReactionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 유효성 검증이 완료된 데이터를 가져오기
        validated_data = serializer.validated_data
        content_type = validated_data['content_type']
        object_id = validated_data['object_id']
        reaction_choice = validated_data['reaction']
        
        # 이미 해당 객체에 대한 리액션이 있는지 찾아보고, 없으면 새로 만듦
        # get_or_create: 객체가 없을 경우, defaults 값으로 객체를 생성
        existing_reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            # get_or_create: 객체가 없을 경우, defaults 값으로 객체를 생성
            defaults={'reaction': reaction_choice}
        )

        # 리액션 존재 여부에 따라 분기 처리
        if not created:
            # (Case 1) 이미 리액션이 존재했을 경우
            if existing_reaction.reaction == reaction_choice:
                # (Case 1-1) 같은 리액션(예: 좋아요 누른 상태에서 또 좋아요) -> 취소 (Delete)
                existing_reaction.delete()
                return Response({"message": "리액션이 취소되었습니다."}, status=status.HTTP_204_NO_CONTENT)
            else:
                # (Case 1-2) 다른 리액션(예: 좋아요 누른 상태에서 싫어요) -> 변경 (Update)
                existing_reaction.reaction = reaction_choice
                existing_reaction.save()
                response_serializer = ReactionSerializer(existing_reaction)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            # (Case 2) 리액션이 새로 생성되었을 경우 (Create)
            response_serializer = ReactionSerializer(existing_reaction)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """ 리액션을 명시적으로 삭제 """
        target_type_str = request.data.get('target_type')
        target_id = request.data.get('target_id')

        model_map = {'post': Post, 'comment': Comment}
        model = model_map.get(target_type_str)
        if not model:
            return Response({"error": "Invalid target_type."}, status=status.HTTP_400_BAD_REQUEST)
        
        content_type = ContentType.objects.get_for_model(model)
        
        # 삭제할 리액션을 '로그인한 사용자'와 '대상 객체'를 기준으로 찾기
        reaction = get_object_or_404(
            Reaction,
            user=request.user,
            content_type=content_type,
            object_id=target_id
        )
        
        reaction.delete()
        return Response({"message": "삭제완료"}, status=status.HTTP_204_NO_CONTENT)