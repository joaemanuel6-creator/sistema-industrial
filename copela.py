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
        self.ventana.title("SISTEMA INDUSTRIAL - COPELAS")
        self.nombre_usuario = nombre_usuario
        
        self.directorio = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(self.directorio, "mi_base_de_datos.db")
        
        self.ventana.state('zoomed') 
        self.ventana.configure(bg="#1e272e")

        # Configuración de ESTILOS para evitar que se ponga blanco
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam') # 'clam' permite cambiar colores de Combobox mejor
        self.estilo.configure("TCombobox", fieldbackground="#2c3e50", background="#2c3e50", foreground="white")
        self.estilo.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50", rowheight=25)
        self.estilo.map("Treeview", background=[('selected', '#10ac84')])

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
        """ Verifica en la tabla USUARIO si el rango es 1 """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("SELECT rango FROM USUARIO WHERE usuario = ?", (self.nombre_usuario,))
                res = cur.fetchone()
                if res and (str(res[0]) == "1"):
                    self.btn_modificar.config(state="normal")
                    self.btn_eliminar.config(state="normal")
        except: pass

    def enviar_a_nube(self, payload):
        """ Envío forzado a la nube """
        try:
            # Importante: enviamos 'json=payload' para que Requests maneje el encabezado automáticamente
            response = requests.post(URL_API_GOOGLE, json=payload, timeout=10)
            print(f"Respuesta Nube: {response.text}")
            return True
        except Exception as e:
            print(f"Error Nube: {e}")
            return False

    def registrar_datos(self):
        if not self.ent_mat.get() or self.ent_mat.get() == "MATERIAL":
            messagebox.showwarning("Atención", "Ingrese el material")
            return
        
        try:
            cant = int(self.ent_uni.get())
            datos = {
                "accion": "crear",
                "codigo": self.cb_prod.get(),
                "fecha": self.ent_fec_reg.get(),
                "operador": self.nombre_usuario,
                "n_parrilla": "P-01",
                "cantidad": cant,
                "material": self.ent_mat.get().upper(),
                "prensa": "PRENSA-1"
            }

            # Guardar Local
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO COPELA (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) 
                            VALUES (?,?,?,?,?,?,?,?)""",
                            (datos["codigo"], datos["fecha"], datos["operador"], datos["n_parrilla"], 
                             datos["cantidad"], datos["material"], datos["prensa"], "ENVIANDO..."))
                conn.commit()
            
            # Guardar Nube
            if self.enviar_a_nube(datos):
                messagebox.showinfo("Éxito", "Registrado en PC y Nube")
            else:
                messagebox.showwarning("Aviso", "Guardado localmente, pero falló la Nube")

            self.cargar_datos_tabla()
            self.ent_mat.delete(0, tk.END)
            self.ent_uni.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser número")

    def crear_interfaz(self):
        # TÍTULO
        tk.Label(self.ventana, text="PANEL DE COPELAS", font=("Arial", 18, "bold"), fg="cyan", bg="#1e272e").pack(pady=10)

        # PANEL ENTRADA
        f_in = tk.Frame(self.ventana, bg="#1e272e")
        f_in.pack(pady=10, fill="x", padx=20)

        self.cb_prod = ttk.Combobox(f_in, values=["Cod-7C", "Cod-8C", "Cod-9C"], state="readonly", width=15)
        self.cb_prod.set("Cod-7C")
        self.cb_prod.grid(row=0, column=0, padx=5)

        self.ent_mat = tk.Entry(f_in, bg="#2c3e50", fg="white", insertbackground="white", width=20)
        self.ent_mat.insert(0, "MATERIAL")
        self.ent_mat.grid(row=0, column=1, padx=5)

        self.ent_uni = tk.Entry(f_in, bg="#2c3e50", fg="white", insertbackground="white", width=10)
        self.ent_uni.insert(0, "0")
        self.ent_uni.grid(row=0, column=2, padx=5)

        self.ent_fec_reg = tk.Entry(f_in, bg="#2c3e50", fg="white", width=15)
        self.ent_fec_reg.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_fec_reg.grid(row=0, column=3, padx=5)

        tk.Button(f_in, text="GUARDAR", bg="#10ac84", fg="white", font=("Arial", 10, "bold"), command=self.registrar_datos).grid(row=0, column=4, padx=10)

        # PANEL TABLA (Tu "Listbox" mejorado)
        f_tabla = tk.Frame(self.ventana, bg="#1e272e")
        f_tabla.pack(expand=True, fill="both", padx=20, pady=10)

        columnas = ("ID", "COD", "FECHA", "OPERADOR", "PARR", "CANT", "MAT", "PREN", "ESTADO")
        self.tabla = ttk.Treeview(f_tabla, columns=columnas, show="headings", height=15)
        
        # Scrollbars para que se vea siempre
        sy = ttk.Scrollbar(f_tabla, orient="vertical", command=self.tabla.yview)
        sx = ttk.Scrollbar(f_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=80, anchor="center")

        self.tabla.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        f_tabla.grid_columnconfigure(0, weight=1)
        f_tabla.grid_rowconfigure(0, weight=1)

        # PANEL BOTONES ABAJO
        f_btn = tk.Frame(self.ventana, bg="#1e272e")
        f_btn.pack(pady=10)

        self.btn_modificar = tk.Button(f_btn, text="MODIFICAR", bg="#f39c12", fg="white", width=15, state="disabled")
        self.btn_modificar.grid(row=0, column=0, padx=10)

        self.btn_eliminar = tk.Button(f_btn, text="ELIMINAR", bg="#e74c3c", fg="white", width=15, state="disabled")
        self.btn_eliminar.grid(row=0, column=1, padx=10)

    def cargar_datos_tabla(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM COPELA ORDER BY N_Codigo DESC")
                for fila in cur.fetchall():
                    self.tabla.insert("", "end", values=fila)
        except: pass

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    # Recuerda que el usuario "MANUEL" debe estar en la tabla USUARIO con rango 1
    app = RegistroCopelas(root, "MANUEL") 
    root.mainloop()
