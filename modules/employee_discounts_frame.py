# modules/employee_discounts_frame.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from datetime import date
from modules.empleados_dao  import get_empleados
from modules.employee_discounts_dao import (
    get_all_discount_types, add_discount_type,
    get_employee_discounts, add_employee_discount,
    update_employee_discount, delete_employee_discount
)

class EmployeeDiscountsFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Descuentos Personales — Usuario: {self.usuario}",
                 font=(None,14,'bold')).pack(pady=10)

        # Selector de empleado
        emp_list = get_empleados()
        self.empleados = {f"{e['id']} - {e['nombre']} {e['apellido']}": e['id'] for e in emp_list}
        frm_emp = tk.Frame(self); frm_emp.pack(pady=5)
        tk.Label(frm_emp, text="Empleado:").pack(side='left')
        self.cmb_emp = ttk.Combobox(frm_emp, values=list(self.empleados.keys()), state='readonly')
        self.cmb_emp.pack(side='left', padx=5)
        self.cmb_emp.bind("<<ComboboxSelected>>", lambda e: self.load_discounts())

        # Botones CRUD
        btns = tk.Frame(self); btns.pack(pady=5)
        tk.Button(btns, text="Agregar (F1)", command=self.on_add).pack(side='left', padx=5)
        tk.Button(btns, text="Modificar (F2)", command=self.on_edit).pack(side='left', padx=5)
        tk.Button(btns, text="Eliminar (F3)", command=self.on_delete).pack(side='left', padx=5)
        tk.Button(btns, text="Volver   (F12)", command=self.volver).pack(side='left', padx=5)

        # Atajos
        self.master.bind('<F1>',  lambda e: self.on_add())
        self.master.bind('<F2>',  lambda e: self.on_edit())
        self.master.bind('<F3>',  lambda e: self.on_delete())
        self.master.bind('<F12>', lambda e: self.volver())

        # Treeview para descuentos
        cols = ('id','tipo','valor','%','activo','cuotas','restantes','sem_ini','anio_ini')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=8)
        headers = ['ID','Tipo','Valor','Pct','Activo','Nº Cuotas','Cuotas Rest.','Sem Inicio','Año Inicio']
        for c, h, w in zip(cols, headers, (30,120,60,30,50,50,70,70,70)):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor='center')
        self.tree.pack(padx=10, pady=10, fill='both', expand=True)

    def load_discounts(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        key = self.cmb_emp.get()
        if not key: return
        emp_id = self.empleados[key]
        for d in get_employee_discounts(emp_id):
            self.tree.insert('', 'end', values=(
                d['id'], d['tipo'], d['valor'], 'Sí' if d['es_porcentaje'] else 'No',
                'Sí' if d['activo'] else 'No',
                d['num_cuotas'], d['cuotas_restantes'],
                d['semana_inicio'], d['anio_inicio']
            ))

    def on_add(self):
        key = self.cmb_emp.get()
        if not key:
            return messagebox.showwarning("Atención", "Selecciona un empleado")
        emp_id = self.empleados[key]

        # Crear nuevo Tipo si hace falta
        tipos = get_all_discount_types()
        nombres = [t['nombre'] for t in tipos] + ['-- Nuevo tipo --']
        tipo = simpledialog.askstring("Tipo de descuento", f"Elige o escribe:\n{', '.join(nombres)}")
        if not tipo: return

        # Si es nuevo, lo añadimos
        match = [t for t in tipos if t['nombre']==tipo]
        if match:
            tipo_id = match[0]['id']
        else:
            tipo_id = add_discount_type(tipo)

        # Valor
        val = simpledialog.askfloat("Valor", "Introduce valor (número):")
        if val is None: return

        # Porcentaje?
        pct = messagebox.askyesno("Porcentaje", "¿Es porcentaje?")

        # Número de cuotas
        cuotas = simpledialog.askinteger("Cuotas", "Número de cuotas (0=único descuento):", minvalue=0)
        if cuotas is None: return

        # Semana y año de inicio
        today = date.today()
        iso_year, iso_week, _ = today.isocalendar()
        week = simpledialog.askinteger("Semana inicio", "Semana de inicio (ISO):", initialvalue=iso_week)
        year = simpledialog.askinteger("Año inicio", "Año de inicio:", initialvalue=iso_year)
        if week is None or year is None: return

        ed_id = add_employee_discount(tipo_id, emp_id, val, pct, cuotas, week, year)
        self.load_discounts()

    def on_edit(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Atención", "Selecciona un descuento")
        vals = self.tree.item(sel[0])['values']
        ed_id = vals[0]

        # Valor
        val = simpledialog.askfloat("Valor", "Nuevo valor:", initialvalue=vals[2])
        if val is None: return

        # Porcentaje?
        pct = messagebox.askyesno("Porcentaje", "¿Es porcentaje?")

        # Activo?
        act = messagebox.askyesno("Activo", "¿Mantener activo?")

        # Cuotas restantes
        rest = simpledialog.askinteger("Cuotas restantes", "Cuotas restantes:", initialvalue=vals[6], minvalue=0)
        if rest is None: return

        # Semana y año
        week = simpledialog.askinteger("Semana inicio", "Semana inicio:", initialvalue=vals[7])
        year = simpledialog.askinteger("Año inicio", "Año inicio:", initialvalue=vals[8])
        if week is None or year is None: return

        update_employee_discount(ed_id, val, pct, act, vals[5], rest, week, year)
        self.load_discounts()

    def on_delete(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Atención", "Selecciona un descuento")
        ed_id = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "Eliminar este descuento?"):
            delete_employee_discount(ed_id)
            self.load_discounts()

    def volver(self):
        self.master.show_menu(self.usuario, self.role)
