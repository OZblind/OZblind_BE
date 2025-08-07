from django.db import models

class Board(models.Model):
    name = models.CharField(max_length = 20, verbose_name = "게시판 이름")
    description = models.CharField(max_length = 255, verbose_name = "게시판 설명")
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = "게시글 생성 일시")
    updated_at = models.DateTimeField(auto_now = True, verbose_name = "게시글 수정 일시")

    def __str__(self):
        return self.name
    class Meta:
        db_table = "boards"
        verbose_name = "게시판"
        verbose_name_plural = "게시판 목록"