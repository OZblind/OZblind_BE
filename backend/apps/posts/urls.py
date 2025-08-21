from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, SurveyPostViewSet, GithubPostViewSet, MainPostView, HotPostView

router = DefaultRouter()
router.register('', PostViewSet, basename='post')

urlpatterns = [
    path('main', MainPostView.as_view(), name='main-post'),
    path('hot', HotPostView.as_view(), name='hot-post'),

    # 설문 게시글 생성 URL
    path('survey/', SurveyPostViewSet.as_view({'post': 'create'}), name='survey-post-create'),
    # 설문 게시글 상세 조회 URL
    path('survey/<int:pk>/', SurveyPostViewSet.as_view({'get': 'retrieve'}), name='survey-post-detail'),
    # 수정: POST /api/posts/survey/{pk}/edit/
    path('survey/<int:pk>/edit/', SurveyPostViewSet.as_view({'post': 'edit'}), name='survey-edit'),

    # GitHub 게시글 생성 URL
    path('github/', GithubPostViewSet.as_view({'post': 'create'}), name='github-post-create'),
    # GitHub 게시글 상세 조회 URL
    path('github/<int:pk>/', GithubPostViewSet.as_view({'get': 'retrieve'}), name='github-post-detail'),
    # 수정: POST /api/posts/github/{pk}/edit/
    path('github/<int:pk>/edit/', GithubPostViewSet.as_view({'post': 'edit'}), name='github-edit'),

    path('', include(router.urls)),






]
