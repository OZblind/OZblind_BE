from django.urls import path
from .views import ReactionAPIView

urlpatterns = [
    path('', ReactionAPIView.as_view(), name='reaction-create-delete'),
]