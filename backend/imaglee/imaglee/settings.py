import os
import dj_database_url

from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv


# Base directory
#
    BASE_DIR = Path(__file__).resolve().parent.parent
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Returns directory in which this settings.py file is


# Load environment variables from .env file
#
    load_dotenv( os.path.join( BASE_DIR, '../../.env' ))


# Get secrets from Docker Secret
#
    def get_secret(secret_name):
        try:
            with open( f'/run/secrets/{secret_name}' ) as f:
                return f.read().strip()
        
        except IOError:
            return os.getenv( secret_name.upper() )


# Security settings
#
    SECRET_KEY = get_secret('django_secret_key')
    DEBUG = os.getenv('DEBUG', 'False') == 'True' # In production needs to be set to False
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
    SITE_ID = 1
    
    CORS_ALLOWED_ORIGINS = [
         "http://localhost:8080",  # Vue.js frontend
         "http://localhost:80",    # Nginx server
         "http://localhost:8000",  # Django backend
    ]


# Applications definition
#
    INSTALLED_APPS = [
        # Django default apps
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.flatpages',
        'django.contrib.redirects',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        
        # Imaglee apps
        'app_activities',
        'app_courses',
        'app_edu',
        'app_workshops',
        'app_my_imaglee',
        'app_core',
        
        # Wagtail apps
        'app_wagtail.contrib.forms',
        'app_wagtail.contrib.redirects',
        'app_wagtail.embeds',
        'app_wagtail.sites',
        'app_wagtail.users',
        'app_wagtail.snippets',
        'app_wagtail.documents',
        'app_wagtail.images',
        'app_wagtail.search',
        'app_wagtail.admin',
        'app_wagtail.core',
        'app_wagtail.locales',
        'app_wagtail.modelcluster',  # Own library that are part of Wagtail
        'app_wagtail.taggit',        # Own library that are part of Wagtail
        
        # Third-party apps
        'graphene_django',
        'channels',
        'corsheaders',
    ]
    
# Middleware definition
#
    MIDDLEWARE = [
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'app_wagtail.contrib.redirects.middleware.RedirectMiddleware',
        'graphql_jwt.middleware.JSONWebTokenMiddleware',  # JWT Middleware
        'corsheaders.middleware.CorsMiddleware',
    ]


# Templates settings with i18n context processor
#
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
                    'django.template.context_processors.i18n',
                ],
            },
        },
    ]


# Graphene settings
#
    GRAPHENE = {
        'SCHEMA': 'imaglee.graphql_schema.schema',  # Path starts with Django project name, file is in the same folder as settings.py
        'MIDDLEWARE': [
            'graphql_jwt.middleware.JSONWebTokenMiddleware',
        ],
    }


# ASGI application definition
#
    ASGI_APPLICATION = 'imaglee.asgi.application'
    
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [os.getenv('REDIS_URL', 'redis://redis:6379/1')],
                "password": get_secret('redis_password'),
            },
        },
    }


# Database configuration
#
    DATABASES = {
        'db_django': dj_database_url.parse(
            os.getenv('DATABASE_URL_DJANGO')
            .replace("<username>", get_secret('db_django_user'))
            .replace("<password>", get_secret('db_django_password'))
        ),
        'wagtail': dj_database_url.parse(
            os.getenv('DATABASE_URL_WAGTAIL')
            .replace("<username>", get_secret('db_wagtail_user'))
            .replace("<password>", get_secret('db_wagtail_password'))
        ),
        'apps': dj_database_url.parse(
            os.getenv('DATABASE_URL_APPS')
            .replace("<username>", get_secret('db_apps_user'))
            .replace("<password>", get_secret('db_apps_password'))
        )
    }


# SSL options for databases
#
    ssl_options = {
        'sslmode': 'require',
        'sslrootcert': get_secret('db_sslrootcert'),
        'sslcert': get_secret('db_sslcert'),
        'sslkey': get_secret('db_sslkey'),
    }


# To add db_key into databases settings
#
    for db_key in DATABASES:
        DATABASES[db_key]['OPTIONS'] = ssl_options


# Database routers
#
    DATABASE_ROUTERS = [
        'imaglee.routers.WagtailRouter',
        'imaglee.routers.AppsRouter',
        'imaglee.routers.DjangoRouter',
    ]


# Authentication backends
#
    AUTHENTICATION_BACKENDS = [
        'graphql_jwt.backends.JSONWebTokenBackend',
        'django.contrib.auth.backends.ModelBackend',
    ]


# JWT Authentication settings
#
    GRAPHQL_JWT = {
        'JWT_VERIFY_EXPIRATION': True,
        'JWT_EXPIRATION_DELTA': timedelta(minutes=30),
        'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    }


# Password validation
#
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


# Internationalization, Czech is main language 
#
    LANGUAGE_CODE = 'cs'
    TIME_ZONE = 'Europe/Prague'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    
    # Add supported languages
    LANGUAGES = [
        ('cs', 'Czech'),
        ('en', 'English'),
        # add more languages this way...
    ]
    
    # Path to locale files, because Wagtail is used this is not necessary as we will not use locale files
    LOCALE_PATHS = [
        os.path.join(BASE_DIR, 'locale'),
    ]
    
    # Activate support for Wagtail internationalization
    WAGTAIL_I18N_ENABLED = True
    WAGTAIL_CONTENT_LANGUAGES = LANGUAGES
    WAGTAILADMIN_BASE_LANG = 'cs'


# Static and media files
#
    # Static files (CSS, JavaScript)
    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]
    
    # Wagtail static and media folder settings
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'backend', 'imaglee', 'app_wagtail', 'staticfiles')
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'backend', 'imaglee', 'app_wagtail', 'app_wagtail', 'static'),
    ]
    
    # Wagtail static and Media folder settings - protected
    MEDIA_URL = '/protected-media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'backend', 'imaglee', 'app_wagtail', 'media')
    
    # Storage settings
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {
                "location": MEDIA_ROOT,
            }
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
            "OPTIONS": {
                "location": STATIC_ROOT,
            }
        },
    }
    
    # Wagtail settings for protected media folder
    WAGTAILIMAGES_IMAGE_MODEL = 'app_wagtail.CustomImage'
    WAGTAILIMAGES_RENDITION_MODEL = 'app_wagtail.CustomRendition'


# Default primary key field type
#
    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Sessions settings
#
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    SESSION_DB_ALIAS = 'db_django'  # Using 'db_django' for sessions


# Cache settings
#
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PASSWORD': get_secret('redis_password')
            }
        }
    }


# Log settings
#
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/var/log/django/debug.log',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
    
    
# Wagtail settings
#
    # This is the human-readable name of your Wagtail install which welcomes users upon login to the Wagtail admin.
    WAGTAIL_SITE_NAME = 'Imaglee'
    
    # Wagtail email notifications from address
    # WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = 'wagtail@myhost.io'
    
    # Wagtail email notification format
    # WAGTAILADMIN_NOTIFICATION_USE_HTML = True
    
    # Allowed file extensions for documents in the document library.
    WAGTAILDOCS_EXTENSIONS = ['csv', 'docx', 'key', 'odt', 'pdf', 'pptx', 'rtf', 'txt', 'xlsx', 'zip']
    
    # Reverse the default case-sensitive handling of tags
    TAGGIT_CASE_INSENSITIVE = True