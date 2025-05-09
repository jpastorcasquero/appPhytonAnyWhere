# wsgi.py

import sys
import os

# Ruta absoluta a tu directorio de proyecto
project_home = '/home/jpastorcasquero/prevision_demanda'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from Http.flask_app import FlaskApp
application = FlaskApp().app
