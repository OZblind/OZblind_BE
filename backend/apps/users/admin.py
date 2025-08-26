# from django.contrib import admin
# from django import forms
# from django.conf import settings
# import hmac, hashlib
#
# from .models import User, OzKey, ActivationLog, UserOzkeyMap
#
# # 공통 유틸
# OZ_SALT = getattr(settings, 'OZ_SALT', "change-me")
#
# def hash_key(plain:str)-> str:
#     return hmac.new(OZ_SALT.encode(), plain.encode(), hashlib.sha256).hexdigest()
#
# # OzKey 폼
# class OzKeyAdminForm(forms.ModelForm):
#     plain_key = forms.CharField(max_length=100, label="Plain Key")
#
#     class Meta:
#         model = OzKey
#         fields = ('tag_number', 'tag_class', 'plain_key')
#
#     def save(self, commit=True):
#         obj = super().save(commit=False)
#         plain = self.cleaned_data['plain_key']
#         obj.key_hash = hash_key(plain)
#
#         if commit:
#             obj.save()
#         return obj
#
# class UserOzkeyMapInline(admin.TabularInline):
#     model = UserOzkeyMap
#     extra = 1
#
# # User Admin
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('email', 'role', 'social_provider', 'created_at') # is_active 제거
#     list_filter = ('role', 'social_provider', 'created_at') # is_active 제거
#     search_fields = ('email', 'social_id')
#     date_hierarchy = 'created_at'
#
#
# # OzKey admin
# @admin.register(OzKey)
# class OzKeyAdmin(admin.ModelAdmin):
#     form = OzKeyAdminForm
#     list_display = ('id', 'tag_number', 'tag_class') # key_hash 제거
#     readonly_fields = ('key_hash',)
#     inlines = [UserOzkeyMapInline] # UserOzkeyMap 인라인 추가
#
# # ActivationLog admin
# @admin.register(ActivationLog)
# class ActivationLogAdmin(admin.ModelAdmin):
#     list_display = ('user', 'oz_key', 'ok', 'created_at')
#     list_filter = ('ok', 'created_at')
#     readonly_fields = ('user', 'oz_key', 'ok', 'created_at')