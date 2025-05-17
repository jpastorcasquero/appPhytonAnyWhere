from flask import Blueprint, jsonify
from IA.get_classifier import obtener_clasificador
import threading

get_classifier_bp = Blueprint('get_classifier', __name__)
classifier_lock = threading.Lock()

@get_classifier_bp.route('/get_classifier', methods=['GET'])
def get_classifier():
    if not classifier_lock.acquire(blocking=False):
        return jsonify({"success": False, "message": "Proceso en ejecución. Por favor espera."}), 429

    try:
        return obtener_clasificador()  # ya devuelve jsonify(...)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error durante la ejecución: {str(e)}"}), 500
    finally:
        classifier_lock.release()
