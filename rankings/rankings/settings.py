"""
Django settings for rankings project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
import os
from typing import List

from django.utils.log import DEFAULT_LOGGING


def generate_secret_key(filename: str) -> None:
    """Generate a file, containing a newly generated secret key."""
    from django.utils.crypto import get_random_string

    chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    key = get_random_string(50, chars)
    with open(filename, "w") as file_handle:
        file_handle.write('"""This file shouldn\'t be commited to repo."""\n')
        file_handle.write("SECRET_KEY = '{}'\n".format(key))


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# This current settings directory
SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))

if os.getenv("DJANGO_SECRET_KEY") is None:
    try:
        from .secret_key import SECRET_KEY
    except ImportError:
        import importlib

        # We create a new secret key file the first time an import is attempted.
        # This simplifies setup for new developers and still allows the key to
        # stay stable in dev environments (useful to maintain sessions even
        # when server constantly restarts due to hot reloading).
        generate_secret_key(os.path.join(SETTINGS_DIR, "secret_key.py"))
        # https://stackoverflow.com/questions/52933869/why-does-importing-fail-after-creating-a-module-under-python-3-on-windows
        importlib.invalidate_caches()
        from .secret_key import SECRET_KEY  # noqa: F401
else:
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", False)

ALLOWED_HOSTS: List[str] = os.getenv(
    "DJANGO_ALLOWED_HOSTS", "*,localhost,host.docker.internal"
).split(",")

APPEND_SLASH = True

# Use logging config similar to Django's default
LOGGING = DEFAULT_LOGGING.copy()
# But enable logging errors to console even when not in debug mode
LOGGING["handlers"]["console"]["filters"] = []  # remove require_debug_true filter

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "massadmin",
    "django_filters",
    "rest_framework",
    "previous.apps.PreviousConfig",
    "drf_spectacular",
]

MIDDLEWARE = [
    "rankings.check_db.CheckDBMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rankings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            os.path.join(BASE_DIR, "previous", "templates", "previous"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "rankings.jinja2.environment",
            "extensions": ["jinja2.ext.with_"],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "rankings.wsgi.application"


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "drf_link_header_pagination.LinkHeaderLimitOffsetPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DB_PATH = os.getenv("DJANGO_DB_PATH")
DB_FILE = os.getenv("DJANGO_DB_FILENAME", "db.sqlite3")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(DB_PATH or BASE_DIR, DB_FILE),
    }
}

# See: https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.getenv("DJANGO_STATIC_ROOT", "/var/www/rankings/static/")
STATIC_URL = os.getenv("DJANGO_STATIC_URL", "/static/")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
