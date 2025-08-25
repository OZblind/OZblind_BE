from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import F

class Reaction(models.Model):
    
    class ReactionType(models.TextChoices):
        LIKE = 'like', '좋아요'
        DISLIKE = 'dislike', '싫어요'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reactions')
    reaction = models.CharField(max_length=10, choices=ReactionType.choices)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id'],
                name='unique_user_reaction_for_content'
            )
        ]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self._state.adding:
            target_object = self.content_object
            if self.reaction == self.ReactionType.LIKE:
                target_object.like_count = F('like_count') + 1
            elif self.reaction == self.ReactionType.DISLIKE:
                target_object.dislike_count = F('dislike_count') + 1

            target_object.save(update_fields=[f'{self.reaction}_count'])
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        target_object = self.content_object
        if self.reaction == self.ReactionType.LIKE and target_object.like_count > 0:
            target_object.like_count = F('like_count') - 1
        elif self.reaction == self.ReactionType.DISLIKE and target_object.dislike_count > 0:
            target_object.dislike_count = F('dislike_count') - 1

        target_object.save(update_fields=[f'{self.reaction}_count'])
        super().delete(*args, **kwargs)