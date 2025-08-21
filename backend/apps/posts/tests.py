from rest_framework.test import APITestCase
from backend.apps.users.models import User, OzKey
from backend.apps.boards.models import Board
from backend.apps.posts.models import Post
from django.urls import reverse

class PostAPITestCase(APITestCase):
    # 6번게시물은 view=0
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
            role='user'
        )
        self.user.oz_keys.set([self.ozkey])
        self.client.force_authenticate(user=self.user)

        self.board=Board.objects.create(
            name="Test Board",
            description="Test Board",
        )

        self.post1=Post.objects.create(
            board=self.board,
            user=self.user,
            title="title1",
            content="content1",
            view_count=10
        )
        self.post2 = Post.objects.create(
            board=self.board,
            user=self.user,
            title="title2",
            content="content2",
            view_count=20
        )
        self.post3 = Post.objects.create(
            board=self.board,
            user=self.user,
            title="title3",
            content="content3",
            view_count=30
        )
        self.post4 = Post.objects.create(
            board=self.board,
            user=self.user,
            title="title4",
            content="content4",
            view_count=40
        )
        self.post5 = Post.objects.create(
            board=self.board,
            user=self.user,
            title="title5",
            content="content5",
            view_count=50
        )
        self.post6 = Post.objects.create(
            board=self.board,
            user=self.user,
            title="title6",
            content="content6"
        )

   # 최신 5개
    def test_post_main_get(self):
        url = reverse('main-post')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        #print(res.data[0])

    # 인기 5개 갱신
    def test_post_hot_patch(self):
        url = reverse('hot-post')
        res = self.client.patch(url)
        self.assertEqual(res.status_code, 200)
        #print(res.data)

    # 인기 5개 조회
    def test_post_hot_get(self):
        url = reverse('hot-post')
        self.client.patch(url)

        url = reverse('hot-post')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        # print(res.data)