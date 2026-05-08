from .base_settings import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SITE_URL = os.environ.get('SITE_URL_PRODUCTION',"https://agc-alimosho-church-apis.onrender.com")

ALLOWED_HOSTS = []
# Get the Render URL (e.g., ://onrender.com)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '*')
# This adds the Render URL to allowed hosts
ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
# only in production Required for Django 4.0+ to prevent "CSRF verification failed"
CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']

# Only apply these in production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# superbase cloud PostgreSQL Connection
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        # Use SSL locally and on Render (required by Supabase)
        ssl_require=True
    )
}

# only in production

STATICFILES_STORAGE = os.environ.get("STATICFILES_STORAGE_WHITENOISE")

DBBACKUP_STORAGE_OPTIONS = {'location':'uploads', 'default_acl': 'private'}
DBBACKUP_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Supabase S3 upload storage Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
# Tell Django to use S3 for media files in production
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_S3_ADDRESSING_STYLE = "path"               # Required for Supabase
AWS_S3_SIGNATURE_VERSION = "s3v4"              # Supabase requires SigV4
AWS_QUERYSTRING_AUTH = True   