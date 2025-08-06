# modules/login_frame.py
import tkinter as tk
from tkinter import messagebox
import bcrypt
from modules.database import get_connection


class LoginFrame(tk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="Usuario:").grid(row=0, column=0, padx=10, pady=5)
        self.user_entry = tk.Entry(self)
        self.user_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(self, text="Contraseña:").grid(row=1, column=0, padx=10, pady=5)
        self.pwd_entry = tk.Entry(self, show="*")
        self.pwd_entry.grid(row=1, column=1, padx=10, pady=5)

        btn_login = tk.Button(self, text="Ingresar", command=self.attempt_login)
        btn_login.grid(row=2, column=0, columnspan=2, pady=10)

        master = self.master
        master.bind("<F1>", lambda e: self.attempt_login())
        master.bind("<F12>", lambda e: master.destroy())

    def attempt_login(self):
        user = self.user_entry.get().strip()
        pwd = self.pwd_entry.get().encode("utf-8")
        if not user or not pwd:
            messagebox.showwarning("Error", "Completa usuario y contraseña")
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, hash_pwd, rol FROM usuarios WHERE nombre=?", (user,))
        row = c.fetchone()
        conn.close()

        if row and bcrypt.checkpw(pwd, row[1]):
            self.on_success(user, row[2])
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")