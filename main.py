#!/usr/bin/env python3
"""
BONUZA: Sistema de Asistencia y Nómina
MVP con Menú, Configuración, Descuentos, Nómina y logging
"""

import logging
import sys
import tkinter as tk
import os

# ——— Logging de errores ———
logging.basicConfig(
    filename='errores.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
def log_uncaught(exctype, value, tb):
    logging.error("Excepción no capturada", exc_info=(exctype, value, tb))
    sys.__excepthook__(exctype, value, tb)
sys.excepthook = log_uncaught
# ——————————————————————

from modules.database          import init_db, create_default_admin
from modules.empleados_dao     import create_table_empleados
from modules.config_dao        import create_table_config
from modules.descuentos_dao    import create_table_descuentos
from modules.nomina_dao        import create_table_nomina
from modules.login_frame       import LoginFrame
from modules.menu_frame        import MenuFrame
from modules.aguinaldo_dao     import create_table_aguinaldo# ...create_table_aguinaldo()
from modules.ptu_dao           import create_table_ptu_config# …create_table_ptu_config()

if __name__ == "__main__":
    # Inicializa todas las tablas
    init_db()
    create_default_admin()
    create_table_empleados()
    create_table_config()
    create_table_descuentos()   # ← Crea la tabla descuentos
    create_table_nomina()

    root = tk.Tk()
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.isfile(icon_path):
        root.iconphoto(True, tk.PhotoImage(file=icon_path))

    root.title("BONUZA - Login")

    def show_menu(user, role):
        root.title(f"BONUZA - Menú (Usuario: {user})")
        for w in root.winfo_children():
            w.destroy()
        root.show_menu = show_menu
        MenuFrame(root, usuario=user, role=role).pack(fill=tk.BOTH, expand=True)

    login = LoginFrame(root, on_success=show_menu)
    login.pack(padx=50, pady=50)

    root.mainloop()
