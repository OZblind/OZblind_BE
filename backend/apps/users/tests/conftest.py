# users/tests/conftest.py
import pytest
from rest_framework.test import APIClient
from ..models import User
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def mock_google_token():
    with patch('apps.users.views.verify_google_token') as mock:
        mock.return_value ={
            'sub': 'google-id-123',
            'email': 'test@example.com',
            'name': '테스트유저',
            'picture': 'https://some.image/url.png',
        }
        yield mock


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='testpassword',
        name='테스트유저',
        social_id='google-uid-123',
        social_provider='google',
        role='user'
    )

@pytest.fixture
def auth_client(test_user):
    client = APIClient()
    refresh = RefreshToken.for_user(test_user)
    access_token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return client

@pytest.fixture
def refresh_token(test_user):
    return str(RefreshToken.for_user(test_user))
