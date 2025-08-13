from django.urls import path
from .views import NotificationAPI, NotificationCheck, NotificationDetail

urlpatterns = [
    path('', NotificationAPI.as_view(), name='ntf'),
    path('<int:pk>', NotificationDetail.as_view(), name='ntf-detail'),
    path('check', NotificationCheck.as_view(), name='ntf-check'),
]