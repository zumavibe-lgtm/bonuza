# modules/payroll_frame.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date, timedelta
import os
from modules.nomina_dao import calcular_nomina

class PayrollFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        self._setup_default_period()
        self.build_ui()

    def _setup_default_period(self):
        """Calcula la semana ISO actual y establece lunes/viernes."""
        today = date.today()
        iso_year, iso_week, _ = today.isocalendar()
        self.lunes   = date.fromisocalendar(iso_year, iso_week, 1)
        self.viernes = self.lunes + timedelta(days=4)
        self.iso_year = iso_year
        self.iso_week = iso_week

    def build_ui(self):
        # Título con la semana ISO
        tk.Label(self, text=f"Nómina Semana {self.iso_week}/{self.iso_year}",
                 font=(None,14,'bold')).pack(pady=10)

        # Selección de fechas
        frm = tk.Frame(self); frm.pack(pady=5)
        tk.Label(frm, text="Desde:").grid(row=0, column=0, sticky='e')
        self.start = DateEntry(frm); self.start.grid(row=0, column=1, padx=5)
        self.start.set_date(self.lunes)
        tk.Label(frm, text="Hasta:").grid(row=0, column=2, sticky='e')
        self.end = DateEntry(frm); self.end.grid(row=0, column=3, padx=5)
        self.end.set_date(self.viernes)

        # Botones de acción
        btns = tk.Frame(self); btns.pack(pady=10)
        tk.Button(btns, text="Calcular (F1)", command=self.on_calc).pack(side='left', padx=5)
        tk.Button(btns, text="Exportar (F3)", command=self.on_export).pack(side='left', padx=5)
        tk.Button(btns, text="Volver   (F12)", command=self.volver).pack(side='left', padx=5)

        # Atajos
        self.master.bind('<F1>',  lambda e: self.on_calc())
        self.master.bind('<F3>',  lambda e: self.on_export())
        self.master.bind('<F12>', lambda e: self.volver())

        # Treeview de resultados
        cols = ('id','inicio','fin','hrs','bruto','desc','neto')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=8)
        for c, txt, w in zip(cols,
                            ('ID','Inicio','Fin','Horas','Bruto','Descuentos','Neto'),
                            (50,120,120,60,80,80,80)):
            self.tree.heading(c, text=txt)
            self.tree.column(c, width=w, anchor='center')
        self.tree.pack(padx=10, pady=10, fill='both', expand=True)

    def on_calc(self):
        ini = self.start.get_date()
        fin = self.end.get_date()
        if fin < ini:
            messagebox.showerror("Error", "La fecha fin debe ser ≥ fecha inicio")
            return
        iso_inicio = ini.isoformat() + "T00:00:00"
        iso_fin    = fin.isoformat() + "T23:59:59"
        try:
            res = calcular_nomina(1, iso_inicio, iso_fin)
            # Mostrar en tabla
            for row in self.tree.get_children():
                self.tree.delete(row)
            self.tree.insert('', 'end', values=(
                res['id'],
                res['fecha_inicio'],
                res['fecha_fin'],
                res['horas_trabajadas'],
                res['sueldo_bruto'],
                res['descuentos_total'],
                res['neto_a_pagar']
            ))
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def on_export(self):
        sel = self.tree.get_children()
        if not sel:
            return messagebox.showwarning("Atención", "Primero calcula la nómina")
        vals = self.tree.item(sel[0])['values']
        nomina_data = {
            'id': vals[0],
            'fecha_inicio': vals[1],
            'fecha_fin': vals[2],
            'horas_trabajadas': vals[3],
            'sueldo_bruto': vals[4],
            'descuentos_total': vals[5],
            'neto_a_pagar': vals[6]
        }
        from modules.pdf_util import init_pdf, add_nomina_section, output_pdf
        # Nombre de archivo con semana/año/usuario/ID
        filename = f"nomina_{self.iso_week}-{self.iso_year}_{self.usuario}_{nomina_data['id']}.pdf"
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        pdf = init_pdf(filename, logo_path)
        add_nomina_section(pdf, nomina_data, self.usuario)
        filepath = output_pdf(pdf, filename)
        messagebox.showinfo("Exportado", f"PDF generado en:\n{filepath}")

    def volver(self):
        self.master.show_menu(self.usuario, self.role)
