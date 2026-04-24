import os
from pathlib import Path

import environ

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    _ = lambda s: s


root = Path(__file__).resolve().parent.parent.parent
BASE_DIR = root

env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file=str(env_file))

SECRET_KEY = env.str(
    "SECRET_KEY",
    default="PRe0vrb9nRb1qMftrg1gEuETn6ui9FbyeRVx6Y1716lN30Dg0qL8BhdOkzW",
)

DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"] if DEBUG else [])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "djangomix",
    "django_umin",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
]

if DEBUG:
    INSTALLED_APPS.append("django_extensions")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

LANGUAGES = [
    ("en", _("English")),
]

TEMPLATES = [
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
                "django.template.context_processors.media",
            ],
        },
    },
]

DATABASES = {"default": env.db()}
DATABASES["default"]["TEST"] = {
    "NAME": "siteplan_test",
    "USER": "siteplan_test",
}

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

AUTH_USER_MODEL = env.str("AUTH_USER_MODEL", default="siteplan_user.User")

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = env.str("STATIC_URL", default="/static/")
STATIC_ROOT = os.path.join(BASE_DIR, "public")

DJANGO_UMIN_VITE_DEV_MODE = env.bool("DJANGO_UMIN_VITE_DEV_MODE", default=False)
DJANGO_UMIN_VITE_DEV_SERVER_HOST = env.str(
    "DJANGO_UMIN_VITE_DEV_SERVER_HOST", default="0.0.0.0"
)
DJANGO_UMIN_VITE_DEV_SERVER_PORT = env.int(
    "DJANGO_UMIN_VITE_DEV_SERVER_PORT", default=5173
)

_codespace_name = env.str("CODESPACE_NAME", default=None)
codespace_name = None if _codespace_name in (None, "None", "") else _codespace_name
_gcp_domain = env.str("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", default=None)
github_codespaces_port_forwarding_domain = (
    None if _gcp_domain in (None, "None", "") else _gcp_domain
)

if codespace_name and github_codespaces_port_forwarding_domain:
    vite_port = DJANGO_UMIN_VITE_DEV_SERVER_PORT
    DJANGO_UMIN_VITE_DEV_SERVER_URL = env.str(
        "DJANGO_UMIN_VITE_DEV_SERVER_URL",
        default=f"https://{codespace_name}-{vite_port}.{github_codespaces_port_forwarding_domain}",
    )
    DJANGO_UMIN_VITE_DEV_SERVER_PROTOCOL = env.str(
        "DJANGO_UMIN_VITE_DEV_SERVER_PROTOCOL", default="https"
    )
    DJANGO_UMIN_VITE_HMR_PROTOCOL = env.str(
        "DJANGO_UMIN_VITE_HMR_PROTOCOL", default="wss"
    )
    DJANGO_UMIN_VITE_HMR_HOST = env.str(
        "DJANGO_UMIN_VITE_HMR_HOST",
        default=f"{codespace_name}-{vite_port}.{github_codespaces_port_forwarding_domain}",
    )
    DJANGO_UMIN_VITE_HMR_PORT = env.int("DJANGO_UMIN_VITE_HMR_PORT", default=443)
    DJANGO_UMIN_VITE_HMR_CLIENT_PORT = env.int(
        "DJANGO_UMIN_VITE_HMR_CLIENT_PORT", default=443
    )

    codespaces_host = f"{codespace_name}.{github_codespaces_port_forwarding_domain}"
    if codespaces_host not in ALLOWED_HOSTS and "*" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(codespaces_host)

    codespaces_origin = f"https://{codespaces_host}"
    csrf_trusted = env.list("CSRF_TRUSTED_ORIGINS", default=[])
    if codespaces_origin not in csrf_trusted:
        csrf_trusted.append(codespaces_origin)
    CSRF_TRUSTED_ORIGINS = csrf_trusted
else:
    DJANGO_UMIN_VITE_DEV_SERVER_PROTOCOL = env.str(
        "DJANGO_UMIN_VITE_DEV_SERVER_PROTOCOL", default="http"
    )
    DJANGO_UMIN_VITE_DEV_SERVER_URL = env.str(
        "DJANGO_UMIN_VITE_DEV_SERVER_URL", default=None
    )
    DJANGO_UMIN_VITE_HMR_PROTOCOL = env.str(
        "DJANGO_UMIN_VITE_HMR_PROTOCOL", default=None
    )
    DJANGO_UMIN_VITE_HMR_HOST = env.str("DJANGO_UMIN_VITE_HMR_HOST", default=None)
    DJANGO_UMIN_VITE_HMR_PORT = env.int("DJANGO_UMIN_VITE_HMR_PORT", default=None)
    DJANGO_UMIN_VITE_HMR_CLIENT_PORT = env.int(
        "DJANGO_UMIN_VITE_HMR_CLIENT_PORT", default=None
    )
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

SIMPLE_CUSTOMIZE_MODE = env.str("SIMPLE_CUSTOMIZE_MODE", default=True)

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/app/"
LOGOUT_REDIRECT_URL = "/"

WAGTAIL_SITE_NAME = "Siteplan App"

INSTALLED_APPS = ["siteplan_user", "siteplan"] + INSTALLED_APPS
WSGI_APPLICATION = "siteplan.wsgi.application"
ROOT_URLCONF = "siteplan.urls"
LOGIN_TEMPLATE = "siteplan/login.html"
