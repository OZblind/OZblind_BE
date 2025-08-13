# from django.contrib import admin
# from django import forms
# from django.contrib import messages
# from django.conf import settings
# import hmac, hashlib
# from django.apps import apps
#
# from .models import User,  OzKey, ActivationLog
#
# # 공통 유틸
# OZ_SALT = getattr(settings, 'OZ_SALT', "change-me")
#
# def hash_key(plain:str)-> str:
#     return hmac.new(OZ_SALT.encode(), plain.encode(), hashlib.sha256).hexdigest()
#
# # OzKey 폼
#
# # OzKey 폼
# class OzKeyAdminForm(forms.ModelForm):
#     # tags_input 필드를 Form에 추가
#     tags_input = forms.CharField(
#         required=False,
#         help_text="태그들을 쉼표(,)로 구분하여 입력하세요."
#     )
#
#     class Meta:
#         model = OzKey
#         fields = '__all__'
#         # 'tags' 필드를 폼에서 숨김. tags_input으로 대체
#         # fields = ('plain_key', 'is_active') # 필드 목록을 명시적으로 지정
#         exclude = ('tags',) # 또는 exclude를 사용
#
#     def save(self, commit=True):
#         obj = super().save(commit=False)
#         plain = self.cleaned_data.get('plain_key')
#         if plain:
#             obj.key_hash = hash_key(plain)
#
#         # tags_input 필드 처리
#         names = [n.strip() for n in (self.cleaned_data.get('tags_input') or '').split(',') if n.strip()]
#
#         if commit:
#             obj.save()
#
#         if names:
#             # apps.get_model로 Tag 모델을 안전하게 가져옴
#             Tag = apps.get_model('tags', 'Tag')
#             tags = []
#             for name in names:
#                 tag, _ = Tag.objects.get_or_create(name=name)
#                 tags.append(tag)
#
#             # 기존 태그들을 지우고 새로운 태그들을 추가
#             obj.tags.set(tags)
#
#         return obj
#         # names = [n.strip() for n in (self.cleaned_data.get('tags_input') or '').spolit(',') if n.strip()]
#         # if names:
#         #     # from backend.apps.tags.models import Tag
#         #     tags = []
#         #     for name in names:
#         #         tag, _ = Tag.objects.get_or_create(name=name)
#         #         tags.append(tag)
#         #         obj.tags.add(*tags)
#         # return obj
#
# # Inlines
# class ActivationLogInline(admin.TabularInline):
#     model = ActivationLog
#     extra = 0
#     readonly_fields = ('oz_key','ok','created_at')
#     can_delete = False
#     ordering = ('-created_at',)
#
# # User Admin
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('email', 'is_active', 'role', 'social_provider', 'created_at')
#     list_filter = ('is_active', 'role', 'social_provider', 'created_at')
#     search_fields = ('email', 'social_id')
#     date_hierarchy = 'created_at'
#     inlines = [ActivationLogInline]
#
#     actions = ['activate_users', 'deactivate_users']
#
#     @admin.action(description="선택 사용자 활성화(관리자 수동")
#     def activate_users(self, request, queryset):
#         updated = queryset.filter(is_active=False).update(is_active=True)
#         self.message_user(request, f"{updated}명 활성화 완료", level=messages.SUCCESS)
#
#     @admin.action(description="선택 사용자 비활성화")
#     def deactivate_users(self, request, queryset):
#         cnt = queryset.update(is_active=False)
#         self.message_user(request, f"{cnt}명 비활성화 완료", level=messages.WARNING)
#
#
# # OzKey admin
# @admin.register(OzKey)
# class OzKeyAdmin(admin.ModelAdmin):
#     form = OzKeyAdminForm
#     list_display = ('id', 'is_active', 'tags_list' )
#     list_filter = ('is_active',)
#     readonly_fields = ('key_hash',)
#     filter_horizontal = ('tags',)
#
#     def tags_list(self, obj):
#         return ', '.join(obj.tags.values_list('name', flat=True))
