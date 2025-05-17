from flask import Blueprint
from IA.get_prediction import obtener_prediccion
import threading

get_prediction_bp = Blueprint('get_prediction', __name__)
prediction_lock = threading.Lock()

@get_prediction_bp.route('/get_prediction', methods=['GET'])
def get_prediction():
    if not prediction_lock.acquire(blocking=False):
        return jsonify({"success": False, "message": "Proceso de predicción ya en ejecución."}), 429

    try:
        return obtener_prediccion()  # Esta ya devuelve jsonify(...) y código de estado
    except Exception as e:
        return jsonify({"success": False, "message": f"Error durante la predicción: {str(e)}"}), 500
    finally:
        prediction_lock.release()
