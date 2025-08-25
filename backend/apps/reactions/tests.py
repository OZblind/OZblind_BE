from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from backend.apps.posts.models import Post
from backend.apps.comments.models import Comment
from backend.apps.boards.models import Board
from .models import Reaction

User = get_user_model()

class ReactionAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='password123')
        self.board = Board.objects.create(name='Test Board')
        self.post = Post.objects.create(user=self.user, board=self.board, title='Test Post', content='Content')
        self.comment = Comment.objects.create(user=self.user, post=self.post, content='Test Comment')

    def test_reaction_toggle_on_post(self):
        """게시물에 대한 리액션의 생성, 취소, 변경 시나리오를 모두 테스트"""
        
        self.client.force_authenticate(user=self.user)
        url = '/api/reactions/'

        # 1. "좋아요" 생성 테스트
        data = {'target_type': 'post', 'target_id': self.post.id, 'reaction': 'like'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.like_count, 1)
        self.assertEqual(self.post.dislike_count, 0)

        # 2. "좋아요" 취소 테스트 (똑같은 요청을 한 번 더 보냄)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.like_count, 0)
        self.assertEqual(Reaction.objects.count(), 0) # DB에서 Reaction 객체가 사라졌는지 확인

        # 3. "싫어요"로 변경 테스트 (기존 "좋아요"가 없는 상태에서 "싫어요" 생성)
        data['reaction'] = 'dislike'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.like_count, 0)
        self.assertEqual(self.post.dislike_count, 1)

        # 4. "싫어요" -> "좋아요"로 변경 테스트
        data['reaction'] = 'like'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.like_count, 1)
        self.assertEqual(self.post.dislike_count, 0)