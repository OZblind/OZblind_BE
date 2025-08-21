import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')  # 쓰면 사용


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'backend.apps.users.apps.UsersConfig',
    'backend.apps.boards.apps.BoardsConfig',
    'backend.apps.posts.apps.PostsConfig',
    'backend.apps.comments.apps.CommentsConfig',
    'backend.apps.reactions.apps.ReactionsConfig',
    'backend.apps.bookmarks.apps.BookmarksConfig',
    'backend.apps.notifications.apps.NotificationsConfig',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}


AUTH_USER_MODEL = 'users.User'


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # 인증 설정
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],

    # 권한 설정
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'OZBlind Board API',
    'DESCRIPTION': 'OZBlind Board 서비스의 백엔드 API 문서입니다.',
    'VERSION': '1.0.0',

    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',

    'SECURITY': [
        {'BearerAuth': []},
    ],
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': "JWT 기반 인증 (Bearer <token>)"
            }
        }
    },
}



LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'



import os
SOCIAL_AUTH_GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')



from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),  # Authorization 헤더에 붙는 타입
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# settings.py

OZ_ALLOW_DEV_ACTIVATION = False
OZ_ENABLE_KEY_ACTIVATION = True


OZ_SALT = "my-super-secret-salt"

CORS_ALLOWED_ORIGINS = [
    # --- Vercel 배포 환경 (Production & Staging) ---
    "https://o-zblind-fe.vercel.app",  # Vercel 메인 배포 주소
    "https://o-zblind-fe-git-develop-ls-projects-b89ad826.vercel.app", # Vercel develop 브랜치 미리보기 주소

    # --- 로컬 개발 환경 ---
    "http://localhost:5173",         # React 개발 서버 (Vite 등)
    "http://127.0.0.1:5173",         # 위와 동일 (IP 주소 접속 대비)

    # 도메인
    "https://api.ozboard.shop",
]

# 쿠키나 인증 헤더(Authorization) 등을 주고받아야 하므로 이 설정은 필수입니다.
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_METHODS = ["GET", "POST", "DELETE", "PUT", "PATCH"]
CORS_ALLOWED_HEADERS = ["Content-Type", "Authorization"]

CSRF_TRUSTED_ORIGINS = ["https://localhost:5173", "https://api.ozboard.shop"]
CSRF_COOKIE_DOMAIN = ".ozboard.shop"