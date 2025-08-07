# modules/config_frame.py

import tkinter as tk
from tkinter import messagebox
from modules.config_dao import get_config, set_config
from modules.descuentos_frame import DescuentosFrame

class ConfigFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Configuración (Usuario: {self.usuario})",
                 font=(None,14,'bold')).pack(pady=10)

        cfg = get_config()
        form = tk.Frame(self); form.pack(padx=10, pady=5)

        tk.Label(form, text="Hora Entrada (HH:MM):").grid(row=0, column=0, sticky='e')
        self.e_entrada = tk.Entry(form); self.e_entrada.grid(row=0, column=1, padx=5)
        self.e_entrada.insert(0, cfg['hora_entrada'])

        tk.Label(form, text="Hora Salida (HH:MM):").grid(row=1, column=0, sticky='e')
        self.e_salida = tk.Entry(form); self.e_salida.grid(row=1, column=1, padx=5)
        self.e_salida.insert(0, cfg['hora_salida'])

        tk.Label(form, text="Tolerancia (min):").grid(row=2, column=0, sticky='e')
        self.e_tol = tk.Entry(form); self.e_tol.grid(row=2, column=1, padx=5)
        self.e_tol.insert(0, cfg['tolerancia_minutos'])

        # Botones de Configuración + Descuentos
        btns = tk.Frame(self); btns.pack(pady=10)
        tk.Button(btns, text="Guardar (F1)",  command=self.guardar).pack(side='left', padx=5)
        tk.Button(btns, text="Descuentos (F4)", command=self.ver_descuentos).pack(side='left', padx=5)
        tk.Button(btns, text="Volver    (F12)", command=self.volver).pack(side='left', padx=5)

        # Atajos de teclado
        self.master.bind('<F1>',  lambda e: self.guardar())
        self.master.bind('<F4>',  lambda e: self.ver_descuentos())
        self.master.bind('<F12>', lambda e: self.volver())

    def guardar(self):
        h_ent = self.e_entrada.get().strip()
        h_sal = self.e_salida.get().strip()
        tol   = self.e_tol.get().strip()
        try:
            # Validar formato HH:MM
            for val in (h_ent, h_sal):
                hh, mm = val.split(':')
                if not (hh.isdigit() and mm.isdigit()):
                    raise ValueError(f"Formato inválido: {val}")
                hh, mm = int(hh), int(mm)
                if not (0 <= hh < 24 and 0 <= mm < 60):
                    raise ValueError(f"Hora fuera de rango: {val}")
            # Validar tolerancia
            if not tol.isdigit():
                raise ValueError(f"Tolerancia inválida: {tol}")

            set_config('hora_entrada', h_ent)
            set_config('hora_salida',  h_sal)
            set_config('tolerancia_minutos', tol)
            messagebox.showinfo("OK", "Configuración guardada")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def ver_descuentos(self):
        # Navega al menú intermedio de descuentos
        for w in self.master.winfo_children():
            w.destroy()
        from modules.descuentos_menu_frame import DescuentosMenuFrame
        DescuentosMenuFrame(self.master, usuario=self.usuario, role=self.role) \
            .pack(fill=tk.BOTH, expand=True)

    def volver(self):
        # Regresa al menú principal
        self.master.show_menu(self.usuario, self.role)
