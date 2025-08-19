from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
from django.conf import settings
from django.db.models import Q
from pyasn1.type.tag import Tag


# -------------------------
# Activation Log
# -------------------------
class ActivationLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    oz_key = models.ForeignKey("OzKey", null=True, blank=True, on_delete=models.SET_NULL)
    ok = models.BooleanField()  # 성공/실패
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


# -------------------------
# User & Manager
# -------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일을 입력하세요')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    profile_image = models.URLField(blank=True)

    # 가입 초기엔 비활성(키 인증 전)
    is_active = models.BooleanField(default=False)

    # 소셜 로그인 식별
    social_provider = models.CharField(max_length=20, blank=True, null=True)
    social_id = models.CharField(max_length=100, blank=True, null=True)

    role = models.CharField(max_length=25, default='user')
    is_staff = models.BooleanField(default=True)

    oz_keys = models.ManyToManyField(
        'OzKey',
        through='UserOzKeyMap',
        related_name='users'
    )


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['social_provider', 'social_id'],
                name='social_provider_socialid'
            )
        ]

    def __str__(self):
        return self.email



# -------------------------
# OzKey (기수별 키 정의)
# -------------------------
class OzKey(models.Model):
    KEY_TYPES = (("FE", "Frontend"), ("BE", "Backend"))

    key_hash = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    tag_number = models.IntegerField(verbose_name='기수', null=True)
    tag_classes= models.CharField(max_length=50, verbose_name='클래스', null=True)


    class Meta:
        indexes = [ models.Index(fields=['is_active'])]
    def __str__(self):
        return f"{self.tag_number}기 {self.tag_classes}"

class UserOzkeyMap(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    oz_key = models.ForeignKey(OzKey, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'oz_key')


