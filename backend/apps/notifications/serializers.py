from rest_framework.serializers import ModelSerializer
from .models import Notification

class NtfListSerializer(ModelSerializer):
    class Meta:
        model = Notification
        exclude = ('user',)