from requests.models import Response
from rest_framework.views import APIView
from .models import Notification
from .selializers import NftListSerializer
from rest_framework import status
from rest_framework.response import Response


class NotificationList(APIView):
    # 유저의 알람목록 조회
    def get(self, request):
        nfts=Notification.objects.filter(user=request.user)
        serializer=NftListSerializer(nfts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationCheck(APIView):
    # 유저의 새로운 알림 표시
    def get(self, request):
        check = Notification.objects.filter(
            user=request.user,
            is_read=False).exists()
        return Response({'new': check}, status=status.HTTP_200_OK)

    # 전체 알림 읽음
    def patch(self, request):
        Notification.objects.filter(user=request.user).update(is_read=True)
        return Response({"message": "전체 알림 읽음" }, status=status.HTTP_200_OK)

class NotificationCheckDetail(APIView):
    # 특정 알림 읽음
    def patch(self, request, pk):  # 본인만 수정할 수 있도록 필터링
        Notification.objects.filter(id=pk, user=request.user).update(is_read=True)
        return Response({"message": "특정 알림 읽음"}, status=status.HTTP_200_OK)
