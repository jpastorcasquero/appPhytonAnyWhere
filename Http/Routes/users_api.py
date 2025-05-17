from flask import Blueprint, request, jsonify
from BBDD.database_connection_handler import DatabaseConnectionHandler
from Logger.logger import Logger

users_api = Blueprint('users_api', __name__, url_prefix="/api/users")

# Inicializa logger y conexión
logger = Logger("/home/jpastorcasquero/JPC/log.txt")
handler = DatabaseConnectionHandler(logger)
functions = handler.functions

@users_api.route("/", methods=["GET"])
def get_users():
    users = functions.fetch_users_from_db()
    logger.log(f"📥 Petición a /api/users/ -> {users}")
    return jsonify(users), 200

@users_api.route("/", methods=["POST"])
def create_user():
    data = request.json
    success, message = functions.create_user_from_json(data)
    return jsonify({"success": success, "message": message}), (200 if success else 400)

@users_api.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    success, message = functions.save_user_data_from_json(user_id, data)
    return jsonify({"success": success, "message": message}), (200 if success else 400)

@users_api.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    success, message = functions.delete_user(user_id)
    return jsonify({"success": success, "message": message}), (200 if success else 400)
