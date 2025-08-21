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