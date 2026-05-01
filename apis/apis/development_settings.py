from .base_settings import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.1.5', 'localhost', '127.0.0.1']

'''
#use offline local disk postgreSQL Connection
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('ENGINE',''),
        'NAME': os.environ.get('NAME',''),
        'USER': os.environ.get('USER',''),
        'PASSWORD' : os.environ.get('PASSWORD',''),
        'HOST': os.environ.get('HOST',''),
        'PORT': os.environ.get('PORT',''),
    }
}
'''

# online superbase cloud PostgreSQL Connection
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        # Use SSL locally and on Render (required by Supabase)
        ssl_require=True
    )
}

#used on Local Development only
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "dbbackup": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            'location': os.path.join(os.path.dirname(BASE_DIR), 'uploads')
        },
     "staticfiles": {
        "BACKEND": 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
    },
    }

