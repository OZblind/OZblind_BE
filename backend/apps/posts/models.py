from django.db import models
from django.conf import settings

# 이 파일의 목적은 오직 다른 앱의 '의존성'을 해결하기 위함입니다.
class Post(models.Model):
    """
    이 모델은 오직 다른 앱(bookmarks 등)이 ForeignKey로 참조할 수 있도록
    최소한의 뼈대만 갖춘 임시 모델입니다.
    """
    
    # Post 모델이 User 모델을 참조하는 경우가 많으므로, 최소한으로 추가해둡니다.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # bookmarks 앱의 __str__ 메서드에서 'self.post.title'을 사용하므로,
    # 이 title 필드는 오류를 막기 위해 반드시 필요합니다.
    title = models.CharField(max_length=100)

    # 이 모델 자체도 __str__을 가지는 것이 좋습니다. 디버깅에 편리합니다.
    def __str__(self):
        return self.title