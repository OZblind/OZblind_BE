from urllib import response

import pytest
from django.urls import reverse
from rest_framework import status
from ..models import OzKey
from datetime import datetime, timedelta

@pytest.mark.django_db
def test_get_tags_success(auth_client, test_user):

    # 예시 데이터
    OzKey.objects.create(
        user=test_user,
        tag_number=7,
        tag_class='A',
        expried_at=datetime.now() + timedelta(days=30)
    )

    assert response.status_code == status.HTTP_200_OK
    assert 'tags' in response.data
    assert response.data['tags'] == ['A-7']