from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction # DB 작업을 안전하게 묶어주기 위한 도구

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

    @transaction.atomic # 이 메서드 안의 모든 DB 작업이 하나의 단위로 처리되도록 보장함
    def post(self, request, *args, **kwargs):
        
        #  Serializer를 통해 입력 데이터의 유효성을 검증
        serializer = ReactionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 유효성 검증을 통과한 데이터들을 가져옴
        validated_data = serializer.validated_data
        content_type = validated_data['content_type']
        object_id = validated_data['object_id']
        reaction_choice = validated_data['reaction']
        
        # 리액션의 대상이 되는 객체(Post 또는 Comment)를 가져오기
        target_model = content_type.model_class()
        target_object = get_object_or_404(target_model, id=object_id)

        # 해당 객체에 대한 리액션이 있는지 찾고, 없으면 새로 만듦
        existing_reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            defaults={'reaction': reaction_choice}
        )

        # 3. 리액션 존재 여부에 따라 분기 처리
        if not created:
            # 이미 리액션이 존재 시
            if existing_reaction.reaction == reaction_choice:
                # 같은 리액션 -> 취소 (Delete)
                
                # 카운트 변경 로직 (감소)
                if isinstance(target_object, (Post, Comment)):
                    if reaction_choice == 'like' and target_object.like_count > 0:
                        target_object.like_count -= 1
                    elif reaction_choice == 'dislike' and target_object.dislike_count > 0:
                        target_object.dislike_count -= 1
                    target_object.save()
                
                existing_reaction.delete()
                return Response({"message": "리액션이 취소됨."}, status=status.HTTP_200_OK)
            else:
                # 다른 리액션 -> 변경 (Update)
                
                # 카운트 변경 (하나 증가, 하나 감소)
                if isinstance(target_object, (Post, Comment)):
                    if reaction_choice == 'like':
                        target_object.like_count += 1
                        if target_object.dislike_count > 0: target_object.dislike_count -= 1
                    else:
                        target_object.dislike_count += 1
                        if target_object.like_count > 0: target_object.like_count -= 1
                    target_object.save()

                existing_reaction.reaction = reaction_choice
                existing_reaction.save()
                serializer = ReactionSerializer(existing_reaction)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # 리액션이 새로 생성되면 Create
            
            # 카운트 변경 (증가)
            if isinstance(target_object, (Post, Comment)):
                if reaction_choice == 'like':
                    target_object.like_count += 1
                else:
                    target_object.dislike_count += 1
                target_object.save()
            
            serializer = ReactionSerializer(existing_reaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)