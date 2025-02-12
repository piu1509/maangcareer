from pathlib import Path
from os import getenv
import os 

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = getenv('SECRET_KEY') or 'django-insecure-pxc@o)o(9g$b5$bwg++fa)31i&*ut3qxy_*%8)7j_9_3g(j^72'

DEBUG = True

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST= "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'support@maangcareers.com'
# EMAIL_HOST_PASSWORD = 'olglwjgicupnkquh'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Support Email Configuration
SUPPORT_EMAIL_CONFIG = {
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'support@maangcareers.com',
    'EMAIL_HOST_PASSWORD': 'olglwjgicupnkquh',
}

# Payment Email Configuration
PAYMENT_EMAIL_CONFIG = {
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'payments@maangcareers.com',
    'EMAIL_HOST_PASSWORD': 'jemqwowtwmrmdkfb',
}

RAZORPAY_KEY_ID = 'rzp_test_0amUpvjUpYsipq'
RAZORPAY_KEY_SECRET = 'wSXxia64LSpRaUrlbniHjzXV'

RAPID_API_KEY = '80e9565da1mshd638ad229dec3d5p1eb76djsn3668074b6cc8'

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'daphne',
    'channels',
    'channels_redis',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "corsheaders",
    "storages",
    'import_export',
    'rest_framework',
    'knox',
    'django_filters',
    'django_select2',
    
    'userManagement',
    'courseManagement',
    'freeCourseManagement',
    'CRM',
    'newWebsiteManagement',
    'testsManagement',
    'funneldate',
    'mentorManagement',
    'notificationManagement.apps.NotificationmanagementConfig',
    'dataManagement',
    'salesManagement',
    'adminSalesManagement',
    "django_otp",
    "django_otp.plugins.otp_totp",
    "widget_tweaks",
]

IMPORT_EXPORT_USE_TRANSACTIONS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 15
}

REST_KNOX = {
  'USER_SERIALIZER': 'maangcareerers.knox_auth.KonxLoginUserSerializer',
  'TOKEN_LIMIT_PER_USER': 5,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_otp.middleware.OTPMiddleware",
    'notificationManagement.middleware.DisableCSRFOnWebSocket',
]

ROOT_URLCONF = 'maangcareerers.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


ASGI_APPLICATION = 'maangcareerers.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://127.0.0.1:6379/1"]
        },
    },
}

CORS_ALLOWED_ORIGINS = (
    'http://localhost:3000', 
    'https://django.maangcareers.com',
    'https://dev.maangcareers.com',
    'https://qa.maangcareers.com',
    'https://www.maangcareers.com',
    'https://maangcareers.com',
    'http://devdjango.maangcareers.com',
    'https://devdjango.maangcareers.com',
    'https://dev.maangcareers.in',
    'https://www.maangcareers.in',
)

CORS_ALLOW_CREDENTIALS = True




# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "mydatabase",
    }
}


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


LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = False

USE_TZ = True



STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static",]
# STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'