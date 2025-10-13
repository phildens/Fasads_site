"""
WSGI config for FasadSiteDjango project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import platform
import sys


# sys.path.insert(0, '/home/c/ct45437/fasad_modern/public_html')

# sys.path.insert(0, '/home/c/ct45437/fasad_modern/public_html/FasadSiteDjango')
# python_version = ".".join(platform.python_version_tuple()[:2])
# sys.path.insert(0, '/home/c/ct45437/fasad_modern/venv/lib/python{0}/site-packages'.format(python_version))
activate_this = os.path.expanduser('~/fasad_modern/venv/bin/activate_this.py')
exec(open(activate_this).read(), {'__file__': activate_this})
 
sys.path.insert(1, os.path.expanduser('~/fasad_modern/public_html/'))
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FasadSiteDjango.settings')

application = get_wsgi_application()
