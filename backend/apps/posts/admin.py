# backend/apps/posts/admin.py

from django.contrib import admin
from .models import Post  # 바로 옆에 있는 models.py 파일에서 Post 모델을 가져옵니다.

# 이 한 줄이 바로 "초대장에 이름을 적는" 행위입니다.
admin.site.register(Post)