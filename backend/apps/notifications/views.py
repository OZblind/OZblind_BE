from rest_framework.views import APIView
from .models import Notification
from .serializers import NtfListSerializer
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer, OpenApiParameter
from rest_framework import serializers

@extend_schema_view(
    get=extend_schema(
        summary='유저 알림 조회',
        description='API를 요청한 유저의 알림 목록을 조회합니다.',
        tags=['Notification'],
        responses=NtfListSerializer,
        ),
    patch=extend_schema(
        summary='전체 알림 읽음',
        description='API를 요청한 유저의 모든 알림의 상태를 읽음으로 전환합니다.',
        tags=['Notification'],
        responses={
            200: inline_serializer(
                name='ntf-patch',
                fields={'message': serializers.CharField(default='전체 알림 읽음')},
            )
        }
        ),
    delete=extend_schema(
        summary='전체 알림 삭제',
        description='API를 요청한 유저의 모든 알림을 삭제합니다.',
        tags=['Notification'],
        responses={204: None}
    )
)
class NotificationAPI(APIView):
    # 유저의 알림 목록 조회
    def get(self, request):
        nfts=Notification.objects.filter(user=request.user)
        serializer=NtfListSerializer(nfts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 전체 알림 읽음
    def patch(self, request):
        Notification.objects.filter(user=request.user).update(is_read=True)
        return Response({"message": "전체 알림 읽음"}, status=status.HTTP_200_OK)

    # 전체 알림 삭제
    def delete(self, request):
        Notification.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema_view(
    patch=extend_schema(
        summary='특정 알림 읽음',
        description='API를 요청한 유저가 선택한 알림의 상태를 읽음으로 전환합니다.',
        tags=['Notification'],
        responses={
            200: inline_serializer(
                name='ntf-patch',
                fields={'message': serializers.CharField(default='특정 알림 읽음')},
            )
        }
        ),
    delete=extend_schema(
        summary='특정 알림 삭제',
        description='API를 요청한 유저가 선택한 알림을 삭제합니다.',
        tags=['Notification'],
        responses={204: None}
    )
)
class NotificationDetail(APIView):
    # 특정 알림 읽음
    def patch(self, request, pk):  # 본인만 수정할 수 있도록 필터링
        cnt=Notification.objects.filter(id=pk, user=request.user).update(is_read=True)
        if cnt==0:
            return Response({"detail": "Notification not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "특정 알림 읽음"}, status=status.HTTP_200_OK)

    # 특정 알림 삭제
    def delete(self, request, pk):
        cnt=Notification.objects.filter(id=pk, user=request.user).delete()
        if cnt==0:
            return Response({"detail": "Notification not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema_view(
    get=extend_schema(
        summary='새로운 알림 표시',
        description='API를 요청한 유저의 알림 중 읽지 않음 상태의 알림이 있는지 조회합니다.',
        tags=['Notification'],
        responses={
            200: inline_serializer(
                name='ntf-get',
                fields={'new': serializers.BooleanField(default=True)},
            )
        }
        )
    )
class NotificationCheck(APIView):
    # 유저의 새로운 알림 표시
    def get(self, request):
        check = Notification.objects.filter(
            user=request.user,
            is_read=False).exists()
        return Response({'new': check}, status=status.HTTP_200_OK)