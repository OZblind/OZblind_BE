from rest_framework.test import APITestCase
from backend.apps.users.models import User
from backend.apps.boards.models import Board
from backend.apps.posts.models import Post
from .models import Notification
from django.urls import reverse

class NotificationAPITestCase(APITestCase):
    def setUp(self):
        self.user=User.objects.create_user(
            email='normal.user@example.com',
            social_provider='google',
            social_id='google123456789',
            role='user'
        )
        self.client.force_authenticate(user=self.user)

        self.board=Board.objects.create(
            name="Test Board",
            description="Test Board",
        )

        self.post=Post.objects.create(
            board=self.board,
            user=self.user,
            title="Test Post",
            content="Test Post",
        )

        self.notification1=Notification.objects.create(
            user=self.user,
            post=self.post,
            message="Test Message",
        )
        self.notification2 = Notification.objects.create(
            user=self.user,
            post=self.post,
            message="Test Message2",
        )

    def test_ntf_list_get(self):
        url = reverse('ntf-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_ntf_check_get(self):
        url = reverse('ntf-check')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_ntf_check_patch(self):
        url = reverse('ntf-check')
        res = self.client.patch(url)
        self.assertEqual(res.status_code, 200)

    def test_ntf_detail_patch(self):
        url = reverse('ntf-check-detail', kwargs={'pk': self.notification1.id})
        res = self.client.patch(url)
        self.assertEqual(res.status_code, 200)

        url = reverse('ntf-list')
        res = self.client.get(url)
        print(res.data)