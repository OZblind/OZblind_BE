import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_delete_user_success(authorized_client):
    url = reverse('user-delete')
    response = auth_client.post(url, {'password': 'testpassword'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == "회원탈퇴 완료"

@pytest.mark.django_db
def test_delete_user_fail_wrong_password(auth_client):
    url = reverse('user-delete')
    respomnse = auth_client.post(url, {'password': 'wrongpassword'}, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert respomnse.data['error'] == "incorrect password"