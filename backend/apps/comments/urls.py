from django.urls import path
from .views import CommentCreate, CommentUpdateDelete, MyComment

urlpatterns = [
    path('', CommentCreate.as_view(), name='cmt-create'),
    path('<int:pk>', CommentUpdateDelete.as_view(), name='cmt-update'),
    path('me', MyComment.as_view(), name='cmt-me'),
]