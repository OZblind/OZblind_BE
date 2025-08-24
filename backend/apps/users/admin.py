from django.contrib import admin
from django import forms
from django.conf import settings
import hmac, hashlib

from .models import User, OzKey, ActivationLog, UserOzkeyMap

# 공통 유틸
OZ_SALT = getattr(settings, 'OZ_SALT', "change-me")

def hash_key(plain:str)-> str:
    return hmac.new(OZ_SALT.encode(), plain.encode(), hashlib.sha256).hexdigest()

# OzKey 폼
class OzKeyAdminForm(forms.ModelForm):
    plain_key = forms.CharField(max_length=100, label="Plain Key")

    class Meta:
        model = OzKey
        fields = ('tag_number', 'tag_class', 'plain_key')

    def save(self, commit=True):
        obj = super().save(commit=False)
        plain = self.cleaned_data['plain_key']
        obj.key_hash = hash_key(plain)

        if commit:
            obj.save()
        return obj

# User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'social_provider', 'created_at') # is_active 제거
    list_filter = ('role', 'social_provider', 'created_at') # is_active 제거
    search_fields = ('email', 'social_id')
    date_hierarchy = 'created_at'
    # inlines = [ActivationLogInline] # ActivationLogInline 제거
    # actions = ['activate_users', 'deactivate_users'] # 액션 제거

    # @admin.action(description="선택 사용자 활성화(관리자 수동") # 액션 정의 제거
    # def activate_users(self, request, queryset):
    #     updated = queryset.filter(is_active=False).update(is_active=True)
    #     self.message_user(request, f"{updated}명 활성화 완료", level=messages.SUCCESS)

    # @admin.action(description="선택 사용자 비활성화") # 액션 정의 제거
    # def deactivate_users(self, request, queryset):
    #     cnt = queryset.update(is_active=False)
    #     self.message_user(request, f"{cnt}명 비활성화 완료", level=messages.WARNING)


# OzKey admin
@admin.register(OzKey)
class OzKeyAdmin(admin.ModelAdmin):
    form = OzKeyAdminForm
    list_display = ('id', 'tag_number', 'tag_class', 'key_hash') # is_active 제거
    # list_filter = ('is_active',) # is_active 필터 제거
    readonly_fields = ('key_hash',)
    filter_horizontal = ('users',) # ManyToMany 필드 표시

# ActivationLog admin
@admin.register(ActivationLog)
class ActivationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'oz_key', 'ok', 'created_at')
    list_filter = ('ok', 'created_at')
    readonly_fields = ('user', 'oz_key', 'ok', 'created_at')