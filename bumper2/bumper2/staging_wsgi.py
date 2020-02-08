"""
WSGI config for bumper2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
from django.core.wsgi import get_wsgi_application
import os
import sys

path = '/srv/www/bumper2'
if path not in sys.path:
    sys.path.insert(0, '/srv/www/bumper2')

path = '/srv/www/bumper2/bumper2'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bumper2.staging_settings")

application = get_wsgi_application()
