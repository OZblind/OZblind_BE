from django.db import models

class Comment(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    root = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='thread_comments')
    content = models.CharField(max_length=255)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('root_id', 'created_at')

    def save(self, *args, **kwargs): # 오버라이딩
        # 댓글 생성때만
        is_new = self.pk is None
        super().save(*args, **kwargs)  # 먼저 save하여 pk(id)를 얻습니다.

        # 최상위 댓글
        if is_new and self.root is None:
            self.root = self
            self.save(update_fields=['root']) # 오직 root만 수정하게 설정
