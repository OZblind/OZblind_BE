from django.urls import path
from .views import NotificationList, NotificationCheck, NotificationCheckDetail

urlpatterns = [
    path('', NotificationList.as_view()),
    path('check', NotificationCheck.as_view()),
    path('check/<int:pk>', NotificationCheckDetail.as_view()),
]