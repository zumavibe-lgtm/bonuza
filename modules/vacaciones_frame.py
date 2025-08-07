# modules/vacaciones_frame.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from modules.empleados_dao import get_empleados
from modules.vacaciones_dao import (
    create_table_vacaciones, add_vacaciones,
    get_vacaciones, delete_vacaciones
)

class VacacionesFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        create_table_vacaciones()
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Vacaciones — Usuario: {self.usuario}",
                 font=(None,14,'bold')).pack(pady=10)

        # Selector de empleado
        emp = get_empleados()
        self.emp_map = {f"{e['id']} - {e['nombre']} {e['apellido']}": e['id'] for e in emp}
        frm1 = tk.Frame(self); frm1.pack(pady=5)
        tk.Label(frm1, text="Empleado:").pack(side='left')
        self.cmb_emp = ttk.Combobox(frm1, values=list(self.emp_map.keys()), state='readonly')
        self.cmb_emp.pack(side='left', padx=5)
        self.cmb_emp.bind("<<ComboboxSelected>>", lambda e: self.load_vacaciones())

        # Calendarios
        frm2 = tk.Frame(self); frm2.pack(pady=5)
        tk.Label(frm2, text="Desde:").grid(row=0, column=0, sticky='e')
        self.start = DateEntry(frm2); self.start.grid(row=0, column=1, padx=5)
        tk.Label(frm2, text="Hasta:").grid(row=0, column=2, sticky='e')
        self.end   = DateEntry(frm2); self.end.grid(row=0, column=3, padx=5)

        # Botones
        btns = tk.Frame(self); btns.pack(pady=10)
        tk.Button(btns, text="Agregar (F1)", command=self.on_add).pack(side='left', padx=5)
        tk.Button(btns, text="Eliminar (F3)", command=self.on_delete).pack(side='left', padx=5)
        tk.Button(btns, text="Volver   (F12)", command=self.volver).pack(side='left', padx=5)

        self.master.bind('<F1>',  lambda e: self.on_add())
        self.master.bind('<F3>',  lambda e: self.on_delete())
        self.master.bind('<F12>', lambda e: self.volver())

        # Tabla de vacaciones
        cols = ('id','inicio','fin','dias')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=8)
        for c,h,w in zip(cols,
                        ('ID','Inicio','Fin','Días'),
                        (50,100,100,60)):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor='center')
        self.tree.pack(padx=10, pady=10, fill='both', expand=True)

    def load_vacaciones(self):
        # Carga los registros del empleado seleccionado
        for i in self.tree.get_children():
            self.tree.delete(i)
        key = self.cmb_emp.get()
        if not key: return
        emp_id = self.emp_map[key]
        for v in get_vacaciones(emp_id):
            self.tree.insert('', 'end', values=(
                v['id'], v['fecha_inicio'], v['fecha_fin'], v['dias_totales']
            ))

    def on_add(self):
        key = self.cmb_emp.get()
        if not key:
            return messagebox.showwarning("Atención", "Selecciona un empleado")
        emp_id = self.emp_map[key]
        ini = self.start.get_date().isoformat()
        fin = self.end.get_date().isoformat()
        try:
            add_vacaciones(emp_id, ini, fin)
            self.load_vacaciones()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def on_delete(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Atención", "Selecciona un periodo")
        vac_id = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "Eliminar este periodo?"):
            delete_vacaciones(vac_id)
            self.load_vacaciones()

    def volver(self):
        self.master.show_menu(self.usuario, self.role)
