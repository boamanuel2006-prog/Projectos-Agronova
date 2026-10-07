import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / '.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-only-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'rest_framework', 'django_filters', 'corsheaders',
    'apps.analytics', 'apps.realtime', 'apps.consultations', 'apps.finance', 'apps.cart', 'apps.orders', 'apps.payments', 'apps.logistics', 'apps.notifications', 'apps.messaging',
    'apps.accounts', 'apps.catalog', 'apps.listings', 'apps.reviews', 'apps.moderation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.common.security.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('POSTGRES_DB', 'agronova'),
    'USER': os.getenv('POSTGRES_USER', 'agronova'),
    'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'agronova'),
    'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
    'PORT': os.getenv('POSTGRES_PORT', '5432'),
}}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Africa/Luanda'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',
                                'rest_framework.filters.SearchFilter',
                                'rest_framework.filters.OrderingFilter'),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_THROTTLE_CLASSES': (
        'apps.common.throttles.AgroNovaAnonRateThrottle',
        'apps.common.throttles.AgroNovaUserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.getenv('API_ANON_RATE', '120/min'),
        'user': os.getenv('API_USER_RATE', '600/min'),
    },
    'PAGE_SIZE': 20,
}

AUTH_USER_MODEL = 'accounts.User'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CORS_ALLOWED_ORIGINS = [x.strip() for x in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',') if x.strip()]

PAYMENT_WEBHOOK_SECRET = os.getenv('PAYMENT_WEBHOOK_SECRET', '')
DEFAULT_PAYMENT_PROVIDER = os.getenv('DEFAULT_PAYMENT_PROVIDER', 'mock')

# Payment provider configuration (secrets must exist only in environment/secret manager)
BITPAY_AO_BASE_URL = os.getenv('BITPAY_AO_BASE_URL', 'https://api-sandbox.bitpay.ao/v1')
BITPAY_AO_SECRET_KEY = os.getenv('BITPAY_AO_SECRET_KEY', '')
BITPAY_AO_WEBHOOK_SECRET = os.getenv('BITPAY_AO_WEBHOOK_SECRET', '')
BITPAY_AO_PAYMENT_METHOD = os.getenv('BITPAY_AO_PAYMENT_METHOD', 'multicaixa_reference')
GPAYGO_AO_BASE_URL = os.getenv('GPAYGO_AO_BASE_URL', 'https://paypay-gateway.gpaygo.com')
GPAYGO_AO_API_KEY = os.getenv('GPAYGO_AO_API_KEY', '')
GPAYGO_AO_WEBHOOK_SECRET = os.getenv('GPAYGO_AO_WEBHOOK_SECRET', '')
GPAYGO_AO_PAYMENT_METHOD = os.getenv('GPAYGO_AO_PAYMENT_METHOD', 'reference')
MOLLIE_API_KEY = os.getenv('MOLLIE_API_KEY', '')
MOLLIE_WEBHOOK_URL = os.getenv('MOLLIE_WEBHOOK_URL', '')
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
MERCADOPAGO_WEBHOOK_SECRET = os.getenv('MERCADOPAGO_WEBHOOK_SECRET', '')
MERCADOPAGO_PAYMENT_METHOD = os.getenv('MERCADOPAGO_PAYMENT_METHOD', 'pix')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
STRIPE_SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL', '')
STRIPE_CANCEL_URL = os.getenv('STRIPE_CANCEL_URL', '')

MARKETPLACE_COMMISSION_RATE = os.getenv('MARKETPLACE_COMMISSION_RATE', '5')

ASGI_APPLICATION = 'config.asgi.application'
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CHANNEL_LAYERS = {'default': {'BACKEND': 'channels_redis.core.RedisChannelLayer', 'CONFIG': {'hosts': [REDIS_URL]}}}
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Production security hardening. Keep DEBUG disabled in production.
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', '1') == '1'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    X_FRAME_OPTIONS = 'DENY'
