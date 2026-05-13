'''
  here web server runs locally but superbase is used for database and file services
'''
from .base_settings import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['10.225.188.68', 'localhost', '127.0.0.1']
SITE_URL = os.environ.get("SITE_URL_LOCAL")

# superbase cloud PostgreSQL Connection
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        # Use SSL locally and on Render (required by Supabase)
        ssl_require=True
    )
}

# only in production for static and media files
STATICFILES_STORAGE = os.environ.get("STATICFILES_STORAGE_WHITENOISE")
SERVICE_ROLE_KEY=os.environ.get('SERVICE_ROLE_KEY')
SUPERBASE_URL=os.environ.get('SUPERBASE_URL')
AWS_STORAGE_BUCKET_NAME=os.environ.get('AWS_STORAGE_BUCKET_NAME')
