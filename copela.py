import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import os
import requests
import threading

# --- TU URL (Cópiala con cuidado, que termine en /exec) ---
URL_API = "https://script.google.com/macros/s/AKfycbxtfNKyg87k752UYDn9JgxZ0qVmxxZJulTKKLKIu_heg4GBDJ7e8ZqeZwgemFlilcXd/exec"

class RegistroCopelas:
    def __init__(self, root, user):
        self.win = tk.Toplevel(root)
        self.win.title("CONTROL INDUSTRIAL - REGISTRO AUTOMÁTICO")
        self.user = user
        self.db = os.path.join(os.path.dirname(__file__), "mi_base_de_datos.db")
        
        self.win.state('zoomed')
        self.win.configure(bg="#1e272e")
        
        # Configuración de la rejilla para que la TABLA sea visible y grande
        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(1, weight=1)

        self.init_db()
        self.build_ui()
        self.load_table()

    def init_db(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS COPELA (id INTEGER PRIMARY KEY, cod TEXT, fec TEXT, op TEXT, cant INT, mat TEXT)")

    def enviar_datos(self, params):
        """Esta función envía el dato a Google automáticamente"""
        # Cabeceras para que Google acepte la conexión sin abrir el navegador
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            # allow_redirects=True es vital para Google Apps Script
            requests.get(URL_API, params=params, headers=headers, timeout=15, allow_redirects=True)
            print("Sincronizado con Google Sheets")
        except Exception as e:
            print(f"Error de red: {e}")

    def guardar(self):
        c, m, q, f = self.cb_c.get(), self.e_m.get().upper(), self.e_q.get(), self.e_f.get()
        if not m or m == "MATERIAL": return

        # 1. Guardar en PC (Al instante)
        with sqlite3.connect(self.db) as conn:
            conn.execute("INSERT INTO COPELA (cod, fec, op, cant, mat) VALUES (?,?,?,?,?)", (c, f, self.user, q, m))
        
        self.load_table()

        # 2. Enviar a Google Automáticamente (en segundo plano)
        params = {"codigo": c, "fecha": f, "operador": self.user, "cantidad": q, "material": m}
        threading.Thread(target=self.enviar_datos, args=(params,), daemon=True).start()

        # Limpiar entradas
        self.e_m.delete(0, tk.END); self.e_q.delete(0, tk.END)

    def build_ui(self):
        # Panel superior (Formulario)
        f1 = tk.Frame(self.win, bg="#1e272e", pady=20)
        f1.grid(row=0, column=0, sticky="ew")
        
        self.cb_c = ttk.Combobox(f1, values=["Cod-7C", "Cod-8C", "Cod-9C"], state="readonly", width=12); self.cb_c.set("Cod-7C")
        self.cb_c.grid(row=0, column=0, padx=10)
        
        self.e_m = tk.Entry(f1, bg="#2c3e50", fg="white", width=20); self.e_m.insert(0, "MATERIAL"); self.e_m.grid(row=0, column=1, padx=5)
        self.e_q = tk.Entry(f1, bg="#2c3e50", fg="white", width=10); self.e_q.insert(0, "0"); self.e_q.grid(row=0, column=2, padx=5)
        self.e_f = tk.Entry(f1, bg="#2c3e50", fg="white", width=12); self.e_f.insert(0, datetime.now().strftime("%d/%m/%Y")); self.e_f.grid(row=0, column=3, padx=5)
        
        tk.Button(f1, text="REGISTRAR", bg="#10ac84", fg="white", font=("Arial", 10, "bold"), command=self.guardar, width=15).grid(row=0, column=4, padx=10)

        # Panel central (La Tabla)
        f2 = tk.Frame(self.win, bg="#1e272e")
        f2.grid(row=1, column=0, sticky="nsew", padx=20)
        f2.columnconfigure(0, weight=1); f2.rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50", rowheight=30)
        style.heading("Treeview", background="#10ac84", foreground="white")

        self.tree = ttk.Treeview(f2, columns=(1,2,3,4,5,6), show="headings")
        for i, h in enumerate(["ID", "CÓD.", "FECHA", "OP", "CANT", "MAT"], 1):
            self.tree.heading(i, text=h); self.tree.column(i, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky="nsew")

    def load_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        with sqlite3.connect(self.db) as conn:
            for r in conn.execute("SELECT * FROM COPELA ORDER BY id DESC"):
                self.tree.insert("", "end", values=r)

if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    app = RegistroCopelas(root, "MANUEL")
    root.mainloop()
