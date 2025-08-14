from django.db import models
from django.conf import settings

class Post(models.Model):
    board = models.ForeignKey('boards.Board', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    image = models.TextField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ('-created_at',)

# 메인페이지에서 사용하는 핫게시물 모음
class BestPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    view_count=models.PositiveIntegerField()
    refreshed_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-view_count']
        db_table = 'best_post'