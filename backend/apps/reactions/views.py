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

class ReactionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReactionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        content_type = validated_data['content_type']
        object_id = validated_data['object_id']
        reaction_choice = validated_data['reaction']
        
        # 이미 리액션이 있는지 찾기
        existing_reaction = Reaction.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        ).first()

        if existing_reaction:
            if existing_reaction.reaction == reaction_choice:
                # 같은 리액션이면 -> 취소 (삭제)
                existing_reaction.delete()
                return Response({"message": "리액션 취소됨."}, status=status.HTTP_204_NO_CONTENT)
            else:
                # 다른 리액션이면 -> 변경 (업데이트)
                existing_reaction.reaction = reaction_choice
                existing_reaction.save()
                serializer = ReactionSerializer(existing_reaction)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        target_type_str = request.data.get('target_type')
        target_id = request.data.get('target_id')

        model_map = {'post': Post, 'comment': Comment}
        model = model_map.get(target_type_str)
        if not model:
            return Response({"error": "Invalid target_type."}, status=status.HTTP_400_BAD_REQUEST)
        
        content_type = ContentType.objects.get_for_model(model)
        
        reaction = get_object_or_404(
            Reaction,
            user=request.user,
            content_type=content_type,
            object_id=target_id
        )
        
        reaction.delete()
        return Response({"message": "삭제완료"}, status=status.HTTP_204_NO_CONTENT)