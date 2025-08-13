import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_get_bookmarks_success(auth_client):
    url = reverse('users:bookmark')
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'bookmakrs' in response.data
