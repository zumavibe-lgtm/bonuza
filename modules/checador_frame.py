import tkinter as tk
from tkinter import messagebox
from modules.database import get_connection

def ahora_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

class ChecadorFrame(tk.Frame):
    def __init__(self, master, usuario, role):
        super().__init__(master)
        self.usuario = usuario
        self.role = role
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Empleado: {self.usuario}", font=(None,14)).pack(pady=5)

        btns = tk.Frame(self); btns.pack(pady=5)
        tk.Button(btns, text="Llegada (F1)", command=self.registrar_entrada).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Salida (F2)",   command=self.registrar_salida).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Volver (F12)",  command=self.volver).pack(side=tk.LEFT, padx=5)

        from tkinter.ttk import Treeview
        self.tree = Treeview(self, columns=("Entrada","Salida"), show="headings")
        self.tree.heading("Entrada", text="Entrada UTC")
        self.tree.heading("Salida",  text="Salida UTC")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.master.bind("<F1>",  lambda e: self.registrar_entrada())
        self.master.bind("<F2>",  lambda e: self.registrar_salida())
        self.master.bind("<F12>", lambda e: self.volver())

        self.cargar_registros()

    def registrar_entrada(self):
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT id FROM usuarios WHERE nombre=?", (self.usuario,))
        row = c.fetchone()
        if not row:
            messagebox.showerror("Error","Usuario no encontrado"); return
        uid = row[0]
        c.execute("INSERT INTO asistencia(usuario_id,ts_entrada) VALUES (?,?)",(uid, ahora_iso()))
        conn.commit(); conn.close()
        self.cargar_registros()

    def registrar_salida(self):
        conn = get_connection(); c = conn.cursor()
        c.execute("""
            SELECT id FROM asistencia
            WHERE usuario_id=(SELECT id FROM usuarios WHERE nombre=?)
              AND ts_salida IS NULL
            ORDER BY ts_entrada DESC LIMIT 1
        """,(self.usuario,))
        row = c.fetchone()
        if not row:
            messagebox.showwarning("Atención","No hay registro de entrada pendiente"); conn.close(); return
        rec_id = row[0]
        c.execute("UPDATE asistencia SET ts_salida=? WHERE id=?",(ahora_iso(), rec_id))
        conn.commit(); conn.close()
        self.cargar_registros()

    def cargar_registros(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_connection(); c = conn.cursor()
        c.execute("""
            SELECT ts_entrada, COALESCE(ts_salida,'-')
            FROM asistencia
            WHERE usuario_id=(SELECT id FROM usuarios WHERE nombre=?)
            ORDER BY ts_entrada DESC LIMIT 10
        """, (self.usuario,))
        for ent, sal in c.fetchall():
            self.tree.insert('', 'end', values=(ent, sal))
        conn.close()

    def volver(self):
        self.master.show_menu(self.usuario, self.role)
