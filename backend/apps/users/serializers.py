from rest_framework import serializers
from .models import User



class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(write_only=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'profile_image', 'role', 'is_active']

class ActivateSerializer(serializers.Serializer):
    id_token_str = serializers.CharField(write_only=True)
    cohort_number = serializers.CharField(write_only=True)
    plain_key = serializers.CharField(write_only=True)

class UserWithTokenSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    class Meta:
        fields = UserSerializer.Meta.fields + ['access', 'refresh', 'is_active', 'id','email']



# 태그 정보가 필요한 경우 정보 필터링에 사용할 시리얼라이저
class UserTagSerializer(serializers.ModelSerializer):
    tag_class=serializers.CharField(source='oz_keys.get.tag_class', read_only=True)
    tag_number=serializers.IntegerField(source='oz_keys.get.tag_number', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'tag_class', 'tag_number']