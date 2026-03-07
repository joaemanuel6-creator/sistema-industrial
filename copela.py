import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import requests
import json

# --- CONFIGURACIÓN ---
URL_API_GOOGLE = "https://script.google.com/macros/s/AKfycbyMjLXjtHgApvfRYaybrbyoOox6wFhh-EtY4ny3lLmUHHiGUpPpwoY0WooHDHKN6Yyo/exec"

class RegistroCopelas:
    def __init__(self, root_parent, nombre_usuario):
        self.ventana = tk.Toplevel(root_parent)
        self.ventana.title("SISTEMA INDUSTRIAL - GESTIÓN INTEGRAL")
        self.nombre_usuario = nombre_usuario
        
        self.directorio = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(self.directorio, "mi_base_de_datos.db")
        
        self.ventana.state('zoomed') 
        self.ventana.configure(bg="#1e272e")

        self.inicializar_db()
        self.crear_interfaz()
        self.verificar_permisos()
        self.cargar_datos_tabla()

    def inicializar_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS COPELA (
                N_Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                Codigo TEXT, Fecha_Registro TEXT, Operador TEXT, 
                N_Parrilla TEXT, Cantidad INTEGER, Material TEXT, 
                Prensa TEXT, Estado TEXT)""")
            conn.commit()

    def verificar_permisos(self):
        """ Habilita botones si el usuario es Rango 1 en la tabla usuarios """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("SELECT rango FROM usuarios WHERE usuario = ?", (self.nombre_usuario,))
                res = cur.fetchone()
                if res and str(res[0]) == "1":
                    self.btn_modificar.config(state="normal")
                    self.btn_eliminar.config(state="normal")
        except: pass

    def enviar_a_nube(self, payload):
        try:
            requests.post(URL_API_GOOGLE, json=payload, timeout=10)
        except: print("Error de sincronización con la nube")

    def registrar_datos(self):
        if not self.ent_mat.get() or not self.ent_uni.get(): return
        
        datos = {
            "accion": "crear",
            "codigo": self.cb_prod.get(),
            "fecha": self.ent_fec_reg.get(),
            "operador": self.nombre_usuario,
            "n_parrilla": self.cb_parr.get(),
            "cantidad": int(self.ent_uni.get()),
            "material": self.ent_mat.get().upper(),
            "prensa": self.cb_prensa.get()
        }

        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO COPELA (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) VALUES (?,?,?,?,?,?,?,?)",
                        (datos["codigo"], datos["fecha"], datos["operador"], datos["n_parrilla"], datos["cantidad"], datos["material"], datos["prensa"], "SINCRONIZADO"))
            conn.commit()
        
        self.enviar_a_nube(datos)
        self.cargar_datos_tabla()
        self.ent_mat.delete(0, tk.END); self.ent_uni.delete(0, tk.END)

    def eliminar_registro(self):
        selected = self.tabla.selection()
        if not selected: return
        
        if messagebox.askyesno("Eliminar", "¿Seguro que desea eliminar este registro en PC y Nube?"):
            val = self.tabla.item(selected)['values']
            id_db = val[0]
            
            # Borrar Local
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM COPELA WHERE N_Codigo=?", (id_db,))
                conn.commit()
            
            # Borrar Nube
            self.enviar_a_nube({"accion": "eliminar", "id_remoto": id_db})
            
            self.cargar_datos_tabla()

    def abrir_ventana_modificar(self):
        selected = self.tabla.selection()
        if not selected: return
        val = self.tabla.item(selected)['values']
        
        edit_win = tk.Toplevel(self.ventana)
        edit_win.title("Modificar Registro")
        edit_win.geometry("300x300")
        edit_win.configure(bg="#2f3640")

        tk.Label(edit_win, text="Nueva Cantidad:", fg="white", bg="#2f3640").pack(pady=5)
        ent_c = tk.Entry(edit_win); ent_c.insert(0, val[5]); ent_c.pack()
        
        tk.Label(edit_win, text="Nuevo Material:", fg="white", bg="#2c3e50").pack(pady=5)
        ent_m = tk.Entry(edit_win); ent_m.insert(0, val[6]); ent_m.pack()

        def confirmar():
            # Actualizar Local
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("UPDATE COPELA SET Cantidad=?, Material=? WHERE N_Codigo=?", (ent_c.get(), ent_m.get().upper(), val[0]))
                conn.commit()
            
            # Actualizar Nube
            self.enviar_a_nube({"accion": "modificar", "id_remoto": val[0], "cantidad": ent_c.get(), "material": ent_m.get().upper()})
            
            self.cargar_datos_tabla()
            edit_win.destroy()
            messagebox.showinfo("Listo", "Registro actualizado en todo el sistema.")

        tk.Button(edit_win, text="GUARDAR CAMBIOS", bg="#27ae60", fg="white", command=confirmar).pack(pady=20)

    def crear_interfaz(self):
        # --- ENTRADA ---
        f_top = tk.Frame(self.ventana, bg="#1e272e")
        f_top.pack(pady=20, fill="x", padx=40)
        
        self.cb_prod = ttk.Combobox(f_top, values=["Cod-7C", "Cod-8C", "Cod-9C"], width=12); self.cb_prod.set("Cod-7C")
        self.cb_prod.grid(row=0, column=0, padx=5)
        self.ent_mat = tk.Entry(f_top, width=15); self.ent_mat.grid(row=0, column=1, padx=5)
        self.ent_uni = tk.Entry(f_top, width=10); self.ent_uni.grid(row=0, column=2, padx=5)
        self.ent_fec_reg = tk.Entry(f_top, width=12); self.ent_fec_reg.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_fec_reg.grid(row=0, column=3, padx=5)
        self.cb_parr = ttk.Combobox(f_top, values=["P-01", "P-02"], width=8); self.cb_parr.set("P-01")
        self.cb_prensa = ttk.Combobox(f_top, values=["Prensa 01"], width=10); self.cb_prensa.set("Prensa 01")
        
        tk.Button(f_top, text="REGISTRAR", bg="#10ac84", fg="white", font=("Arial", 10, "bold"), command=self.registrar_datos).grid(row=0, column=4, padx=10)

        # --- TABLA ---
        self.tabla = ttk.Treeview(self.ventana, columns=("ID", "Cod", "Fec", "Op", "Par", "Cant", "Mat", "Pre", "Est"), show="headings")
        for c in self.tabla["columns"]: self.tabla.heading(c, text=c); self.tabla.column(c, width=95, anchor="center")
        self.tabla.pack(expand=True, fill="both", padx=40)

        # --- PANEL ADMIN ---
        f_bot = tk.Frame(self.ventana, bg="#1e272e")
        f_bot.pack(pady=30)
        
        self.btn_modificar = tk.Button(f_bot, text="🔧 MODIFICAR", bg="#f39c12", fg="white", width=20, state="disabled", command=self.abrir_ventana_modificar)
        self.btn_modificar.grid(row=0, column=0, padx=15)
        
        self.btn_eliminar = tk.Button(f_bot, text="🗑️ ELIMINAR", bg="#e74c3c", fg="white", width=20, state="disabled", command=self.eliminar_registro)
        self.btn_eliminar.grid(row=0, column=1, padx=15)

    def cargar_datos_tabla(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM COPELA ORDER BY N_Codigo DESC LIMIT 20")
            for r in cur.fetchall(): self.tabla.insert("", "end", values=r)

if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    app = RegistroCopelas(root, "MANUEL") 
    root.mainloop()
