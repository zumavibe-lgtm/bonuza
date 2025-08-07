# modules/config_menu_frame.py

import tkinter as tk
from modules.config_frame           import ConfigFrame
from modules.descuentos_menu_frame  import DescuentosMenuFrame

class ConfigMenuFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="Configuración", font=(None,14,'bold')).pack(pady=10)
        btns = tk.Frame(self)
        btns.pack(pady=20)

        tk.Button(btns, text="Horarios y Tolerancia (F1)", width=25,
                  command=self.ver_horarios).pack(pady=5)
        tk.Button(btns, text="Descuentos          (F2)", width=25,
                  command=self.ver_descuentos).pack(pady=5)
        tk.Button(btns, text="Volver              (F12)", width=25,
                  command=self.volver).pack(pady=5)

        # Atajos de teclado
        self.master.bind('<F1>',  lambda e: self.ver_horarios())
        self.master.bind('<F2>',  lambda e: self.ver_descuentos())
        self.master.bind('<F12>', lambda e: self.volver())

    def ver_horarios(self):
        for w in self.master.winfo_children():
            w.destroy()
        ConfigFrame(self.master, usuario=self.usuario, role=self.role) \
            .pack(fill=tk.BOTH, expand=True)

    def ver_descuentos(self):
        for w in self.master.winfo_children():
            w.destroy()
        DescuentosMenuFrame(self.master, usuario=self.usuario, role=self.role) \
            .pack(fill=tk.BOTH, expand=True)

    def volver(self):
        from modules.menu_frame import MenuFrame
        for w in self.master.winfo_children():
            w.destroy()
        MenuFrame(self.master, usuario=self.usuario, role=self.role) \
            .pack(fill=tk.BOTH, expand=True)
