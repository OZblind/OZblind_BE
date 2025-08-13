import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_revoke_token_success(auth_client, refresh_token):
    url = reverse('token-revoke')
    response = auth_client.post(url, {'refresh': refresh_token}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == "토큰이 무효화됬습니다"