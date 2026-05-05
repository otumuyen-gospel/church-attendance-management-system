from .base_settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.1.5', 'localhost', '127.0.0.1']
SITE_URL = os.environ.get("SITE_URL_LOCAL")

#use offline local disk postgreSQL 
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

#used on Local Development only
STORAGES = {
    "default": {
        "BACKEND": os.environ.get('DEFAULT_FILE_STORAGE_DJANGO'),
    },
    "dbbackup": {
        "BACKEND": os.environ.get('DEFAULT_FILE_STORAGE_DJANGO'),
        "OPTIONS": {
            'location': os.path.join(os.path.dirname(BASE_DIR), 'uploads'),
        },
     "staticfiles": {
        "BACKEND": os.environ.get("STATICFILES_STORAGE_DJANGO"),
    },
    },
    }


