from django.db import models
from django.conf import settings

# Create your models here.
class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user.username} bookmarked Post: '{self.post.title}'"

    class Meta:
        constraints = [
            # 중복 북마크를 방지하는 가장 중요한 규칙
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_post_bookmark')
        ]
        ordering = ['-created_at']