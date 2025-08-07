# modules/descuentos_frame.py

import tkinter as tk
from tkinter import messagebox
from modules.descuentos_dao import get_descuentos, set_descuento, DISCOUNT_KEYS

class DescuentosFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Configuración de Descuentos (%)  — Usuario: {self.usuario}",
                 font=(None,14,'bold')).pack(pady=10)

        cfg = get_descuentos()
        form = tk.Frame(self)
        form.pack(padx=10, pady=5)

        # Entrada para cada descuento
        self.entries = {}
        for i, clave in enumerate(DISCOUNT_KEYS):
            tk.Label(form, text=f"{clave} (%):").grid(row=i, column=0, sticky='e')
            e = tk.Entry(form)
            e.grid(row=i, column=1, padx=5)
            e.insert(0, str(cfg.get(clave, 0.0)))
            self.entries[clave] = e

        # Botones
        btns = tk.Frame(self)
        btns.pack(pady=10)
        tk.Button(btns, text="Guardar (F1)", command=self.guardar).pack(side='left', padx=5)
        tk.Button(btns, text="Volver  (F12)", command=self.volver).pack(side='left', padx=5)

        # Atajos
        self.master.bind('<F1>',  lambda e: self.guardar())
        self.master.bind('<F12>', lambda e: self.volver())

    def guardar(self):
        try:
            for clave, entry in self.entries.items():
                val = float(entry.get().replace(',','.'))
                set_descuento(clave, val)
            messagebox.showinfo("OK", "Descuentos guardados")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def volver(self):
        # Vuelve al menú
        self.master.show_menu(self.usuario, self.role)
