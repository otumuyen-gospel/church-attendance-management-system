from .base_settings import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.1.5', 'localhost', '127.0.0.1']


#use offline local disk postgreSQL 
'''
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



# Supabase S3 Uploaded storage alternative Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')

# Tell Django to use Superbase S3 for media files and uploads
DEFAULT1 = os.environ.get('DEFAULT_FILE_STORAGE')
LOCATION_MEDIA_ROOT1 = 'uploads'

# Tell Django to use local disk for media files and uploads
DEFAULT2 = 'django.core.files.storage.FileSystemStorage'
LOCATION_MEDIA_ROOT2 = os.path.join(os.path.dirname(BASE_DIR), 'uploads')


#used on Local Development only
STORAGES = {
    "default": {
        "BACKEND": DEFAULT1,
    },
    "dbbackup": {
        "BACKEND": DEFAULT1,
        "OPTIONS": {
            'location': LOCATION_MEDIA_ROOT1,
            "default_acl": "private",  # Essential for security
        },
     "staticfiles": {
        "BACKEND": 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
    },
    }


