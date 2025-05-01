import tkinter as tk
from threading import Thread
from Http.flask_app import FlaskApp
from BBDD.database_UI import DatabaseUI

if __name__ == "__main__":
    # Crear la ventana principal de la aplicación
    root = tk.Tk()
    app_instance = DatabaseUI(root)

    # Iniciar el servidor Flask en un hilo separado y pasar app_instance a FlaskApp
    def start_flask_app():
        flask_app = FlaskApp(app_instance)
        flask_app.run()

    flask_thread = Thread(target=start_flask_app)
    flask_thread.start()

    # Definir la función para cerrar la aplicación correctamente
    def on_closing():
        app_instance.exit_program()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()