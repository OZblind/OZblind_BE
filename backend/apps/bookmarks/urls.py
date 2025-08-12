from django.urls import path
from .views import BookmarkAPIView, BookmarkListView

urlpatterns = [
    path('<int:post_id>/', BookmarkAPIView.as_view(), name='bookmark-api'),
    path('me/', BookmarkListView.as_view(), name='bookmark-me-list'),
]