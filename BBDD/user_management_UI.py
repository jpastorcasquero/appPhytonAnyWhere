import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from BBDD.validator_UI import Validator
import smtplib
from email.mime.text import MIMEText

class UserManagementUI:
    def __init__(self, root, functions):
        self.root = root
        self.functions = functions

    def show_user_management(self):
        if hasattr(self, 'user_management_window') and self.user_management_window.winfo_exists():
            self.user_management_window.lift()
            return

        self.user_management_window = tk.Toplevel(self.root)
        self.user_management_window.title("Gestión de usuarios")
        self.user_management_window.iconbitmap("Images/Logo.ico")
        self.user_management_window.geometry("800x600")

        columns = ("id", "Nombre", "Nombre de usuario", "Correo", "Contraseña", "Rol", "Imagen")
        tree = ttk.Treeview(self.user_management_window, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col, anchor='center')
            tree.column(col, anchor='center', width=100)
        tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_user_management(tree)

        tree.bind("<Double-1>", lambda event: self.on_user_double_click(event, tree))
        tree.bind("<Button-3>", lambda event: self.show_context_menu(event, tree))

        refresh_button = ttk.Button(self.user_management_window, text="Actualizar Tabla", command=lambda: self.refresh_user_management(tree))
        refresh_button.pack(pady=10)

    def refresh_user_management(self, tree):
        for item in tree.get_children():
            try:
                tree.delete(item)
            except Exception as e:
                print("Formulario cerrado manualmente")
        users = self.functions.fetch_users_from_db()
        for user in users:
            tree.insert("", tk.END, values=user)

    def on_user_double_click(self, event, tree):
        try:
            item = tree.selection()[0]
            user_data = tree.item(item, "values")
            self.show_user_form(user_data, tree)
        except IndexError:
            messagebox.showerror("Error", "No se ha seleccionado ningún usuario.")

    def show_context_menu(self, event, tree):
        try:
            item = tree.identify_row(event.y)
            tree.selection_set(item)
            user_data = tree.item(item, "values")
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Eliminar Usuario", command=lambda: self.delete_user(user_data, tree))
            context_menu.add_command(label="Restablecer Contraseña", command=lambda: self.send_reset_email(user_data))
            context_menu.post(event.x_root, event.y_root)
        except IndexError:
            pass

    def delete_user(self, user_data, tree):
        confirm = messagebox.askyesno("Confirmar Eliminación",
                                      f"¿Estás seguro de que deseas eliminar al usuario {user_data[1]}?")
        if confirm:
            success, message = self.functions.delete_user(user_data[0])
            if success:
                messagebox.showinfo("Éxito", message)
                self.refresh_user_management(tree)
            else:
                messagebox.showerror("Error", message)

    def show_user_form(self, user_data=None, tree=None):
        if hasattr(self, 'user_form_window') and self.user_form_window.winfo_exists():
            self.user_form_window.lift()
            return

        self.user_form_window = tk.Toplevel(self.root)
        self.user_form_window.title("Editar usuario" if user_data else "Crear usuario")
        self.user_form_window.iconbitmap("Images/Logo.ico")
        self.user_form_window.geometry("600x750")

        labels = ["Nombre", "Nombre de usuario", "Correo", "Contraseña", "Rol", "Imagen", "Código de País 1", "Teléfono 1", "Código de País 2", "Teléfono 2", "Ciudad", "País", "Código postal", "Dirección"]
        entries = {}
        error_labels = {}
        error_points = {}

        country_codes = self.functions.fetch_country_codes()

        for i, label in enumerate(labels):
            tk.Label(self.user_form_window, text=label).grid(row=i, column=0, padx=10, pady=5)
            if "Código de País" in label:
                entry = ttk.Combobox(self.user_form_window, values=[f"{code} ({country})" for code, country in country_codes.items()])
            elif label == "Rol":
                entry = ttk.Combobox(self.user_form_window, values=["admin", "user"])
            elif label == "Imagen":
                entry = ttk.Combobox(self.user_form_window, values=["avatar1.png", "avatar2.png", "avatar3.png", "avatar4.png"])
                entry.bind("<<ComboboxSelected>>", self.create_update_avatar_image_callback(entry))
            else:
                entry = tk.Entry(self.user_form_window, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
            entries[label] = entry

            error_point = tk.Label(self.user_form_window, text="●", fg="green", font=("Arial", 16))
            error_point.grid(row=i, column=2, padx=10, pady=5, sticky='w')
            error_points[label] = error_point

            error_label = tk.Label(self.user_form_window, text="", fg="red")
            error_label.grid(row=i, column=3, padx=10, pady=5, sticky='w')
            error_labels[label] = error_label

        self.avatar_label = tk.Label(self.user_form_window)
        self.avatar_label.grid(row=0, column=4, rowspan=6, padx=10, pady=5)

        if user_data:
            entries["Nombre"].insert(0, user_data[1])
            entries["Nombre de usuario"].insert(0, user_data[2])
            entries["Correo"].insert(0, user_data[3])
            entries["Contraseña"].insert(0, user_data[4])
            entries["Rol"].set(user_data[5])
            entries["Imagen"].set(user_data[6])
            self.update_avatar_image(user_data[6])

            user_id = user_data[0]
            phone_data = self.functions.fetch_phone_data(user_id)
            address_data = self.functions.fetch_address_data(user_id)

            if phone_data:
                if len(phone_data) > 0:
                    entries["Código de País 1"].set(f"{phone_data[0][0]} ({country_codes.get(phone_data[0][0], 'Desconocido')})")
                    entries["Teléfono 1"].insert(0, phone_data[0][1])

                if len(phone_data) > 1:
                    entries["Código de País 2"].set(f"{phone_data[1][0]} ({country_codes.get(phone_data[1][0], 'Desconocido')})")
                    entries["Teléfono 2"].insert(0, phone_data[1][1])
            if address_data:
                entries["Ciudad"].insert(0, address_data[0])
                entries["País"].insert(0, address_data[1])
                entries["Código postal"].insert(0, address_data[2])
                entries["Dirección"].insert(0, address_data[3])

        original_values = {label: entry.get() for label, entry in entries.items()}

        self.error_message_label = tk.Label(self.user_form_window, text="", fg="red")
        self.error_message_label.grid(row=len(labels) + 1, column=0, columnspan=4, padx=10, pady=5, sticky='w')

        def save_and_close():
            # Extraer solo los códigos de país para guardar en la base de datos
            if entries["Código de País 1"].get():
                entries["Código de País 1"].set(entries["Código de País 1"].get().split()[0])
            if entries["Código de País 2"].get():
                entries["Código de País 2"].set(entries["Código de País 2"].get().split()[0])

            # Guarda los datos del usuario y cierra el formulario
            if user_data:
                success, message = self.functions.save_user_data(user_id, entries)
            else:
                success, message = self.functions.create_user(entries)

            if success:
                messagebox.showinfo("Éxito", message)
                if tree:
                    self.refresh_user_management(tree)
                self.user_form_window.destroy()
            else:
                messagebox.showerror("Error", message)

        def on_closing():
            current_values = {label: entry.get() for label, entry in entries.items()}
            if current_values != original_values:
                if messagebox.askyesno("Salir", "¿Deseas guardar los cambios antes de salir?"):
                    save_and_close()
                else:
                    self.user_form_window.destroy()
                    if tree:
                        tree.focus_set()
            else:
                self.user_form_window.destroy()
                if tree:
                    tree.focus_set()

        self.user_form_window.protocol("WM_DELETE_WINDOW", on_closing)

        button_frame = ttk.Frame(self.user_form_window)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)

        self.save_button = ttk.Button(button_frame, text="Guardar", command=save_and_close)
        self.save_button.pack(side=tk.LEFT, padx=10)

        exit_button = ttk.Button(button_frame, text="Salir", command=on_closing)
        exit_button.pack(side=tk.LEFT, padx=10)

        # Realizar la validación inicial después de cargar los datos
        self.validate_all_fields(entries, error_labels, error_points)

        # Vincular eventos de validación en tiempo real
        for label, entry in entries.items():
            entry.bind("<KeyRelease>",
                       lambda event, lbl=label: self.validate_field(lbl, entries, error_labels, error_points))

    def validate_field(self, label, entries, error_labels, error_points):
        value = entries[label].get()
        error_message = ""

        if label == "Contraseña":
            error_message = Validator.validate_password(value)
        elif label == "Correo":
            error_message = Validator.validate_email(value)
        elif "Teléfono" in label:
            error_message = Validator.validate_phone(value)

        if not value and label not in ["Código de País 2", "Teléfono 2", "Imagen"]:
            error_message = f"El campo '{label}' es obligatorio."

        error_labels[label].config(text=error_message)
        error_points[label].config(fg="red" if error_message else "green")
        self.validate_all_fields(entries, error_labels, error_points)

    def validate_all_fields(self, entries, error_labels, error_points):
        all_valid = True
        error_messages = []
        for label, entry in entries.items():
            value = entry.get()
            error_message = error_labels[label].cget("text")
            if not value and label not in ["Código de País 2", "Teléfono 2", "Imagen"]:
                all_valid = False
                error_messages.append(f"El campo '{label}' es obligatorio.")
            if error_message:
                all_valid = False
                error_messages.append(error_message)

        self.error_message_label.config(text="\n".join(error_messages))

        if all_valid:
            self.save_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.DISABLED)

    def create_update_avatar_image_callback(self, entry):
        return lambda event: self.update_avatar_image(entry.get())

    def update_avatar_image(self, avatar_name):
        image_path = os.path.join("Images", "AvataresImage", avatar_name)
        if os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.avatar_label.config(image=photo)
            self.avatar_label.image = photo
        else:
            messagebox.showerror("Error", f"No se encontró la imagen: {avatar_name}")


    def send_reset_email(self, user_data):
        user_email = user_data[3]  # Asumiendo que el correo está en la tercera posición
        reset_link = f"http://localhost:5001/reset_password/{user_data[0]}"  # Enlace de restablecimiento

        msg = MIMEText(f"Para restablecer tu contraseña, haz clic en el siguiente enlace: {reset_link}")
        msg['Subject'] = 'Restablecimiento de Contraseña'
        msg['From'] = 'pass.recovery.jpcinformatica@gmail.com'
        msg['To'] = user_email

        try:
            with (
                smtplib.SMTP('smtp.gmail.com', 587) as server):
                server.starttls()
                server.login('pass.recovery.jpcinformatica@gmail.com', 'yxko jelw mgoo vumt')
                             #'P@ssRecovery1234')  # Usa la contraseña de aplicación si es necesario
                server.sendmail('pass.recovery.jpcinformatica@gmail.com', user_email, msg.as_string())
            messagebox.showinfo("Correo Enviado", f"Se ha enviado un correo de restablecimiento a {user_email}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el correo: {e}")
