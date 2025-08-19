from django.test import TestCase
import pytest
from unittest.mock import MagicMock

from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from ..services import (
    revoke_token,
    delete_user,
    update_profile,
    InvalidTokenError,
    SocialReauthRequired,
    ProfileUpdateError,
)
from ..models import User

pytestmark = pytest.mark.django_db


# revoke_toeken

def test_revoke_token_success():
    # 성공: 유효한 리프레시 토큰이쭈어지면 성공적으로 블랙리스트에 추가
    user = User.objects.create_user(email='test@example.com')
    refresh = RefreshToken.for_user(user)
    refresh_token_str = str(refresh)

    assert BlacklistedToken.objects.count() == 0

    revoke_token(refresh_token_str)

    assert BlacklistedToken.objects.count() == 1
    assert BlacklistedToken.objects.first().token.token == refresh_token_str

def test_revoke_token_with_invalid_token():
# 싪패
    with pytest.raises(InvalidTokenError):
        revoke_token('invalid_token')

# def test_update_profile_success():
#     user = User.objects.create_user(email='test@example.com', profile_image='test_profile.png')
#     new_image_url = "http://new.image.url/profile.jpg"
#
#     update_profile(user.id, new_image_url)
#
#     user.refresh_from_db()
#     assert user.profile_image == new_image_url

def test_delete_user_success(mocker):
    user_social_id = "123456789"
    user = User.objects.create_user(
    email='delete@me.com',
    social_id=user_social_id,
    social_provider='google'
    )
    dummy_id_token = "dummy.google.id_token"

    mock_verify = mocker.patch(
        'backend.apps.users.services.verify_google_token',
        return_value={'sub': user_social_id}
    )

    assert User.objects.count() == 1

    delete_user(user, dummy_id_token)

    mock_verify.assert_called_once_with(dummy_id_token)
    assert User.objects.count() == 0

