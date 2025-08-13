from rest_framework.test import APITestCase
from backend.apps.users.models import User
from backend.apps.boards.models import Board
from backend.apps.posts.models import Post
from .models import Comment
from django.urls import reverse

class CommentAPITestCase(APITestCase):
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

        self.comment1=Comment.objects.create(
            user=self.user,
            post=self.post,
            content="Test Comment1",
        )

        self.comment2=Comment.objects.create(
            user=self.user,
            post=self.post,
            root=self.comment1,
            content="Test Comment2",
        )

    def test_cmt_create_post(self):
        url = reverse('cmt-create')
        data={
            'post': self.post.id,
            'content': '루트댓글테스트 등록',
        }
        res = self.client.post(url,data)
        self.assertEqual(res.status_code, 201)

        data={
            'post': self.post.id,
            'parent': self.comment2.id,
            'content': '대댓글 테스트',
        }
        res = self.client.post(url,data)
        self.assertEqual(res.status_code, 201)
        #print(res.data)

    def test_cmt_update_patch(self):
        url = reverse('cmt-update', kwargs={'pk':self.comment1.id})
        data={
            'content': 'update string',
        }
        res = self.client.patch(url,data)
        self.assertEqual(res.status_code, 200)
        #print(res.data)

    def test_cmt_delete(self):
        url = reverse('cmt-update', kwargs={'pk':self.comment1.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 200)
        #print(res.data)

        url=reverse('cmt-update', kwargs={'pk':self.comment2.id})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 204)
        #print('개수는 1개?',Comment.objects.all().count())

    def test_cmt_me_get(self):
        url = reverse('cmt-me')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        print(res.data)