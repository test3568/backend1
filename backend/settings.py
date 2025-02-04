from pathlib import Path

from config import Config

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = Config.DJANGO_DEBUG
SECRET_KEY = Config.DJANGO_SECRET_KEY

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_WHITELIST = Config.CORS_ORIGIN_WHITELIST
CSRF_TRUSTED_ORIGINS = Config.CSRF_TRUSTED_ORIGINS

INSTALLED_APPS = [
    'daphne',
    'corsheaders',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'rest_framework_gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'polygons.apps.PolygonsConfig',
    'app.apps.AppConfig',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'django.contrib.gis'
]

STATIC_URL = '/static/'
STATIC_ROOT = '/usr/app/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ]
        }
    }
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Azimut API',
    'DESCRIPTION': 'Azimut auto-generated docs',
    'VERSION': "1.0.0",
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    # "SCHEMA_PATH_PREFIX": "/v1"
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'backend.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': Config.POSTGIS_USER,
        'PASSWORD': Config.POSTGIS_PASSWORD,
        'HOST': Config.POSTGIS_HOST,
        'PORT': Config.POSTGIS_PORT,
        'OPTIONS': {
            'pool': True,
        },
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# gdal-config --libs
GDAL_LIBRARY_PATH=Config.GDAL_LIBRARY_PATH
# geos-config --libs
GEOS_LIBRARY_PATH=Config.GEOS_LIBRARY_PATH

ASGI_APPLICATION = 'backend.asgi.application'

AUTH_USER_MODEL = 'polygons.User'

CELERY_BROKER_URL = f'amqp://{Config.AMQP_USER}:{Config.AMQP_PASSWORD}@{Config.AMQP_HOST}:{Config.AMQP_PORT}'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ["application/json", "application/x-python-serialize"]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(Config.REDIS_HOST, Config.REDIS_PORT)],
        },
    },
}
CHANNEL_GROUP_NAME = 'all'

CACHE_POLYGONS_GET_KEY = "polygons_get"
CACHE_INTERSECTIONS_GET_KEY = "intersections_get"
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

KAFKA_SERVER = f'{Config.KAFKA_HOST}:{Config.KAFKA_PORT}'
KAFKA_CONSUMER_TOPIC = Config.KAFKA_CONSUMER_TOPIC
KAFKA_PRODUCER_TOPIC = Config.KAFKA_PRODUCER_TOPIC

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'custom': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s %(asctime)s - %(message)s',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'custom',
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": Config.DJANGO_LOG_LEVEL,
            "propagate": False,
        },
        'app': {
            'handlers': ['console'],
            'level': Config.APP_LOG_LEVEL,
            'propagate': False,
        }
    }
}
