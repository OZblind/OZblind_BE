from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = (
            'id',
            'user',
            'view_count',
            'like_count',
            'dislike_count',
            'bookmark_count',
            'created_at',
            'updated_at'
        )