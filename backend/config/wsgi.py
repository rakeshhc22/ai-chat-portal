"""
WSGI config for AI Chat Portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Activate Django settings for this interpreter.
application = get_wsgi_application()

# ==================== PRODUCTION SETUP (OPTIONAL) ====================
# Uncomment and customize for production environments
# from whitenoise.django import DjangoWhiteNoise
# application = DjangoWhiteNoise(application)
