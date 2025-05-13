#!/bin/bash

echo "🔄  Eliminando proyecto anterior..."
rm -rf ~/prevision_demanda
rm -rf ~/JPC

echo "⬇️  Clonando el repositorio desde GitHub..."
git clone https://github.com/jpastorcasquero/appPhytonAnyWhere.git ~/prevision_demanda

if [ $? -ne 0 ]; then
  echo "❌ Error al clonar el repositorio."
  exit 1
fi

echo "📦 Instalando dependencias..."
cd ~/prevision_demanda
pip install --user -r requirements.txt

if [ $? -ne 0 ]; then
  echo "❌ Error al instalar requirements.txt"
  exit 1
fi

echo "🔐 Inicializando credenciales..."
python3 main.py

if [ $? -ne 0 ]; then
  echo "❌ Error al ejecutar main.py"
  exit 1
fi

echo "✅ Proyecto desplegado correctamente en ~/prevision_demanda"
echo "🔁 Recuerda ir a tu panel web y pulsar el botón Reload para reiniciar tu aplicación"
