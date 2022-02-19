"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from celery.schedules import crontab
from .celery import detect_tasks
import os
import environ
from kombu import Exchange, Queue
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    EMAIL_USE_TLS=bool,
    STRIPE_LIVE_MODE=bool,
)
# reading .env file
environ.Env.read_env('./.env')
SENTRY = env('SENTRY')
if SENTRY is True:
    sentry_sdk.init(
        dsn=env('SENTRY_URL'),
        integrations=[DjangoIntegration(), RedisIntegration()],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )



# False if not in os.environ
DEBUG = env('DEBUG')

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


INTERNAL_IPS = [
    '127.0.0.1',
]

ALLOWED_HOSTS = ['*']

#SIGNING_BACKEND = 'django_cryptography.core.signing.TimestampSigner'


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_celery_results',
    'django_celery_beat',
    'debug_toolbar',
    'djstripe',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',
    #'django_rest_passwordreset',
    'corsheaders',
    'django_filters',
    'rest_framework_datatables',
    'bootstrap4',
    'crispy_forms',
    'users',
    'core',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

SITE_ID = 1
CORS_ALLOW_ALL_ORIGINS = True
REST_AUTH_SERIALIZERS = {
    # Changed
    'USER_DETAILS_SERIALIZER': 'users.serializers.UserDetailsSerializerWithType',
}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'app.urls'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
GOOGLE_API_KEY = env('GOOGLE_API_KEY')
STRIPE_LIVE_SECRET_KEY = env('STRIPE_LIVE_SECRET_KEY')
STRIPE_TEST_SECRET_KEY = env('STRIPE_TEST_SECRET_KEY')
STRIPE_LIVE_MODE = env('STRIPE_LIVE_MODE')
DJSTRIPE_WEBHOOK_SECRET = env('DJSTRIPE_WEBHOOK_SECRET')
DJSTRIPE_USE_NATIVE_JSONFIELD = env('DJSTRIPE_USE_NATIVE_JSONFIELD')
DJSTRIPE_FOREIGN_KEY_TO_FIELD = env('DJSTRIPE_FOREIGN_KEY_TO_FIELD')
STRIPE_TEST_PUBLIC_KEY = env('STRIPE_TEST_PUBLIC_KEY')
REDIS_HOST = env('REDIS_HOST')

USE_DJANGO_JQUERY = False
JQUERY_URL = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'app.wsgi.application'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}


CELERY_BROKER_URL = f'redis://{REDIS_HOST}:6379'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
#CELERY_IMPORTS = detect_tasks(BASE_DIR)
CELERY_QUEUES = (
    Queue('default', Exchange('default', type='direct'), routing_key='default'),
    Queue('acme', Exchange('acme', type='direct'), routing_key='acme'),
)
CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
#
CELERY_TASK_ROUTES = ({'core.tasks.get_certs': {
    'queue': 'acme',
    'routing_key': 'acme'
}},)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'app.auth.TokenAuthSupportQueryString',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.HTMLFormRenderer',
        'drf_aggregates.renderers.AggregateRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 50,
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")


ACCOUNT_LOGIN_REDIRECT_URL = '/services/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/account/login/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/order/'
LOGIN_URL = '/account/login/'

DISCOURSE_BASE_URL = env('DISCOURSE_URL')
DISCOURSE_SSO_SECRET = env('DISCOURSE_SECRET')

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
