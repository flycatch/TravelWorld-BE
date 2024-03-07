"""
Django settings for TravelWorld project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-kgx&9c0t4r03*y^h5uv+4hx@uob0wb)@$f6e5#8&!jv2qq@&v4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default=[], cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition

INSTALLED_APPS = [
    'admin_reorder',
    'jazzmin',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'drf_yasg',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    'api',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
    'api.middleware.ModelAdminReorderWithNav'
]


ROOT_URLCONF = 'TravelWorld.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': [os.path.join(BASE_DIR, 'api', 'templates')],

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

WSGI_APPLICATION = 'TravelWorld.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'NAME': config('PSQL_DATABASE', default=''),
        'ENGINE': config('PSQL_ENGINE'),
        'USER': config('PSQL_USER', default=''),
        'PASSWORD': config('PSQL_PASSWORD', default=''),
        'HOST': config('PSQL_HOST', default=''),
        'PORT': config('PSQL_PORT', default=''),
    }
}

HASHHID_SALT = '123ABC'
HASHID_MIN_LENGTH = 5

AUTH_USER_MODEL = 'api.BaseUser'
AUTHENTICATION_BACKENDS = [
    'api.backends.BaseUserModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Explore World Admins",

    # # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    # "site_header": "ADMIN PANEL",

    # Welcome text on the login screen
    "welcome_sign": "Welcome to Explore World",
    # "changeform_format": "single",
    # "related_modal_active": True,
    # "hide_models": ['api.Token','api.Group'],
 
    # "show_sidebar": False,
    # "order_with_respect_to": ["api.User", "Make Messages"],

}

ADMIN_REORDER = (
    
    {'app': 'api', 'models': ('api.Agent', 'api.User',),'label': 'Users'},

    {'app': 'api', 
     'models': ('api.Package', 'api.Activity', 'api.Attraction', 'api.Inclusions', 'api.Exclusions','api.PackageCategory'),
     'label': 'Products'},

    {'app': 'api', 'models': ('api.Booking',),'label': 'Bookings'},

    {'app': 'api', 'models': ('api.AgentTransactionSettlement','api.UserRefundTransaction'),'label': 'Transactions'},

    {'app': 'api', 'models': ('api.UserReview',),'label': 'Reviews'},



    {'app': 'api', 
     'models': ('api.Country', 'api.State', 'api.City', 'api.AdvanceAmountPercentageSetting',),
     'label': 'General Settings'},

    # {'app': 'api', 
    #  'models': ('api.PackageCategory', 'api.Currency'),
    #  'label': 'Others'},
    
)

CSRF_TRUSTED_ORIGINS = config("ENV_CSRF_TRUSTED_ORIGINS").split(',')
CORS_ORIGIN_WHITELIST = config("ENV_CORS_ORIGIN_WHITELIST").split(',')
CORS_ORIGIN_REGEX_WHITELIST = config("ENV_CORS_ORIGIN_REGEX_WHITELIST").split(',')
CORS_ALLOW_METHODS = [
   'GET',
   'POST',
   'PUT',
   'PATCH',
   'DELETE',
   'OPTIONS',
]

RAZOR_PUBLIC_KEY=  config('RAZOR_PUBLIC_KEY')
RAZOR_SECRET_KEY = config('RAZOR_SECRET_KEY')


# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
result_backend = config('RESULT_BACKEND')
accept_content = ['application/json']
task_serializer = 'json'
result_serializer= 'json'
broker_connection_retry_on_startup = True

DEFAULT_BASE_URL = config('DEFAULT_BASE_URL',default='')
DEFAULT_BASE_URL_USER_FRONTEND = config('DEFAULT_BASE_URL_USER_FRONTEND',default='')


GOOGLE_OAUTH2_CLIENT_ID = config("GOOGLE_OAUTH2_CLIENT_ID", default="")
GOOGLE_OAUTH2_CLIENT_SECRET = config("GOOGLE_OAUTH2_CLIENT_SECRET", default="")
GOOGLE_OAUTH2_PROJECT_ID = config("GOOGLE_OAUTH2_PROJECT_ID", default="")