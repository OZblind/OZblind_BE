from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, SurveyPostViewSet, GithubPostViewSet

router = DefaultRouter()
router.register('', PostViewSet, basename='post')
router.register('survey', SurveyPostViewSet, basename='post-survey')
router.register('github', GithubPostViewSet, basename='post-github')

urlpatterns = [
    path('', include(router.urls))
]
