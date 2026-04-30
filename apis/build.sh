#!/usr/bin/env bash
# exit on error
set -o errexit
cd apis
export DJANGO_SETTINGS_MODULE=apis.settings
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
