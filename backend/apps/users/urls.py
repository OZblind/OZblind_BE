from django.urls import path
from django.views.generic.edit import DeleteView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views
from .models import ActivationLog
from .views import (
    GoogleStartView,
    revoke_view,
    ActivateWithKeyView,
    UpdateProfileView,
    ProfileView,
    DeleteUserView,
    UserTagView
)

urlpatterns = [
    # 구글 소셜
    path('auth/google/start', GoogleStartView.as_view(), name='google-start'),

    # 키 횔성화
    path('auth/activate', ActivateWithKeyView.as_view(), name='auth-activate'),

    # 토큰
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/revoke', revoke_view, name='revoke-token'),

    # 유저
    path('delete', DeleteUserView.as_view(), name='user-delete'),
    path('profile/update', UpdateProfileView.as_view(), name='user-profile'),
    path('profile', ProfileView.as_view(), name='user-profile-view'),

    # 유저 태그 조회
    path('user/tag', UserTagView.as_view(), name='user-tag'),
]