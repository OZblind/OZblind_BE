from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from .services import force_activate_and_issue_tokens
from django.conf import settings

from drf_spectacular.utils import extend_schema, extend_schema_view

from . import services
from .services import (
    google_start_minimal,
    activate_with_key_minimal,
    revoke_token,
    InvalidGoogleTokenError,
    UserNotFoundError,
    NoActiveKeyConfiguredError,
    InvalidKeyError, InvalidTokenError,
    IncorrectPasswordError,
    ProfileUpdateError
)
from .models import User
from .serializers import (
    GoogleAuthSerializer,
    ActivateSerializer,
    UserWithTokenSerializer,
    UserSerializer,
    UserTagSerializer
)
import logging

log = logging.getLogger(__name__)

# google 시작 (가입/로그인 분기)
class GoogleStartView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer

    @extend_schema(
        request=GoogleAuthSerializer,
        responses=UserWithTokenSerializer,
        summary="구글 로그인/회원가입 시작"
    )

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token = serializer.validated_data['id_token']
        try:
            result = google_start_minimal(id_token)
            return Response(result, status=status.HTTP_200_OK)
        except InvalidGoogleTokenError:
            return Response({'error': 'invalid google token'}, status=status.HTTP_401_UNAUTHORIZED)

# 키로 활성화
class ActivateWithKeyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ActivateSerializer

    @extend_schema(
        request=GoogleAuthSerializer,
        responses=UserWithTokenSerializer,
        summary="구글 로그인/회원가입 시작"
    )

    def post(self, request):
        serializer = ActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token_str = serializer.validated_data['id_token']
        cohort_number = serializer.validated_data['cohort_number']
        plain_key = serializer.validated_data['plain_key']

        try:
            data, code = activate_with_key_minimal(
                id_token_str=id_token_str,
                cohort_number=int(cohort_number),
                plain_key=plain_key,
            )
            return Response(data, status=code)
        except InvalidGoogleTokenError:
            return Response({"error": "invalid google token"}, status=status.HTTP_401_UNAUTHORIZED)
        except UserNotFoundError:
            return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        except NoActiveKeyConfiguredError:
            return Response({"error": "no active key configured"}, status=status.HTTP_404_NOT_FOUND)
        except InvalidKeyError:
            return Response({"error": "invalid key"}, status=status.HTTP_401_UNAUTHORIZED)

# JWT: 리프레시, revoke
@extend_schema(
    request=UserWithTokenSerializer,
    responses={'200': None}
)
@api_view(['POST'])
@permission_classes([AllowAny])

def revoke_view(request):
    refresh_token_str = request.data.get('refresh')
    if not refresh_token_str:
        return Response({'error': 'refresh_token is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = revoke_token(refresh_token_str)
        token.blacklist()
        return Response({'status': 'revoked'}, status=status.HTTP_200_OK)
    except InvalidTokenError as e:
        return Response({'error': 'invalid token', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 인증 필요한 사용자 api
class DeleteUserView(APIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = GoogleAuthSerializer

    @extend_schema(
        request=GoogleAuthSerializer,
        responses={"200": {"type": "object"}},
        summary="회원탈퇴"
    )

    def post(self, request):
        user = request.user
        # 개발 테스트
        if settings.DEBUG and getattr(user, 'social_provider', None) == 'google':
            user.delete()
            return Response({'status':'success', 'message': '회원탈퇴 완료'}, status=status.HTTP_200_OK)

        # 일반 계정
        id_token = request.data.get('id_token')
        try:
            services.delete_user_social(request.user, id_token_str=id_token)
            return Response({'satus': 'success', 'message': '회원탈퇴완료'}, status=status.HTTP_200_OK)
        except services.SocialProviderError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfileView(APIView):
    serializer_class = UserSerializer
    @extend_schema(
        request=UserSerializer,
        responses=UserSerializer,
        summary="프로필 수정"
    )

    def put(self, request):
        name = request.data.get('name')
        profile_image = request.data.get('profile_image')
        try:
            services.update_profile(request.user,  profile_image)
            return Response({'status': 'success', 'message': '회원 정보 수정 완료'}, status=status.HTTP_200_OK)
        except services.ProfileUpdateError:
            return Response({'error': 'profile update failed'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    serializer_class = UserSerializer
    @extend_schema(
        responses=UserSerializer,
        summary="내 프로필 조회"
    )

    def get(self, request):
        claims = getattr(request, 'auth', {}) or {}
        return Response({
            'email': request.user.email,
            'name': claims.get('name'),
            'profile_image': request.user.profile_image or claims.get('picture')
        }, status=status.HTTP_200_OK)



# 유저 태그 조회
@extend_schema_view(
    get=extend_schema(
        summary='유저 태그 조회',
        description='API를 요청한 유저에게 할당된 OzKey 태그 정보를 조회합니다.',
        tags=['Tag'],
        responses=UserTagSerializer,
        )
    )
class UserTagView(APIView):
    def get(self, request):
        serializer = UserTagSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)