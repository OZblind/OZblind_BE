import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db

User = get_user_model()

@pytest.fixture
# 모든 테스트에서 사용함
def client():
    return APIClient()

# 토큰 발급 및 관리
class TestTokenAPI:

    def test_google_login_new_user_success(self, client, mocker):
        dummy_google_token = "dummy.google.id.token.for.new.user"
        google_user_info = {
            'sub': '112223344', # 구글 구유 id
            'email': 'testuser@google.com',
            'name': 'testUser',
            'picture': 'https://placehold.it/32x32',
        }
        mocker.patch(
            'bakcend.apps.users.services.verify_google_token',
            return_Value=google_user_info
        )

        assert User.objects.count() == 0

        # 실행
        response = client.post('/api/auth/google/start', {'id_token': dummy_google_token})

        # 검증
        assert response.status_code == 200

        assert 'access' in response.data
        assert 'refresh' in response.data
        # db에 유저 생겼는지 확인
        assert User.objects.count() == 1
        create_user = User.objects.first()
        assert create_user.email == google_user_info['email']
        assert create_user.social_id == google_user_info['sub']
