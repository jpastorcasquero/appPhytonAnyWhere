from flask import Blueprint, jsonify
import os

avatar_bp = Blueprint('avatar_bp', __name__, url_prefix="/api")

@avatar_bp.route('/avatars', methods=['GET'])
def get_avatars():
    avatar_dir = "/home/jpastorcasquero/prevision_demanda/static/AvataresImage"
    try:
        files = os.listdir(avatar_dir)
        images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        return jsonify(images), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
