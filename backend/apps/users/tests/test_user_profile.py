import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def tset_update_profile_success(auth_client):
    url = reverse('user-profile')
    payload = {
        'name': '변경된이름',
        'profrilimage': 'https://some.url/image.jpg'
    }
    response = auth_client.post(url, payload, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '<회원정보 수정 완료>'