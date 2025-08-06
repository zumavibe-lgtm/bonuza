import tkinter as tk
from tkinter import messagebox
import sqlite3
from modules.database import get_connection

def ahora_iso():
    """Devuelve timestamp ISO 8601 en UTC"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

class ChecadorFrame(tk.Frame):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text=f"Empleado: {self.usuario}", font=(None, 14)).pack(pady=5)
        # Botones
        btn_ent = tk.Button(self, text="Llegada", command=self.registrar_entrada)
        btn_ent.pack(side=tk.LEFT, padx=20, pady=10)
        btn_sal = tk.Button(self, text="Salida", command=self.registrar_salida)
        btn_sal.pack(side=tk.LEFT, padx=20, pady=10)
        # Treeview para registros
        from tkinter.ttk import Treeview
        cols = ("Entrada", "Salida")
        self.tree = Treeview(self, columns=cols, show="headings")
        self.tree.heading("Entrada", text="Entrada UTC")
        self.tree.heading("Salida", text="Salida UTC")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Atajos de teclado
        self.master.bind("<F1>", lambda e: self.registrar_entrada())
        self.master.bind("<F12>", lambda e: self.logout())

        self.cargar_registros()

    def registrar_entrada(self):
        conn = get_connection()
        c = conn.cursor()
        # Obtiene id de usuario
        c.execute("SELECT id FROM usuarios WHERE nombre=?", (self.usuario,))
        row = c.fetchone()
        if not row:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        uid = row[0]
        c.execute(
            "INSERT INTO asistencia (usuario_id, ts_entrada) VALUES (?,?)",
            (uid, ahora_iso())
        )
        conn.commit()
        conn.close()
        self.cargar_registros()

    def registrar_salida(self):
        conn = get_connection()
        c = conn.cursor()
        # Busca la última fila sin ts_salida
        c.execute(
            "SELECT id FROM asistencia WHERE usuario_id=(SELECT id FROM usuarios WHERE nombre=?) AND ts_salida IS NULL ORDER BY ts_entrada DESC LIMIT 1",
            (self.usuario,)
        )
        row = c.fetchone()
        if not row:
            messagebox.showwarning("Atención", "No hay registro de entrada pendiente")
            return
        rec_id = row[0]
        c.execute(
            "UPDATE asistencia SET ts_salida=? WHERE id=?",
            (ahora_iso(), rec_id)
        )
        conn.commit()
        conn.close()
        self.cargar_registros()

    def cargar_registros(self):
        # Limpia Treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Carga últimas 10 filas
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT ts_entrada, COALESCE(ts_salida,'-') FROM asistencia WHERE usuario_id=(SELECT id FROM usuarios WHERE nombre=?) ORDER BY ts_entrada DESC LIMIT 10",
            (self.usuario,)
        )
        for ent, sal in c.fetchall():
            self.tree.insert('', 'end', values=(ent, sal))
        conn.close()

    def logout(self):
        # Vuelve al login
        from modules.login_frame import LoginFrame
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.title("BONUZA - Login")
        LoginFrame(self.master, on_success=self.master.show_chekador).pack(padx=50, pady=50)