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
    def __init__(self, root_parent, nombre_usuario):
        self.ventana = tk.Toplevel(root_parent)
        self.ventana.title("CONTROL DE PRODUCCIÓN - INDUSTRIAL")
        self.nombre_usuario = nombre_usuario
        self.db_path = os.path.join(os.path.dirname(__file__), "mi_base_de_datos.db")
        
        # Configuración de Ventana
        self.ventana.state('zoomed')
        self.ventana.configure(bg="#1e272e")
        
        # FORZAR EXPANSIÓN (Para que la tabla no desaparezca)
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.rowconfigure(1, weight=1) # La fila 1 es la tabla

        # Estilos visuales
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50", rowheight=28)
        style.heading("Treeview", background="#10ac84", foreground="white", font=("Arial", 10, "bold"))

        self.inicializar_db()
        self.crear_interfaz()
        self.cargar_datos()
        self.verificar_admin()

    def inicializar_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS COPELA (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT, fecha TEXT, operador TEXT, 
                cantidad INTEGER, material TEXT, estado TEXT)""")

    def verificar_admin(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                r = conn.execute("SELECT rango FROM USUARIO WHERE usuario=?", (self.nombre_usuario,)).fetchone()
                if r and str(r[0]) == "1":
                    self.btn_mod.config(state="normal")
                    self.btn_del.config(state="normal")
        except: pass

    def guardar(self):
        cod, mat, cant = self.cb_cod.get(), self.ent_mat.get().upper(), self.ent_cant.get()
        fec = self.ent_fec.get()

        if not mat or not cant:
            messagebox.showwarning("Aviso", "Llene los campos vacíos")
            return

        # 1. GUARDADO LOCAL (Rápido)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO COPELA (codigo, fecha, operador, cantidad, material, estado) VALUES (?,?,?,?,?,?)",
                            (cod, fec, self.nombre_usuario, cant, mat, "OK"))
            
            # 2. ENVÍO NUBE (Sin bloqueos)
            payload = {"codigo": cod, "fecha": fec, "operador": self.nombre_usuario, "cantidad": cant, "material": mat}
            requests.post(URL_API, data=json.dumps(payload), headers={"Content-Type":"application/json"}, timeout=5)
            
            self.cargar_datos()
            self.ent_mat.delete(0, tk.END)
            self.ent_cant.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")

    def crear_interfaz(self):
        # --- PANEL SUPERIOR (REGISTRO) ---
        f_top = tk.Frame(self.ventana, bg="#1e272e", pady=20)
        f_top.grid(row=0, column=0, sticky="ew")

        self.cb_cod = ttk.Combobox(f_top, values=["Cod-7C", "Cod-8C", "Cod-9C"], width=12); self.cb_cod.set("Cod-7C")
        self.cb_cod.grid(row=0, column=0, padx=10)

        self.ent_mat = tk.Entry(f_top, bg="#2c3e50", fg="white", font=("Arial", 11), width=15)
        self.ent_mat.insert(0, "MATERIAL"); self.ent_mat.grid(row=0, column=1, padx=5)

        self.ent_cant = tk.Entry(f_top, bg="#2c3e50", fg="white", font=("Arial", 11), width=8)
        self.ent_cant.insert(0, "CANT"); self.ent_cant.grid(row=0, column=2, padx=5)

        self.ent_fec = tk.Entry(f_top, bg="#2c3e50", fg="white", font=("Arial", 11), width=12)
        self.ent_fec.insert(0, datetime.now().strftime("%d/%m/%Y")); self.ent_fec.grid(row=0, column=3, padx=5)

        tk.Button(f_top, text="REGISTRAR", bg="#10ac84", fg="white", font=("Arial", 10, "bold"), command=self.guardar, width=15).grid(row=0, column=4, padx=15)

        # --- PANEL CENTRAL (TABLA / LISTBOX) ---
        # Este contenedor es el que garantiza que la tabla sea visible
        f_mid = tk.Frame(self.ventana, bg="#1e272e")
        f_mid.grid(row=1, column=0, sticky="nsew", padx=20)
        f_mid.columnconfigure(0, weight=1)
        f_mid.rowconfigure(0, weight=1)

        columnas = ("ID", "COD", "FECHA", "OPERADOR", "CANT", "MAT", "ESTADO")
        self.tabla = ttk.Treeview(f_mid, columns=columnas, show="headings")
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100, anchor="center")

        scroll = ttk.Scrollbar(f_mid, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        
        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        # --- PANEL INFERIOR (BOTONES ADMIN) ---
        f_bot = tk.Frame(self.ventana, bg="#1e272e", pady=20)
        f_bot.grid(row=2, column=0, sticky="ew")

        self.btn_mod = tk.Button(f_bot, text="MODIFICAR", bg="#f39c12", fg="white", width=20, state="disabled")
        self.btn_mod.grid(row=0, column=0, padx=20)

        self.btn_del = tk.Button(f_bot, text="ELIMINAR", bg="#e74c3c", fg="white", width=20, state="disabled")
        self.btn_del.grid(row=0, column=1, padx=20)

    def cargar_datos(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM COPELA ORDER BY id DESC")
            for r in cursor.fetchall():
                self.tabla.insert("", "end", values=r)

if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    # Recuerda: El usuario "MANUEL" debe tener rango 1 en la tabla USUARIO para activar botones
    app = RegistroCopelas(root, "MANUEL")
    root.mainloop()
