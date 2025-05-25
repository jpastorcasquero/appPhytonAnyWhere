from flask import Blueprint, request, jsonify
from Logger.logger import Logger
from datetime import datetime

users_api = Blueprint('users_api', __name__, url_prefix="/api/users")

def create_users_routes(app, logger: Logger, functions):
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

    # ✅ Endpoint de login
    @users_api.route("/login", methods=["POST"])
    def login_user():
        data = request.get_json(force=True)
        username = data.get("username") or data.get("email")
        password = data.get("password")
    
        user = functions.validate_login(username, password)
    
        if not user:
            return jsonify({"success": False, "message": "Credenciales incorrectas"}), 401
    
        try:
            functions.db_connection.ensure_connection()
    
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
            with functions.db_connection.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, connection_date FROM connections
                    WHERE user_id = %s AND disconnection_date IS NULL
                    ORDER BY connection_date DESC
                    LIMIT 1
                """, (user['id'],))
                existing = cursor.fetchone()
    
                if existing:
                    # Cerramos automáticamente si la sesión es anterior a 24 horas
                    cursor.execute("""
                        UPDATE connections
                        SET disconnection_date = %s
                        WHERE id = %s
                    """, (now, existing['id']))
                    functions.db_connection.connection.commit()
                    logger.log(f"⚠️ Sesión anterior cerrada automáticamente para user_id={user['id']} (connection_id={existing['id']})")
    
                # Insertamos nueva sesión
                cursor.execute("""
                    INSERT INTO connections (user_id, connection_date, disconnection_date)
                    VALUES (%s, %s, NULL)
                """, (user['id'], now))
                functions.db_connection.connection.commit()
                logger.log(f"✅ Nueva conexión insertada para user_id={user['id']}")
    
        except Exception as e:
            logger.log(f"❌ Error en login_user al insertar conexión: {repr(e)}")
    
        user.pop("password", None)
        return jsonify({"success": True, "user": user}), 200



    # ✅ Endpoint de logout
    @users_api.route("/logout", methods=["POST"])
    def logout_user():
        data = request.get_json(force=True)
        user_id = data.get("user_id")
    
        if not user_id:
            return jsonify({"error": "user_id es obligatorio"}), 400
    
        try:
            functions.db_connection.ensure_connection()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
            with functions.db_connection.connection.cursor() as cursor:
                affected = cursor.execute("""
                    UPDATE connections
                    SET disconnection_date = %s
                    WHERE user_id = %s AND disconnection_date IS NULL
                    ORDER BY connection_date DESC
                    LIMIT 1
                """, (now, user_id))
                functions.db_connection.connection.commit()
    
            if affected == 0:
                logger.log("⚠️ No se actualizó ninguna conexión (quizá ya estaba cerrada)")
                return jsonify({"warning": "No había ninguna sesión abierta"}), 200
    
            logger.log(f"✅ Logout registrado para user_id={user_id}")
            return jsonify({"message": "Usuario desconectado correctamente"}), 200
    
        except Exception as e:
            logger.log(f"❌ Error en logout_user: {repr(e)}")
            return jsonify({"error": str(e)}), 500

    app.register_blueprint(users_api)
