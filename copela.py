import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import os
import requests
import threading # PARA QUE NO SE TRABE

# --- TU URL (Asegúrate de que termine en /exec) ---
URL_API = "https://script.google.com/macros/s/AKfycbxtfNKyg87k752UYDn9JgxZ0qVmxxZJulTKKLKIu_heg4GBDJ7e8ZqeZwgemFlilcXd/exec"

class RegistroCopelas:
    def __init__(self, root, user):
        self.win = tk.Toplevel(root)
        self.win.title("SISTEMA INDUSTRIAL - FLUJO RÁPIDO")
        self.user = user
        self.db = os.path.join(os.path.dirname(__file__), "mi_base_de_datos.db")
        
        self.win.state('zoomed')
        self.win.configure(bg="#1e272e")
        
        # Configuración de expansión total para la TABLA
        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(1, weight=1)

        self.init_db()
        self.build_ui()
        self.load_table()

    def init_db(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS COPELA (id INTEGER PRIMARY KEY, cod TEXT, fec TEXT, op TEXT, cant INT, mat TEXT)")

    def enviar_a_nube(self, params):
        """Función que corre de fondo para no trabar el programa"""
        try:
            requests.get(URL_API, params=params, timeout=10)
        except:
            pass

    def guardar(self):
        c, m, q, f = self.cb_c.get(), self.e_m.get().upper(), self.e_q.get(), self.e_f.get()
        if not m or m == "MATERIAL": return

        # 1. PC: GUARDADO INSTANTÁNEO
        with sqlite3.connect(self.db) as conn:
            conn.execute("INSERT INTO COPELA (cod, fec, op, cant, mat) VALUES (?,?,?,?,?)", (c, f, self.user, q, m))
        
        self.load_table() # Actualiza la tabla en la PC de inmediato
        
        # 2. NUBE: ENVÍO EN SEGUNDO PLANO (No detiene el programa)
        params = {"codigo": c, "fecha": f, "operador": self.user, "cantidad": q, "material": m}
        threading.Thread(target=self.enviar_a_nube, args=(params,), daemon=True).start()

        # Limpiar campos rápido
        self.e_m.delete(0, tk.END); self.e_q.delete(0, tk.END)

    def build_ui(self):
        # PANEL SUPERIOR (REGISTRO)
        f1 = tk.Frame(self.win, bg="#1e272e", pady=20)
        f1.grid(row=0, column=0, sticky="ew")
        
        self.cb_c = ttk.Combobox(f1, values=["Cod-7C", "Cod-8C", "Cod-9C"], state="readonly", width=12); self.cb_c.set("Cod-7C")
        self.cb_c.grid(row=0, column=0, padx=10)
        
        self.e_m = tk.Entry(f1, bg="#2c3e50", fg="white", font=("Arial", 12), width=20); self.e_m.insert(0, "MATERIAL"); self.e_m.grid(row=0, column=1, padx=5)
        self.e_q = tk.Entry(f1, bg="#2c3e50", fg="white", font=("Arial", 12), width=10); self.e_q.insert(0, "0"); self.e_q.grid(row=0, column=2, padx=5)
        self.e_f = tk.Entry(f1, bg="#2c3e50", fg="white", font=("Arial", 12), width=12); self.e_f.insert(0, datetime.now().strftime("%d/%m/%Y")); self.e_f.grid(row=0, column=3, padx=5)
        
        tk.Button(f1, text="REGISTRAR", bg="#10ac84", fg="white", font=("Arial", 11, "bold"), command=self.guardar, width=15).grid(row=0, column=4, padx=15)

        # PANEL CENTRAL (TABLA GIGANTE)
        f2 = tk.Frame(self.win, bg="#1e272e")
        f2.grid(row=1, column=0, sticky="nsew", padx=20)
        f2.columnconfigure(0, weight=1); f2.rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50", rowheight=30, font=("Arial", 10))
        style.heading("Treeview", background="#10ac84", foreground="white", font=("Arial", 10, "bold"))

        cols = ["ID", "CÓDIGO", "FECHA", "OPERADOR", "CANT", "MATERIAL"]
        self.tree = ttk.Treeview(f2, columns=cols, show="headings")
        for h in cols: 
            self.tree.heading(h, text=h)
            self.tree.column(h, anchor="center", width=100)
        
        scroll = ttk.Scrollbar(f2, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

    def load_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        try:
            with sqlite3.connect(self.db) as conn:
                for r in conn.execute("SELECT * FROM COPELA ORDER BY id DESC LIMIT 100"):
                    self.tree.insert("", "end", values=r)
        except: pass

if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    app = RegistroCopelas(root, "MANUEL")
    root.mainloop()
