# modules/ptu_frame.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from modules.ptu_dao import (
    create_table_ptu_config, get_ptu_config,
    set_ptu_config, calculate_ptu
)

class PtuFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role    = role
        create_table_ptu_config()
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Reparto de Utilidades (PTU) — Usuario: {self.usuario}",
                 font=(None,14,'bold')).pack(pady=10)

        # Configuración PTU
        cfg = get_ptu_config()
        frm_cfg = tk.Frame(self); frm_cfg.pack(pady=5)
        tk.Label(frm_cfg, text="Monto total:").grid(row=0, column=0, sticky='e')
        self.e_monto = tk.Entry(frm_cfg, width=10); self.e_monto.grid(row=0, column=1, padx=5)
        self.e_monto.insert(0, str(cfg['monto_total']))
        tk.Label(frm_cfg, text="Pct (%):").grid(row=0, column=2, sticky='e')
        self.e_pct = tk.Entry(frm_cfg, width=5); self.e_pct.grid(row=0, column=3, padx=5)
        self.e_pct.insert(0, str(cfg['porcentaje']))
        tk.Label(frm_cfg, text="Días mínimos:").grid(row=0, column=4, sticky='e')
        self.e_min = tk.Entry(frm_cfg, width=5); self.e_min.grid(row=0, column=5, padx=5)

        # Fecha de corte
        frm_sel = tk.Frame(self); frm_sel.pack(pady=10)
        tk.Label(frm_sel, text="Hasta fecha:").pack(side='left')
        self.dt_hasta = DateEntry(frm_sel); self.dt_hasta.pack(side='left', padx=5)

        # Botones
        btns = tk.Frame(self); btns.pack(pady=10)
        tk.Button(btns, text="Guardar Config (F1)", command=self.on_save).pack(side='left', padx=5)
        tk.Button(btns, text="Calcular PTU  (F2)", command=self.on_calc).pack(side='left', padx=5)
        tk.Button(btns, text="Volver       (F12)", command=self.volver).pack(side='left', padx=5)

        self.master.bind('<F1>', lambda e: self.on_save())
        self.master.bind('<F2>', lambda e: self.on_calc())
        self.master.bind('<F12>', lambda e: self.volver())

        # Tabla de resultados
        cols = ('empleado','dias','salario','ptu')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=8)
        headers = ['Empleado','Días','Salario Anual','PTU']
        for c,h,w in zip(cols, headers, (200,60,100,100)):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor='center')
        self.tree.pack(padx=10, pady=10, fill='both', expand=True)

    def on_save(self):
        try:
            monto = float(self.e_monto.get())
            pct   = float(self.e_pct.get())
            dias  = int(self.e_min.get())
            set_ptu_config(monto, pct, dias)
            messagebox.showinfo("OK", "Configuración PTU guardada")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def on_calc(self):
        hasta = self.dt_hasta.get_date().isoformat()
        try:
            rows = calculate_ptu(hasta)
            for i in self.tree.get_children():
                self.tree.delete(i)
            for r in rows:
                self.tree.insert('', 'end', values=(
                    r['empleado'], r['dias_trabajados'],
                    r['salario_anual'], r['ptu_individual']
                ))
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def volver(self):
        self.master.show_menu(self.usuario, self.role)
