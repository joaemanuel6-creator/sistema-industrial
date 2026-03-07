import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import requests

# --- PEGA AQUÍ TU NUEVA URL ---
URL_API = "https://script.google.com/macros/s/AKfycbxZJc_-CsJsCsTM-qG6vRNDdraStXWDnng73yWiS_VyH9Incwnr4tfr9Ee0n66DIqAh/exec"

class RegistroCopelas:
    def __init__(self, root, user):
        self.win = tk.Toplevel(root)
        self.win.title("SISTEMA INDUSTRIAL - REGISTRO DIRECTO")
        self.user = user
        self.db = os.path.join(os.path.dirname(__file__), "mi_base_de_datos.db")
        
        self.win.state('zoomed')
        self.win.configure(bg="#1e272e")
        
        # Pesos para que la tabla ocupe el centro
        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(1, weight=1)

        # Estilo oscuro forzado
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50", rowheight=28)
        s.heading("Treeview", background="#10ac84", foreground="white", font=("Arial", 10, "bold"))

        self.init_db()
        self.build_ui()
        self.load_table()

    def init_db(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS COPELA (id INTEGER PRIMARY KEY, cod TEXT, fec TEXT, op TEXT, cant INT, mat TEXT)")

    def guardar(self):
        c, m, q, f = self.cb_c.get(), self.e_m.get().upper(), self.e_q.get(), self.e_f.get()
        if not m or m == "MATERIAL": return

        # 1. PC (Local)
        with sqlite3.connect(self.db) as conn:
            conn.execute("INSERT INTO COPELA (cod, fec, op, cant, mat) VALUES (?,?,?,?,?)", (c, f, self.user, q, m))
        
        # 2. NUBE (Método GET - El más confiable)
        params = {"codigo": c, "fecha": f, "operador": self.user, "cantidad": q, "material": m}
        try:
            # Enviamos los datos como parámetros de URL (GET)
            requests.get(URL_API, params=params, timeout=5)
        except: pass 

        self.load_table()
        self.e_m.delete(0, tk.END); self.e_q.delete(0, tk.END)

    def build_ui(self):
        # Superior
        f1 = tk.Frame(self.win, bg="#1e272e", pady=20)
        f1.grid(row=0, column=0, sticky="ew")
        
        self.cb_c = ttk.Combobox(f1, values=["Cod-7C", "Cod-8C", "Cod-9C"], state="readonly", width=12); self.cb_c.set("Cod-7C")
        self.cb_c.grid(row=0, column=0, padx=10)
        
        self.e_m = tk.Entry(f1, bg="#2c3e50", fg="white", width=20); self.e_m.insert(0, "MATERIAL"); self.e_m.grid(row=0, column=1, padx=5)
        self.e_q = tk.Entry(f1, bg="#2c3e50", fg="white", width=8); self.e_q.insert(0, "0"); self.e_q.grid(row=0, column=2, padx=5)
        self.e_f = tk.Entry(f1, bg="#2c3e50", fg="white", width=12); self.e_f.insert(0, datetime.now().strftime("%d/%m/%Y")); self.e_f.grid(row=0, column=3, padx=5)
        
        tk.Button(f1, text="REGISTRAR", bg="#10ac84", fg="white", command=self.guardar, width=15).grid(row=0, column=4, padx=10)

        # Central (LA TABLA)
        f2 = tk.Frame(self.win, bg="#1e272e")
        f2.grid(row=1, column=0, sticky="nsew", padx=20)
        f2.columnconfigure(0, weight=1); f2.rowconfigure(0, weight=1)

        cols = ["ID", "CÓDIGO", "FECHA", "OPERADOR", "CANT", "MATERIAL"]
        self.tree = ttk.Treeview(f2, columns=cols, show="headings")
        for h in cols: self.tree.heading(h, text=h); self.tree.column(h, anchor="center")
        
        scroll = ttk.Scrollbar(f2, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

    def load_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        with sqlite3.connect(self.db) as conn:
            for r in conn.execute("SELECT * FROM COPELA ORDER BY id DESC"):
                self.tree.insert("", "end", values=r)

if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    app = RegistroCopelas(root, "MANUEL")
    root.mainloop()
