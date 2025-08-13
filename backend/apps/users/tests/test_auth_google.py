import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

@pytest.mark.django_db
def test_google_signup_success(mock_google_token):
    client = APIClient()
    url = reverse('google-signup')
    response = client.post(url, {'idToken': 'valid_token'}, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert 'accessToken' in response.data

@pytest.mark.django_db
def test_google_login_success(mock_google_token):
    client = APIClient()
    client.post(reverse('google-signup'), {'idToken': 'valid_token'}, format='json')
    response = client.post(reverse('google-login'), {'idToken': 'valid_token'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'accessToken' in response.data

@pytest.mark.django_db
def test_refresh_token_success(mock_google_token):
    client = APIClient()
    signup = client.post(reverse('google-signup'), {'idToken': 'valid_token'}, format='json')
    refresh = signup.data['refreshToken']

    response = client.post(reverse('token-refresh'), {'refresh': refresh}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
