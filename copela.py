import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import requests
import json

# --- CONFIGURACIÓN DIRECTA ---
URL_API = "https://script.google.com/macros/s/AKfycbyv9E4-o66w0jkgDf7Ber0souEQ0jFTnFGIQrRVtiod7rm0YE7cdu23XHCx_0GLbYxZ/exec"

class RegistroCopelas:
    def __init__(self, root, user):
        self.win = tk.Toplevel(root)
        self.win.title("SISTEMA DE PRODUCCIÓN")
        self.user = user
        self.db = os.path.join(os.path.dirname(__file__), "mi_base_de_datos.db")
        
        self.win.state('zoomed')
        self.win.configure(bg="#1e272e")

        # Estilo Forzado
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50")
        s.configure("TCombobox", fieldbackground="#2c3e50", background="#2c3e50", foreground="white")

        self.init_db()
        self.build_ui()
        self.load_data()
        self.check_admin()

    def init_db(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS COPELA (id INTEGER PRIMARY KEY, cod TEXT, fec TEXT, op TEXT, cant INT, mat TEXT, est TEXT)")

    def check_admin(self):
        try:
            with sqlite3.connect(self.db) as conn:
                r = conn.execute("SELECT rango FROM USUARIO WHERE usuario=?", (self.user,)).fetchone()
                if r and str(r[0]) == "1":
                    self.b_mod.config(state="normal"); self.b_del.config(state="normal")
        except: pass

    def save(self):
        # Captura rápida de datos
        c, f, m, q = self.cb_p.get(), self.e_f.get(), self.e_m.get().upper(), self.e_q.get()
        if not m or not q: return

        # 1. LOCAL (Instantáneo)
        with sqlite3.connect(self.db) as conn:
            conn.execute("INSERT INTO COPELA (cod, fec, op, cant, mat, est) VALUES (?,?,?,?,?,?)", (c, f, self.user, q, m, "PENDIENTE"))
        
        # 2. NUBE (Sin restricciones de espera)
        payload = {"codigo": c, "fecha": f, "operador": self.user, "cantidad": q, "material": m}
        try:
            requests.post(URL_API, data=json.dumps(payload), headers={"Content-Type":"application/json"}, timeout=5)
            print("Enviado a la nube.")
        except:
            print("Error de red, guardado solo local.")

        self.load_data()
        self.e_m.delete(0, tk.END); self.e_q.delete(0, tk.END)

    def build_ui(self):
        # Panel Superior (Registro)
        f1 = tk.Frame(self.win, bg="#1e272e", pady=20)
        f1.pack(fill="x")
        
        self.cb_p = ttk.Combobox(f1, values=["Cod-7C", "Cod-8C", "Cod-9C"], width=12); self.cb_p.set("Cod-7C")
        self.cb_p.grid(row=0, column=0, padx=10)
        
        self.e_m = tk.Entry(f1, bg="#2c3e50", fg="white", width=20); self.e_m.insert(0, "MATERIAL"); self.e_m.grid(row=0, column=1, padx=10)
        self.e_q = tk.Entry(f1, bg="#2c3e50", fg="white", width=10); self.e_q.insert(0, "CANT"); self.e_q.grid(row=0, column=2, padx=10)
        
        self.e_f = tk.Entry(f1, bg="#2c3e50", fg="white", width=12); self.e_f.insert(0, datetime.now().strftime("%d/%m/%Y")); self.e_f.grid(row=0, column=3, padx=10)
        
        tk.Button(f1, text="GUARDAR", bg="#10ac84", fg="white", font=("Arial",10,"bold"), command=self.save, width=12).grid(row=0, column=4, padx=10)

        # Panel Central (Tabla/Listbox)
        f2 = tk.Frame(self.win, bg="#1e272e")
        f2.pack(expand=True, fill="both", padx=20)
        
        cols = ("ID", "COD", "FECHA", "OPERADOR", "CANT", "MAT", "ESTADO")
        self.tree = ttk.Treeview(f2, columns=cols, show="headings")
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, width=100, anchor="center")
        
        sc = ttk.Scrollbar(f2, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc.set)
        self.tree.pack(side="left", expand=True, fill="both")
        sc.pack(side="right", fill="y")

        # Panel Inferior (Admin)
        f3 = tk.Frame(self.win, bg="#1e272e", pady=20)
        f3.pack()
        self.b_mod = tk.Button(f3, text="MODIFICAR", bg="#f39c12", fg="white", width=15, state="disabled")
        self.b_mod.grid(row=0, column=0, padx=10)
        self.b_del = tk.Button(f3, text="ELIMINAR", bg="#e74c3c", fg="white", width=15, state="disabled")
        self.b_del.grid(row=0, column=1, padx=10)

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        with sqlite3.connect(self.db) as conn:
            for r in conn.execute("SELECT * FROM COPELA ORDER BY id DESC LIMIT 50"):
                self.tree.insert("", "end", values=r)

if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    app = RegistroCopelas(root, "MANUEL") # Cambia por el usuario real
    root.mainloop()
