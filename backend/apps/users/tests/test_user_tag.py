from rest_framework.test import APITestCase, APIClient
from backend.apps.users.models import User, OzKey
from django.urls import reverse

class UserAPITestCase(APITestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client: APIClient

    def setUp(self):
        self.ozkey=OzKey.objects.create(
            key_hash='testkey',
            tag_number=11,
            tag_class='BE'
        )

        self.user=User.objects.create_user(
            email='normal.user@example.com',
            social_provider='google',
            social_id='google123456789',
        )

        self.user.oz_keys.set([self.ozkey])
        self.client.force_authenticate(user=self.user)

    def test_user_tag_get(self):
        url = reverse('user-tag')
        res=self.client.get(url)
        self.assertEqual(res.status_code, 200)
        print(res.data)