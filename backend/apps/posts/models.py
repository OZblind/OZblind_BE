from django.db import models
from django.conf import settings

class Post(models.Model):
    board = models.ForeignKey('boards.Board', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=5000)
    image = models.CharField(max_length=255, null=True)
    views = models.IntegerField(default=0)
    likes_cnt = models.IntegerField(default=0)
    dislikes_cnt = models.IntegerField(default=0)
    bookmark_cnt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
