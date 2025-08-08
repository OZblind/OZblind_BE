from rest_framework.serializers import ModelSerializer
from .models import Notification

class NftListSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'