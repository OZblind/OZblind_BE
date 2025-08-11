from django.urls import path
from .views import CommentCreate, CommentUpdateDelete

urlpatterns = [
    path('', CommentCreate.as_view(), name='cmt-create'),
    path('<int:pk>', CommentUpdateDelete.as_view(), name='cmt-update'),]