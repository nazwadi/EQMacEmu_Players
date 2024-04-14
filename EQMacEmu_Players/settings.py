"""
Django settings for EQMacEmu_Players project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from django.contrib.messages import constants as messages
import os
from pathlib import Path

from dotenv import load_dotenv
from os.path import join, dirname

load_dotenv()
LS_DB_NAME = os.environ.get("LS_DB_NAME")
LS_DB_USER = os.environ.get("LS_DB_USER")
LS_DB_PASSWORD = os.environ.get("LS_DB_PASSWORD")
LS_DB_PORT = os.environ.get("LS_DB_PORT")
GAME_DB_NAME = os.environ.get("GAME_DB_NAME")
GAME_DB_USER = os.environ.get("GAME_DB_USER")
GAME_DB_PASSWORD = os.environ.get("GAME_DB_PASSWORD")
GAME_DB_PORT = os.environ.get("GAME_DB_PORT")
DJANGO_APP_DB_NAME = os.environ.get("DJANGO_APP_DB_NAME")
DJANGO_APP_DB_USER = os.environ.get("DJANGO_APP_DB_USER")
DJANGO_APP_DB_PASSWORD = os.environ.get("DJANGO_APP_DB_PASSWORD")
DJANGO_APP_DB_PORT = os.environ.get("DJANGO_APP_DB_PORT")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_APP_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ['DEBUG'] == 'TRUE'

ALLOWED_HOSTS = ['loginserver.eqarchives.com', 'eqarchives.com', 'localhost']
#ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://loginserver.eqarchives.com']

# Application definition

INSTALLED_APPS = [
    'accounts.apps.AccountsConfig',
    'common.apps.CommonConfig',
    'characters.apps.CharactersConfig',
    'character_transfer.apps.CharacterTransferConfig',
    'debug_toolbar',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tables2',
    'crispy_forms',
    'crispy_bootstrap4',
    'bootstrap5',
    'items.apps.ItemConfig',
    'npcs.apps.NpcsConfig',
    'recipes.apps.RecipesConfig',
    'polls.apps.PollsConfig',
    'zones.apps.ZonesConfig',
]

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap4-responsive.html'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'EQMacEmu_Players.urls'

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

WSGI_APPLICATION = 'EQMacEmu_Players.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASE_ROUTERS = ['accounts.LoginServerRouter.LoginServerRouter',
                    'accounts.GameServerRouter.GameServerRouter',
                    'common.GameServerRouter.GameServerRouter']

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.mysql",
        "NAME": DJANGO_APP_DB_NAME,
        "USER": DJANGO_APP_DB_USER,
        "PASSWORD": DJANGO_APP_DB_PASSWORD,
        "HOST": "127.0.0.1",
        "PORT": DJANGO_APP_DB_PORT

    },
    "game_database": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": GAME_DB_NAME,
        "USER": GAME_DB_USER,
        "PASSWORD": GAME_DB_PASSWORD,
        "HOST": "127.0.0.1",
        "PORT": GAME_DB_PORT
    },
    "login_server_database": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": LS_DB_NAME,
        "USER": LS_DB_USER,
        "PASSWORD": LS_DB_PASSWORD,
        "HOST": "127.0.0.1",
        "PORT": LS_DB_PORT
    }
}

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

SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = True

#SECURE_HSTS_SECONDS = 2, 592, 000
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = False

CSRF_COOKIE_SECURE = True
#SECURE_SSL_REDIRECT = True

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
#STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'logfile': {
            'class': 'logging.FileHandler',
            'filename': 'server.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logfile'],
        },
    },
}

