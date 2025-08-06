from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
from django.utils import timezone
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일을 입력하세요')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(max_length=50, unique=True)
    authenticated = models.BooleanField(default=False) # 오즈인증
    social_provider = models.CharField(max_length=20) # 소셜 제공자
    social_id = models.CharField(max_length=100, unique=True) # 소셜 고유 ID
    role = models.CharField(max_length=25) # 권한

    is_active = models.BooleanField(default=True)  # 필수
    is_staff = models.BooleanField(default=False)  # 관리자 페이지 여부 접근

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.email} ({self.role})"

# OzKey
class OzKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag_number = models.IntegerField()
    tag_class = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - {self.tag_number}"