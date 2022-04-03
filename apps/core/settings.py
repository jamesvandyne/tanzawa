"""
Django settings for web20core project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

import django
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


root = environ.Path(__file__) - 3
env = environ.Env()

if env("ENV_FILE", default=None):
    env.read_env(env("ENV_FILE"))
elif Path(root(".env")).is_file():
    env.read_env(root(".env"))
else:
    pass

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE")

CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.gis",
    "rest_framework",
    "webmention",
    "meta",
    "core",
    "data",
    "data.entry",
    "data.settings",
    "data.streams",
    "data.trips",
    "data.post",
    "indieweb",
    "files",
    "public",
    "wordpress",
    "plugins",
    "interfaces",
]

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "turbo_response.middleware.TurboMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "interfaces.common.middleware.SettingsMiddleware",
    "webmention.middleware.webmention_middleware",
    "plugins.middleware.PluginMiddleware",
]

ROOT_URLCONF = "core.urls"

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(BASE_DIR) / "templates", django.__path__[0] + "/forms/templates"],
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

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL", engine=env.str("DATABASE_ENGINE", default=None))}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = env.str("LANGUAGE_CODE")

TIME_ZONE = env.str("TIME_ZONE")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

THEMES_ROOT = BASE_DIR / "../front/src/themes"
THEMES = [path.stem for path in THEMES_ROOT.iterdir() if path.is_dir()]
THEME_STATICFILE_DIRS = [path for path in THEMES_ROOT.glob("**/static") if path.is_dir()]
STATICFILES_DIRS = [BASE_DIR / "../static/", *THEME_STATICFILE_DIRS]

STATIC_ROOT = env.path("STATIC_ROOT")
MEDIA_ROOT = env.path("MEDIA_ROOT")


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

SPATIALITE_LIBRARY_PATH = env.str("SPATIALITE_LIBRARY_PATH", default=None)

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "post:dashboard"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


PLUGINS = env.list("PLUGINS", default=[])

INSTALLED_APPS.extend(PLUGINS)

PLUGINS_RUN_MIGRATIONS_STARTUP = env.bool("PLUGINS_RUN_MIGRATIONS_STARTUP", True)


# Open Graph Settings

META_SITE_DOMAIN = env.str("DOMAIN_NAME", default="example.com")
META_SITE_PROTOCOL = env.str("PROTOCOL", default="https")
OPEN_GRAPH_USE_OPEN_GRAPH = env.bool("OPEN_GRAPH_USE_OPEN_GRAPH", default=True)
OPEN_GRAPH_USE_TWITTER = env.bool("OPEN_GRAPH_USE_TWITTER", default=True)
OPEN_GRAPH_USE_FACEBOOK = env.bool("OPEN_GRAPH_USE_FACEBOOK", default=True)
