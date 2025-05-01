from flask import Blueprint, jsonify
from IA.get_prediction import obtener_prediccion


get_prediction_bp = Blueprint('get_prediction', __name__)
is_running = False


@get_prediction_bp.route('/get_prediction', methods=['GET'])
def get_prediction():
    global is_running
    if is_running:
        return jsonify({"success": False, "message": "Proceso ejecutandose actualmente"})

    is_running = True
    resultado = obtener_prediccion()
    is_running = False
    return resultado#jsonify({"success": resultado})