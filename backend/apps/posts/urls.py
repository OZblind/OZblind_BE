from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, MainPostView, HotPostView

router = DefaultRouter()
router.register('', PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
    path('main', MainPostView.as_view(), name='main-post'),
    path('hot', HotPostView.as_view(), name='hot-post'),
]
