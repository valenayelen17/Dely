"""Configuración del panel web de DELY (Django).

El panel no tiene base de datos propia: los datos viven en la API de DELY
(backend/) y se consumen por HTTP desde panel/src/services.py.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

# URL base de la API de DELY, por ejemplo http://127.0.0.1:8000/api/
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/")

INSTALLED_APPS = [
    "panel",
    "django.contrib.sessions",
    "django.contrib.messages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "panel.middleware.TokenApiMiddleware",
]

# Sesión firmada en una cookie (no hace falta base de datos). Guarda el JWT que devuelve la API.
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 8 * 60 * 60  # igual que la validez del token de la API
LOGIN_URL = "login"

ROOT_URLCONF = "panel.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "panel" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "panel.context_processors.dely",
            ],
        },
    },
]

WSGI_APPLICATION = "panel.wsgi.application"

# Sin base propia: la persistencia es responsabilidad de la API.
DATABASES = {}

# Los mensajes de éxito/error viajan en una cookie (no hacen falta sesiones).
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
