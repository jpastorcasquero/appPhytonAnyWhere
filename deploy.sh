#!/bin/bash

echo "🧹 Eliminando versiones anteriores..."
rm -rf ~/prevision_demanda
rm -rf ~/JPC

echo "📥 Clonando repositorio..."
git clone https://github.com/jpastorcasquero/appPhytonAnyWhere.git ~/prevision_demanda

if [ $? -ne 0 ]; then
  echo "❌ Error al clonar el repositorio."
  exit 1
fi

echo "🔧 Corrigiendo get_classifier.py para entorno Linux..."
CLASSIFIER_FILE=~/prevision_demanda/IA/get_classifier.py
sed -i 's|program_files = os.getenv('\''ProgramFiles'\'')|home_dir = os.path.expanduser("~")|' "$CLASSIFIER_FILE"
sed -i 's|log_path = os.path.join(program_files, '\''JPC'\'', '\''log.txt'\'')|log_path = os.path.join(home_dir, '\''JPC'\'', '\''log.txt'\'')|' "$CLASSIFIER_FILE"

echo "📦 Instalando dependencias desde requirements.txt..."
cd ~/prevision_demanda
pip install --user -r requirements.txt

if [ $? -ne 0 ]; then
  echo "❌ Error durante la instalación de requirements.txt"
  exit 1
fi

echo "🔐 Ejecutando main.py para generar credenciales cifradas..."
python3 main.py

if [ $? -ne 0 ]; then
  echo "❌ Error al ejecutar main.py"
  exit 1
fi

echo "✅ Despliegue completado correctamente en ~/prevision_demanda"
echo "🟢 Ahora puedes ir a tu panel web y pulsar 'Reload'"
