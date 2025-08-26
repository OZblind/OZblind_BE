from __future__ import annotations
import hmac, hashlib
from typing import Tuple, Dict, Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from .models import User, OzKey, ActivationLog, UserOzkeyMap
import logging

log = logging.getLogger(__name__)
# 예외 클래스 정의

class InvalidGoogleTokenError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class NoActiveKeyConfiguredError(Exception):
    pass


class InvalidKeyError(Exception):
    pass
class IncorrectPasswordError(Exception):pass

class ProfileUpdateError(Exception):pass

class InvalidRefreshTokenError(Exception):pass

class SocialReauthRequired(Exception):pass

class ProfileUpdateError(Exception):pass

# 회원 정보 수정
def update_profile(user, profile_image: str | None):
    if profile_image is None:
        raise ProfileUpdateError("Profile image is required")

    with transaction.atomic():
        user.profile_image = profile_image
        user.save(update_fields=["profile_image"])

# 회원탈퇴
def delete_user(user, id_token_str: str):
    if not id_token_str:
        raise SocialReauthRequired("id_token is required")
    info = verify_google_token(id_token_str)
    sub = info.get("sub")
    if not sub or sub != user.social_id or user.social_provider != "google":
        raise SocialReauthRequired("re-auth failed")
    try:
        for t in OutstandingToken.objects.filter(user_id=user.id):
            BlacklistedToken.objects.get_or_create(token=t)
    except Exception as e:
        print(f"[delete_user_social] Token blacklist failed: {e}")

    user.delete()


# revoke_token
def revoke_token(refresh_token_str: str):
    try:
        t = RefreshToken(refresh_token_str)
        if t.payload.get('token_type') != 'refresh':
            raise InvalidRefreshTokenError('wrong token type: expected refresh')
        try:
            t.blacklist()
        except TokenError as e:
            if 'blacklisted' in str(e).lower():
                log.info('refresh already blacklisted')
                return
            raise InvalidTokenError(str(e))
    except Exception as e:
        log.exception('revoke_token failed')
        raise InvalidTokenError(str(e))

# 키 유틸
OZ_SALT = getattr(settings, 'OZ_SALT', None)

if not OZ_SALT:
    raise ImproperlyConfigured('OZ_SALT must be set in settings')
_OZ_SALT_BYTES = OZ_SALT.encode('utf-8')

def _normalize_key(s: str)-> str:
    return " ".join(s.strip().split())

def _hmac_sha256_hex(data_bytes: bytes)-> str:
    return hmac.new(_OZ_SALT_BYTES, data_bytes, hashlib.sha256).hexdigest()

def hash_key(plain: str) -> str:
    if not isinstance(plain, str) or not plain.strip():
        raise ValueError('plain key is required')
    return _hmac_sha256_hex(_normalize_key(plain).encode('utf-8'))

def save_api_key(raw_key: str):
    # 관리자나 콘솔에서 실행 키 저장
    hashed = _hmac_sha256_hex(raw_key.encode())
    OzKey.objects.create(key_hash=hashed)
    print(f" 발급된 키 :{raw_key}")
def verify_key(raw_key: str) -> bool:
    return OzKey.objects.filter(key_hash=hash_key(raw_key)).exists()

# jwt 발급
def _issue_tokens(user, extra: dict | None = None) :
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    if extra:
        for k,v in extra.items():
            refresh[k] = v
            access[k] = v

    return {"access": str(access), "refresh": str(refresh)}

# Google id_token 검증
def verify_google_token(id_token_str: str, audience: Optional[str] = None)-> dict:
    audience = audience or settings.GOOGLE_CLIENT_ID
    try:
        info = google_id_token.verify_oauth2_token(
        id_token_str,
        google_requests.Request(),
        audience
        )
        if info.get('iss') not in {'accounts.google.com', 'https://accounts.google.com'}:
            raise InvalidGoogleTokenError('invalid issuer')
        return info

    except Exception as e:
        raise InvalidGoogleTokenError('invalid google token') from e

# 구글로 가입만 시킴 is_active=False
# 활성화 상태면 토큰 발급
def google_start_minimal(id_token_str: str)-> Dict[str, object]:
    info = verify_google_token(id_token_str, audience=settings.GOOGLE_CLIENT_ID)
    email = info.get('email', '')
    sub = info.get("sub", '')
    pic =info.get("picture", '')
    name = info.get('name', '')

    user, created  =User.objects.get_or_create(
        social_provider='google',
        social_id=sub,
        defaults={
            'email': email,
            'profile_image': pic,
            'is_active': False,
            'role': 'user'
        },
    )
    if not created and pic and user.profile_image != pic:
        user.profile_image = pic
        user.save(update_fields=["profile_image"])
    extra = {"name": name, "picture": pic}


    if not user.is_active and getattr(settings, 'OZ_ALLOW_DEV_ACTIVATION', False):
        user.is_active = True
        user.save(update_fields=["is_active"])
        return {'status': 'activated', **_issue_tokens(user), 'next': '/main'}

    if user.is_active:
        return {'status': 'active', **_issue_tokens(user), 'next': '/main'}
    return {'status': 'pending_activation', 'next': 'activate'}

# 키 검증 -> 활성화 -> 토큰 발급
def _get_active_ozkey(cohort_number: int) -> Optional[OzKey]:
    tag_number = f"{cohort_number}"

    return (
        OzKey.objects
        .filter(is_active=True, tag_number=cohort_number)
        .order_by('-id')
        .first()
    )
def activate_with_key_minimal(
    request,
    id_token_str: str,
    cohort_number: int,
    plain_key: str,
):

    # 사용자 식별
    info = verify_google_token(id_token_str)
    sub = info.get('sub')
    user = User.objects.filter(social_provider='google', social_id=sub).first()
    if not user:
        return Response({'status': 'user_not_found'}, status=status.HTTP_404_NOT_FOUND)

    #이미 활성화된 사용자면 바로 토큰
    if user.is_active:
        return Response({'status': 'active', **_issue_tokens(user), 'next': '/main'}, status=status.HTTP_200_OK)

    # 활성 키 조회
    active_qs = OzKey.objects.filter(is_active=True, tag_number=cohort_number)
    if not active_qs.exists():
        ActivationLog.objects.create(user=user, oz_key=None, ok=False)
        return Response({'status': 'no_active_key'}, status=status.HTTP_400_BAD_REQUEST)

    # 평문 키 해시 계산 후 매칭
    key_hash = hash_key(plain_key)
    ozkey = active_qs.filter(key_hash=key_hash).first()
    if not ozkey:
        # 기수 맞는데 키 틀림
        ActivationLog.objects.create(user=user, oz_key=None, ok=False)
        return Response({'status': 'invalid_key'}, status=status.HTTP_200_OK)

    # 유저-키 매핑 및 활성화
    with transaction.atomic():
        UserOzkeyMap.objects.get_or_create(user=user, oz_key=ozkey)
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        ActivationLog.objects.create(user=user, oz_key=ozkey, ok=True)
    return Response({'status': 'activated', **_issue_tokens(user), 'next': '/main'}, status=status.HTTP_200_OK)


def force_activate_and_issue_tokens(id_token_str: str) -> Dict[str, object]:
    # 개발모드 키없이 활성화
    info = verify_google_token(id_token_str)
    sub = info.get('sub')
    user = User.objects.filter(social_provider='google', social_id=sub).first()
    if not user:
        raise UserNotFoundError('user not found')
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=["is_active"])

    return {'status': 'activated', **_issue_tokens(user), 'next': '/main'}