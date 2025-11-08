"""
Django settings for AI Chat Portal project.

Built for: Intelligent Conversation Management System
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here-change-this')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,192.168.229.1').split(',')

# ==================== INSTALLED APPS ====================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',  # ✅ MUST be here for CORS
    'django_filters',
    
    # Local apps
    'conversations.apps.ConversationsConfig',
]

# ==================== MIDDLEWARE CONFIGURATION ====================
# ✅ CRITICAL: Order matters! Follow this exact sequence

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # 1. Security
    'corsheaders.middleware.CorsMiddleware',                   # 2. CORS (BEFORE Common)
    'django.middleware.common.CommonMiddleware',               # 3. Common
    'django.middleware.csrf.CsrfViewMiddleware',               # 4. CSRF
    'django.contrib.sessions.middleware.SessionMiddleware',    # 5. Sessions
    'django.contrib.auth.middleware.AuthenticationMiddleware', # 6. Auth (AFTER Sessions)
    'django.contrib.messages.middleware.MessageMiddleware',    # 7. Messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 8. Security headers
]

# ==================== CORS CONFIGURATION ====================

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://192.168.229.1:3000',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'HEAD',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-request-id',  # ✅ ADD THIS LINE
]
 

CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']

# ==================== REST FRAMEWORK ====================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # ✅ Changed to AllowAny for frontend
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# ==================== URL CONFIGURATION ====================

ROOT_URLCONF = 'config.urls'

# ==================== TEMPLATES ====================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==================== WSGI APPLICATION ====================

WSGI_APPLICATION = 'config.wsgi.application'

# ==================== DATABASE ====================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ai_chat_portal'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}

# ==================== PASSWORD VALIDATION ====================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==================== INTERNATIONALIZATION ====================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# ==================== STATIC & MEDIA FILES ====================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# ==================== DEFAULT PRIMARY KEY FIELD ====================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== SECURITY SETTINGS ====================

SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'

SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'

CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'

SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))

SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False') == 'True'

SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'False') == 'True'

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://192.168.229.1:3000',
]

# ==================== SESSION CONFIGURATION ====================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_AGE = int(os.getenv('SESSION_TIMEOUT', '86400'))  # 24 hours

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = 'Lax'

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ==================== LOGGING ====================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'conversations': {
            'handlers': ['console', 'file'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# ==================== APPLICATION SETTINGS ====================

APP_NAME = os.getenv('APP_NAME', 'AI Chat Portal')

APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '2000'))

MAX_CONVERSATION_LENGTH = int(os.getenv('MAX_CONVERSATION_LENGTH', '100000'))

# ==================== FILE UPLOAD SETTINGS ====================

MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '5242880'))  # 5MB

UPLOAD_EXTENSIONS = os.getenv('UPLOAD_EXTENSIONS', 'jpg,jpeg,png,pdf,txt,csv').split(',')

# ==================== AI PROVIDER SETTINGS ====================

AI_PROVIDER = os.getenv('AI_PROVIDER', 'lm_studio')

LM_STUDIO_API_URL = os.getenv('LM_STUDIO_API_URL', 'http://192.168.229.1:1234/v1')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')

# ==================== FEATURE FLAGS ====================

ENABLE_EXPORT = os.getenv('ENABLE_EXPORT', 'True') == 'True'

ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True') == 'True'

ENABLE_SEMANTIC_SEARCH = os.getenv('ENABLE_SEMANTIC_SEARCH', 'True') == 'True'

ENABLE_SENTIMENT_ANALYSIS = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'True') == 'True'

# ==================== CELERY CONFIGURATION (Optional) ====================

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

CELERY_ACCEPT_CONTENT = ['json']

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_SERIALIZER = 'json'

# Create logs directory if it doesn't exist
logs_dir = BASE_DIR / 'logs'
logs_dir.mkdir(exist_ok=True)
