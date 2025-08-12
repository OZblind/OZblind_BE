from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Reaction
from backend.apps.posts.models import Post
from backend.apps.comments.models import Comment

class ReactionSerializer(serializers.ModelSerializer):
    # API 명세서의 요청 Body를 처리하기 위한 필드
    # write_only=True는, 데이터를 쓸 때(POST)만 사용하고, 응답(GET)에는 포함하지 않겠다는 뜻입니다.
    target_type = serializers.ChoiceField(choices=['post', 'comment'], write_only=True)
    target_id = serializers.IntegerField(write_only=True)
    
    reaction_type = serializers.CharField(source='reaction', read_only=True)

    class Meta:
        model = Reaction
        # API 명세서에 맞는 필드들을 정의합니다.
        fields = ['id', 'reaction', 'target_type', 'target_id', 'reaction_type']
        # API 요청 시에는 reaction, target_type, target_id만 받고, 응답 시에는 id와 reaction_type만 보냅니다.
        read_only_fields = ['id']
        extra_kwargs = {
            'reaction': {'write_only': True},
        }

    def validate(self, data):
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        
        # 'post'나 'comment' 같은 문자열을 실제 ContentType 객체로 변환
        model_map = {'post': Post, 'comment': Comment}
        model = model_map.get(target_type)

        if not model:
            raise serializers.ValidationError({'target_type': 'Invalid target_type.'})
        
        # 해당 ContentType과 ID를 가진 실제 객체(Post 또는 Comment)가 존재하는지 확인
        if not model.objects.filter(id=target_id).exists():
            raise serializers.ValidationError({'target_id': 'Target object does not exist.'})
        
        data['content_type'] = ContentType.objects.get_for_model(model)
        data['object_id'] = target_id
        return data

    def create(self, validated_data):
        # view에서 user 정보를 받아와야 하므로, view의 perform_create에서 처리
        validated_data.pop('target_type')
        validated_data.pop('target_id')
        return Reaction.objects.create(**validated_data)