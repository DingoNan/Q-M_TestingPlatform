"""
WSGI config for black_bag project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from manage import ENV, ENVIRONMENT

os.environ.setdefault("DJANGO_SETTINGS_MODULE", ENVIRONMENT.get(ENV))

application = get_wsgi_application()
