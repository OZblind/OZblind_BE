from django.urls import path
from .views import BookmarkAPIView

urlpatterns = [
    path('<int:post_id>/', BookmarkAPIView.as_view(), name='bookmark-api'),
]