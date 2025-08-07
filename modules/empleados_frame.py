import tkinter as tk
from tkinter import ttk, messagebox
from modules.empleados_dao import (
    create_empleado, get_empleados,
    update_empleado, delete_empleado
)

class EmpleadosFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role = role
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Usuario: {self.usuario}", font=(None,12,'bold')).pack(pady=5)

        form = tk.Frame(self); form.pack(pady=5, padx=10, fill='x')
        tk.Label(form, text="Nombre:").grid(row=0, column=0, sticky='e')
        self.e_nombre = tk.Entry(form);    self.e_nombre.grid(row=0, column=1, padx=5)
        tk.Label(form, text="Apellido:").grid(row=0, column=2, sticky='e')
        self.e_apellido = tk.Entry(form);  self.e_apellido.grid(row=0, column=3, padx=5)

        tk.Label(form, text="Puesto:").grid(row=1, column=0, sticky='e')
        self.e_puesto = tk.Entry(form);    self.e_puesto.grid(row=1, column=1, padx=5)
        tk.Label(form, text="Salario Semanal:").grid(row=1, column=2, sticky='e')
        self.e_salario = tk.Entry(form);   self.e_salario.grid(row=1, column=3, padx=5)

        tk.Label(form, text="Fecha Ingreso:").grid(row=2, column=0, sticky='e')
        self.e_fecha = tk.Entry(form);     self.e_fecha.grid(row=2, column=1, padx=5)

        btns = tk.Frame(self); btns.pack(pady=5)
        tk.Button(btns, text="Agregar (F1)", command=self.agregar).pack(side='left', padx=5)
        tk.Button(btns, text="Modificar (F2)", command=self.modificar).pack(side='left', padx=5)
        tk.Button(btns, text="Eliminar (F3)", command=self.eliminar).pack(side='left', padx=5)
        tk.Button(btns, text="Volver (F12)",  command=self.volver).pack(side='left', padx=5)

        cols = ('id','nombre','apellido','puesto','salario','fecha')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=8)
        for c, txt in zip(cols, ('ID','Nombre','Apellido','Puesto','Salario','Ingreso')):
            self.tree.heading(c, text=txt)
            self.tree.column(c, width=100, anchor='center')
        self.tree.pack(padx=10, pady=10, fill='both', expand=True)

        self.master.bind('<F1>',  lambda e: self.agregar())
        self.master.bind('<F2>',  lambda e: self.modificar())
        self.master.bind('<F3>',  lambda e: self.eliminar())
        self.master.bind('<F12>', lambda e: self.volver())

        self.cargar()

    def cargar(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for emp in get_empleados():
            salario_fmt = f"{emp['salario_semanal']:,.2f}"
            self.tree.insert('', 'end', values=(
                emp['id'], emp['nombre'], emp['apellido'],
                emp['puesto'], salario_fmt,
                emp['fecha_ingreso']
            ))

    def agregar(self):
        try:
            new_id = create_empleado(
                self.e_nombre.get(),
                self.e_apellido.get(),
                self.e_puesto.get(),
                float(self.e_salario.get().replace(',','')),
                self.e_fecha.get()
            )
            messagebox.showinfo("OK", f"Empleado #{new_id} agregado")
            for entry in (self.e_nombre, self.e_apellido, self.e_puesto, self.e_salario, self.e_fecha):
                entry.delete(0, tk.END)
            self.cargar()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def modificar(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Atención", "Selecciona un empleado")
        vals = self.tree.item(sel[0])['values']
        emp_id = vals[0]
        updated = update_empleado(
            emp_id,
            self.e_nombre.get() or vals[1],
            self.e_apellido.get() or vals[2],
            self.e_puesto.get() or vals[3],
            float((self.e_salario.get() or vals[4]).replace(',','')),
            self.e_fecha.get() or vals[5]
        )
        if updated:
            messagebox.showinfo("OK", "Empleado modificado")
            self.cargar()
        else:
            messagebox.showwarning("Info", "No hubo cambios")

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Atención", "Selecciona un empleado")
        emp_id = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"Eliminar empleado #{emp_id}?"):
            delete_empleado(emp_id)
            self.cargar()

    def volver(self):
        self.master.show_menu(self.usuario, self.role)
