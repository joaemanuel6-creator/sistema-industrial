import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import requests

# --- PEGA TU NUEVA URL AQUÍ ---
URL_API = "https://script.google.com/macros/s/AKfycbzhZXSzhIT9JYVHnOaw7uzJvTb_lE7WjZTAqEUB2ki1LWlcoxFBKJPKtvRQb4e1u7_S/exec"

class RegistroCopelas:
    def __init__(self, root, user):
        self.win = tk.Toplevel(root)
        self.win.title("SISTEMA INDUSTRIAL - REGISTRO DIRECTO")
        self.user = user
        self.db = os.path.join(os.path.dirname(__file__), "mi_base_de_datos.db")
        
        self.win.state('zoomed')
        self.win.configure(bg="#1e272e")
        
        # Configuración de pesos para que la tabla sea visible y grande
        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(1, weight=1)

        self.init_db()
        self.build_ui()
        self.load_table()

    def init_db(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS COPELA (id INTEGER PRIMARY KEY, cod TEXT, fec TEXT, op TEXT, cant INT, mat TEXT)")

    def guardar(self):
        c, m, q, f = self.cb_c.get(), self.e_m.get().upper(), self.e_q.get(), self.e_f.get()
        if not m or m == "MATERIAL": return

        # 1. Guardar en PC (Local)
        with sqlite3.connect(self.db) as conn:
            conn.execute("INSERT INTO COPELA (cod, fec, op, cant, mat) VALUES (?,?,?,?,?)", (c, f, self.user, q, m))
        
        # 2. Enviar a Nube por parámetros de URL (Más rápido y sin JSON)
        params = {
            "codigo": c,
            "fecha": f,
            "operador": self.user,
            "cantidad": q,
            "material": m
        }
        
        try:
            # Enviamos los datos pegados a la URL
            requests.post(URL_API, params=params, timeout=5)
        except:
            pass 

        self.load_table()
        self.e_m.delete(0, tk.END)
        self.e_q.delete(0, tk.END)

    def build_ui(self):
        # Panel Superior
        f1 = tk.Frame(self.win, bg="#1e272e", pady=20)
        f1.grid(row=0, column=0, sticky="ew")
        
        self.cb_c = ttk.Combobox(f1, values=["Cod-7C", "Cod-8C", "Cod-9C"], width=12); self.cb_c.set("Cod-7C")
        self.cb_c.grid(row=0, column=0, padx=10)
        
        self.e_m = tk.Entry(f1, bg="#2c3e50", fg="white", width=20); self.e_m.insert(0, "MATERIAL"); self.e_m.grid(row=0, column=1, padx=5)
        self.e_q = tk.Entry(f1, bg="#2c3e50", fg="white", width=10); self.e_q.insert(0, "0"); self.e_q.grid(row=0, column=2, padx=5)
        self.e_f = tk.Entry(f1, bg="#2c3e50", fg="white", width=12); self.e_f.insert(0, datetime.now().strftime("%d/%m/%Y")); self.e_f.grid(row=0, column=3, padx=5)
        
        tk.Button(f1, text="REGISTRAR", bg="#10ac84", fg="white", font=("Arial", 10, "bold"), command=self.guardar, width=15).grid(row=0, column=4, padx=10)

        # Panel Central (La Tabla / Listbox)
        f2 = tk.Frame(self.win, bg="#1e272e")
        f2.grid(row=1, column=0, sticky="nsew", padx=20)
        f2.columnconfigure(0, weight=1)
        f2.rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50", rowheight=25)
        style.heading("Treeview", background="#10ac84", foreground="white")

        self.tree = ttk.Treeview(f2, columns=(1,2,3,4,5,6), show="headings")
        for i, h in enumerate(["ID", "CÓD.", "FECHA", "OPERADOR", "CANT", "MAT"], 1):
            self.tree.heading(i, text=h); self.tree.column(i, anchor="center", width=100)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Panel Inferior
        f3 = tk.Frame(self.win, bg="#1e272e", pady=20)
        f3.grid(row=2, column=0, sticky="ew")
        tk.Button(f3, text="MODIFICAR", bg="#f39c12", fg="white", width=15).grid(row=0, column=0, padx=20)
        tk.Button(f3, text="ELIMINAR", bg="#e74c3c", fg="white", width=15).grid(row=0, column=1, padx=20)

    def load_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        try:
            with sqlite3.connect(self.db) as conn:
                for r in conn.execute("SELECT * FROM COPELA ORDER BY id DESC"):
                    self.tree.insert("", "end", values=r)
        except: pass

if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    app = RegistroCopelas(root, "MANUEL")
    root.mainloop()
