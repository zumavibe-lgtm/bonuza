# main.py
#!/usr/bin/env python3
"""
BONUZA: Sistema de Asistencia y Nómina
Versión MVP Básico
"""
import tkinter as tk
from modules.database import init_db, create_default_admin
from modules.login_frame import LoginFrame


from modules.checador_frame import ChecadorFrame

def show_chekador(user, role):
    # Limpia y muestra el ChecadorFrame
    root.title(f"BONUZA - Usuario: {user} ({role})")
    for widget in root.winfo_children():
        widget.destroy()
    ChecadorFrame(root, usuario=user).pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    # Inicializa BD y admin por defecto
    init_db()
    create_default_admin()

    root = tk.Tk()
    root.title("BONUZA - Login")
    login = LoginFrame(root, on_success=show_chekador)
    login.pack(padx=50, pady=50)
    root.mainloop()

# Nota: instala bcrypt con: pip install bcrypt
