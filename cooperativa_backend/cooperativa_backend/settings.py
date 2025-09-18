from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / Modo ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-unsafe-secret")  # en Render pon un SECRET_KEY real
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Tu servicio en Render + local
ALLOWED_HOSTS = [
    "agrocoop-backend.onrender.com",
    "localhost",
    "127.0.0.1",
]
# permite añadir más hosts por env si hace falta (coma-separado)
ALLOWED_HOSTS += [h for h in os.getenv("ALLOWED_HOSTS_EXTRA", "").split(",") if h]

# Si estás detrás de proxy HTTPS (Render)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Si tu frontend (Netlify) usará cookies/CSRF en peticiones XHR cross-site,
# cambia estas dos líneas a "None" (ojo: requiere HTTPS en ambos lados):
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE   = os.getenv("CSRF_COOKIE_SAMESITE", "Lax")

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "cooperativa",   # tu app
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise para estáticos en Render
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cooperativa_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "cooperativa_backend.wsgi.application"

# --- Base de datos ---
# Render te inyecta DATABASE_URL (Postgres). Ej: postgres://...
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Dev local
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "cooperativa_db"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", "kihomy123"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# Usuario custom (si lo usas)
AUTH_USER_MODEL = "cooperativa.Usuario"

# --- i18n ---
LANGUAGE_CODE = "es-bo"
TIME_ZONE = "America/La_Paz"
USE_I18N = True
USE_TZ = True

# --- Estáticos / Media ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# --- CORS / CSRF ---
# Pon EXACTAMENTE tu dominio Netlify (sin slash)
NETLIFY_ORIGIN = os.getenv("NETLIFY_ORIGIN", "https://agrocoop-frontend.netlify.app")

# CORS: debe listar el FRONTEND (no el backend)
CORS_ALLOWED_ORIGINS = [
    NETLIFY_ORIGIN,  # p.ej. https://agrocoop-frontend.netlify.app
]

# Si prefieres permitir cualquier subdominio *.netlify.app:
# (CORS no acepta wildcards en ORIGINS, así que usamos REGEX)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.netlify\.app$",
]

CORS_ALLOW_CREDENTIALS = True

# CSRF: también el FRONTEND (sin slash). Puedes incluir wildcard de netlify
CSRF_TRUSTED_ORIGINS = [
    NETLIFY_ORIGIN,           # p.ej. https://agrocoop-frontend.netlify.app
    "https://*.netlify.app",  # cualquier subdominio de Netlify
    "https://agrocoop-backend.onrender.com",  # opcional, no hace daño
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
