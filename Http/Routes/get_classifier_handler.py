from flask import Blueprint, jsonify
from IA.get_classifier import obtener_clasificador


get_classifier_bp = Blueprint('get_classifier', __name__)
is_running = False


@get_classifier_bp.route('/get_classifier', methods=['GET'])
def get_classifier():
    global is_running
    if is_running:
        return jsonify({"success": False, "message": "Proceso ejecutandose actualmente"})

    is_running = True
    resultado = obtener_clasificador()
    is_running = False
    return resultado#jsonify({"success": resultado})