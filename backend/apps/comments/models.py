from django.db import models

class Comment(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    root = models.ForeignKey('comments.Comment', on_delete=models.CASCADE)
    parent = models.ForeignKey('comments.Comment', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    likes_cnt = models.IntegerField(default=0)
    dislikes_cnt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)