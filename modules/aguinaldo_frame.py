# modules/aguinaldo_frame.py

import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import date
from modules.empleados_dao import get_empleados
from modules.aguinaldo_dao import (
    create_table_aguinaldo, get_aguinaldo_days,
    set_aguinaldo_days, calculate_aguinaldo_for_employee
)

class AguinaldoFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        create_table_aguinaldo()
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Aguinaldo — Usuario: {self.usuario}",
                 font=(None,14,'bold')).pack(pady=10)

        # Configuración días de aguinaldo
        frm_cfg = tk.Frame(self); frm_cfg.pack(pady=5)
        tk.Label(frm_cfg, text="Días de aguinaldo:").pack(side='left')
        self.e_dias = tk.Entry(frm_cfg, width=5)
        self.e_dias.pack(side='left', padx=5)
        self.e_dias.insert(0, str(get_aguinaldo_days()))
        tk.Button(frm_cfg, text="Guardar (F1)", command=self.on_save_cfg).pack(side='left', padx=10)

        # Selección de empleado y fecha
        frm_sel = tk.Frame(self); frm_sel.pack(pady=10)
        tk.Label(frm_sel, text="Empleado:").grid(row=0, column=0, sticky='e')
        emp = get_empleados()
        self.emp_map = {f"{e['id']} - {e['nombre']} {e['apellido']}": e['id'] for e in emp}
        self.cmb_emp = tk.ttk.Combobox(frm_sel, values=list(self.emp_map.keys()), state='readonly')
        self.cmb_emp.grid(row=0, column=1, padx=5)
        tk.Label(frm_sel, text="Hasta fecha:").grid(row=1, column=0, sticky='e')
        self.dt_hasta = DateEntry(frm_sel)
        self.dt_hasta.grid(row=1, column=1, padx=5)

        # Botones calcular y volver
        btns = tk.Frame(self); btns.pack(pady=10)
        tk.Button(btns, text="Calcular (F2)", command=self.on_calcular).pack(side='left', padx=5)
        tk.Button(btns, text="Volver   (F12)", command=self.volver).pack(side='left', padx=5)

        self.master.bind('<F1>', lambda e: self.on_save_cfg())
        self.master.bind('<F2>', lambda e: self.on_calcular())
        self.master.bind('<F12>', lambda e: self.volver())

    def on_save_cfg(self):
        try:
            dias = float(self.e_dias.get())
            set_aguinaldo_days(dias)
            messagebox.showinfo("OK", "Configuración guardada")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def on_calcular(self):
        key = self.cmb_emp.get()
        if not key:
            return messagebox.showwarning("Atención", "Selecciona un empleado")
        emp_id = self.emp_map[key]
        hasta = self.dt_hasta.get_date().isoformat()
        try:
            data = calculate_aguinaldo_for_employee(emp_id, hasta)
            # Mostrar en un messagebox
            msg = (
                f"Días trabajados: {data['dias_trabajados']}\n"
                f"Días config: {data['dias_config']}\n"
                f"Sueldo diario: {data['sueldo_diario']}\n"
                f"Monto aguinaldo: {data['monto_aguinaldo']}"
            )
            messagebox.showinfo("Resultado Aguinaldo", msg)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def volver(self):
        self.master.show_menu(self.usuario, self.role)
