from rest_framework.serializers import ModelSerializer
from .models import Comment

class CommentCreateSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'root', 'content']
        read_only_fields = ['id']

class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class MyCommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'post', 'content', 'created_at', 'updated_at')