from django.db import models
from django.conf import settings
from django.db.models import F

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

    def save(self, *args, **kwargs):
        # 북마크가 새로 생성될 때만 카운트를 증가시킴
        if self._state.adding:
            self.post.bookmark_count = F('bookmark_count') + 1
            self.post.save(update_fields=['bookmark_count'])
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # 북마크가 삭제될 때만 카운트를 감소시킴
        self.post.bookmark_count = F('bookmark_count') - 1
        self.post.save(update_fields=['bookmark_count'])
        super().delete(*args, **kwargs)