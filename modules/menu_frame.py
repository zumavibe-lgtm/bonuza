# modules/menu_frame.py

import tkinter as tk
from modules.checador_frame import ChecadorFrame
from modules.empleados_frame import EmpleadosFrame
from modules.config_menu_frame import ConfigMenuFrame  # ← updated import

class MenuFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Menú (Usuario: {self.usuario})",
                 font=(None,14,'bold')).pack(pady=10)
        btns = tk.Frame(self)
        btns.pack(pady=20)

        tk.Button(btns, text="Asistencia    (F1)",
                  width=20, command=self.ver_asistencia).pack(pady=5)

        if self.role == 'admin':
            tk.Button(btns, text="Empleados     (F2)",
                      width=20, command=self.ver_empleados).pack(pady=5)
            # now calls ConfigMenuFrame instead of ConfigFrame
            tk.Button(btns, text="Configuración (F3)",
                      width=20, command=self.ver_config).pack(pady=5)
            tk.Button(btns, text="Nómina        (F4)",
                      width=20, command=self.ver_nomina).pack(pady=5)

        tk.Button(btns, text="Cerrar sesión (F12)",
                  width=20, command=self.volver_login).pack(pady=5)
        tk.Button(btns, text="Vacaciones     (F5)",
          width=20, command=self.ver_vacaciones).pack(pady=5)
        self.master.bind('<F5>', lambda e: self.ver_vacaciones() if self.role=='admin' else None)
        
        tk.Button(btns, text="Aguinaldo     (F6)",
        width=20, command=self.ver_aguinaldo).pack(pady=5)
        self.master.bind('<F6>', lambda e: self.ver_aguinaldo() if self.role=='admin' else None)
        
        tk.Button(btns, text="PTU            (F7)",
                  width=20, command=self.ver_ptu).pack(pady=5)
        self.master.bind('<F7>', lambda e: self.ver_ptu() if self.role=='admin' else None)


        self.master.bind('<F1>',  lambda e: self.ver_asistencia())
        self.master.bind('<F2>',  lambda e: self.ver_empleados() if self.role=='admin' else None)
        self.master.bind('<F3>',  lambda e: self.ver_config()    if self.role=='admin' else None)
        self.master.bind('<F4>',  lambda e: self.ver_nomina()    if self.role=='admin' else None)
        self.master.bind('<F12>', lambda e: self.volver_login())

    def ver_asistencia(self):
        for w in self.master.winfo_children():
            w.destroy()
        ChecadorFrame(self.master, usuario=self.usuario, role=self.role).pack(fill=tk.BOTH, expand=True)

    def ver_empleados(self):
        for w in self.master.winfo_children():
            w.destroy()
        EmpleadosFrame(self.master, usuario=self.usuario, role=self.role).pack(fill=tk.BOTH, expand=True)

    def ver_config(self):
        for w in self.master.winfo_children():
            w.destroy()
        ConfigMenuFrame(self.master, usuario=self.usuario, role=self.role).pack(fill=tk.BOTH, expand=True)

    def ver_nomina(self):
        from modules.payroll_frame import PayrollFrame
        for w in self.master.winfo_children():
            w.destroy()
        PayrollFrame(self.master, usuario=self.usuario, role=self.role).pack(fill=tk.BOTH, expand=True)

    def volver_login(self):
        from modules.login_frame import LoginFrame
        for w in self.master.winfo_children():
            w.destroy()
        self.master.title("BONUZA - Login")
        LoginFrame(self.master, on_success=self.master.show_menu).pack(padx=50, pady=50)

    def ver_vacaciones(self):
        for w in self.master.winfo_children(): w.destroy()
        from modules.vacaciones_frame import VacacionesFrame
        VacacionesFrame(self.master, usuario=self.usuario, role=self.role) \
        .pack(fill=tk.BOTH, expand=True)

    def ver_aguinaldo(self):
        for w in self.master.winfo_children():w.destroy()
        from modules.aguinaldo_frame import AguinaldoFrame
        AguinaldoFrame(self.master, usuario=self.usuario, role=self.role).pack(fill=tk.BOTH, expand=True)

    def ver_ptu(self):
        for w in self.master.winfo_children(): w.destroy()
        from modules.ptu_frame import PtuFrame
        PtuFrame(self.master, usuario=self.usuario, role=self.role).pack(fill=tk.BOTH, expand=True)
