import sys
import os

# Ruta absoluta al directorio del proyecto
project_home = '/home/jpastorcasquero/prevision_demanda'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Establecer variable de entorno para distinguir entorno PythonAnywhere
os.environ['PA_ENV'] = 'pythonanywhere'

# Importar y lanzar la aplicación Flask
from Http.flask_app import FlaskApp
flask_app_instance = FlaskApp()
application = flask_app_instance.app
