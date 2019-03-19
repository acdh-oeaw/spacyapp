"""
Django settings for spacyapp project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# see https://docs.djangoproject.com/en/2.0/ref/settings/#file-upload-permissions
# FILE_UPLOAD_PERMISSIONS = 0o644

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.join(__file__, '../'))))

# Application definition
CELERY_BROKER_URL = 'pyamqp://guest@localhost//'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_SERIALIZER = 'json'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tables2',
    'crispy_forms',
    'rest_framework',
    'webpage',
    'enrich',
    'rest_framework.authtoken',
    'django_celery_results'
]

CRISPY_TEMPLATE_PACK = "bootstrap3"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES':
    ('rest_framework.permissions.AllowAny',),
    'DEFAULT_PARSER_CLASSES':
    ('rest_framework.parsers.JSONParser',)
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'spacyapp.urls'

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
                'webpage.webpage_content_processors.installed_apps',
                'webpage.webpage_content_processors.is_dev_version',
                'webpage.webpage_content_processors.get_db_name',
            ],
        },
    },
]

WSGI_APPLICATION = 'spacyapp.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

XTX_URL = "https://xtx.acdh.oeaw.ac.at/exist/restxq/xtx/tokenize/default"
TREETAGGER_URL = "https://linguistictagging.eos.arz.oeaw.ac.at"
JSONPARSER_URL = "https://spacyapp.eos.arz.oeaw.ac.at/query/jsonparser-api/"

SPACYAPP_TEMP_DIR = os.path.join(BASE_DIR, 'tmp')

NLP_MODELS_FOLDER = "/home/sennierer/spacyapp/spacyapp/media/nlp_models/"

SPACYAPP_PROFILES = [
    {
        'title': 'tei_to_tei_de',
        'verbose': 'TEI to TEI (German)', 
        'description': '''Uses Xtx service to tokenize the TEIs and Spacy to enrich it.
        Returns enriched TEIs. Uses the standard German spacy model for enrichment and
        the Default profile for Xtx.
        ''',
        'pipeline': {'nlp_pipeline': [('acdh-tokenizer',
                                       {'profile': 'default'}),
                                      ('spacy',
                                       {'language': 'de'})],
                     "zip_type": "zip",
                     "file_type": "application/xml+tei",
                     "out_format": "application/xml+tei"}
    },
    {
        'title': 'txt_to_json_de',
        'verbose': 'Plain text to Json (German)',
        'description': '''Uses Spacy to enrich a plain text.
        Returns enriched Json. Uses the standard German spacy model for enrichment.
        ''',
        'pipeline': {'nlp_pipeline': ('spacy', {'language': 'de'}),
                     "zip_type": "zip",
                     "file_type": "text/plain",
                     "out_format": "application/json+acdhlang"}
    }
] 
