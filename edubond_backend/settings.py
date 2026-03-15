from datetime import timedelta
import importlib.util
from pathlib import Path

import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-edubond-dev-key-change-me")
DEBUG = os.getenv("DEBUG", "true").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

HAS_CORSHEADERS = importlib.util.find_spec("corsheaders") is not None
HAS_DRF = importlib.util.find_spec("rest_framework") is not None
HAS_SIMPLEJWT = importlib.util.find_spec("rest_framework_simplejwt") is not None

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts",
    "apps.community",
    "apps.marketplace",
    "apps.studyhub",
    "apps.hostel",
    "apps.chat",
]

if HAS_CORSHEADERS:
    INSTALLED_APPS.append("corsheaders")
if HAS_DRF:
    INSTALLED_APPS.append("rest_framework")
if HAS_SIMPLEJWT:
    INSTALLED_APPS.append("rest_framework_simplejwt")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if HAS_CORSHEADERS:
    MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

ROOT_URLCONF = "edubond_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "edubond_backend.wsgi.application"
ASGI_APPLICATION = "edubond_backend.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if HAS_DRF and HAS_SIMPLEJWT:
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ),
        "DEFAULT_PERMISSION_CLASSES": (
            "rest_framework.permissions.IsAuthenticated",
        ),
    }

if HAS_SIMPLEJWT:
    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    }

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "EduBond <noreply@indiraicem.ac.in>")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "false").lower() in {"1", "true", "yes", "on"}
