# backend/apps/bookmarks/tests.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from backend.apps.posts.models import Post
from backend.apps.boards.models import Board 
from .models import Bookmark # models.py에서 진짜 Bookmark를 가져옵니다.

User = get_user_model()

class BookmarkAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='password123')
        self.board = Board.objects.create(name='Test Board')
        self.post = Post.objects.create(
            user=self.user,
            board=self.board,
            title='Test Post for Bookmarks', 
            content='This is a test.'
        )

    def test_bookmark_creation_and_deletion(self):
        self.client.force_authenticate(user=self.user)
        url = f'/api/bookmarks/{self.post.id}/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bookmark.objects.count(), 1)
        self.post.refresh_from_db()
        self.assertEqual(self.post.bookmark_count, 1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bookmark.objects.count(), 0)
        self.post.refresh_from_db()
        self.assertEqual(self.post.bookmark_count, 0)