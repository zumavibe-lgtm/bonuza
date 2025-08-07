# modules/descuentos_menu_frame.py

import tkinter as tk
from modules.descuentos_frame         import DescuentosFrame
from modules.employee_discounts_frame import EmployeeDiscountsFrame
from modules.config_frame             import ConfigFrame

class DescuentosMenuFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="Descuentos", font=(None,14,'bold')).pack(pady=10)
        btns = tk.Frame(self); btns.pack(pady=20)

        tk.Button(btns, text="De Ley      (F1)", width=20,
                  command=self.ver_descuentos_ley).pack(pady=5)
        tk.Button(btns, text="Personales  (F2)", width=20,
                  command=self.ver_descuentos_personales).pack(pady=5)
        tk.Button(btns, text="Volver      (F12)", width=20,
                  command=self.volver).pack(pady=5)

        # Atajos
        self.master.bind('<F1>',  lambda e: self.ver_descuentos_ley())
        self.master.bind('<F2>',  lambda e: self.ver_descuentos_personales())
        self.master.bind('<F12>', lambda e: self.volver())

    def ver_descuentos_ley(self):
        for w in self.master.winfo_children():
            w.destroy()
        DescuentosFrame(self.master, usuario=self.usuario, role=self.role) \
            .pack(fill=tk.BOTH, expand=True)

    def ver_descuentos_personales(self):
        for w in self.master.winfo_children():
            w.destroy()
        EmployeeDiscountsFrame(self.master, usuario=self.usuario, role=self.role) \
            .pack(fill=tk.BOTH, expand=True)

    def volver(self):
        for w in self.master.winfo_children():
            w.destroy()
        ConfigFrame(self.master, usuario=self.usuario, role=self.role) \
            .pack(fill=tk.BOTH, expand=True)
