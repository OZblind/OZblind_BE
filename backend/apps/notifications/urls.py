from django.urls import path
from .views import NotificationList, NotificationCheck, NotificationCheckDetail

urlpatterns = [
    path('', NotificationList.as_view(), name='ntf-list'),
    path('check', NotificationCheck.as_view(), name='ntf-check'),
    path('check/<int:pk>', NotificationCheckDetail.as_view(), name='ntf-check-detail'),
]